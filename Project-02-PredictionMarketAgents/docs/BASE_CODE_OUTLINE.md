# Base Code Outline

This document is the implementation map for the first production-capable version of the forecasting platform. It separates research contracts from data vendors, model implementations, orchestration, persistence, and presentation.

## 1. End-to-end execution path

```text
POST /v1/forecasts
    ↓
ForecastQuestion validation
    ↓
LangGraph starts two retrieval branches
    ├── MarketConnector.snapshot()
    └── EvidenceConnector.retrieve()
    ↓
Normalize and rank evidence
    ↓
Run independent forecasting agents
    ├── Historical/base-rate forecast
    ├── Macro forecast
    ├── News/event forecast
    └── Statistical forecast
    ↓
Skeptic reviews correlation and overconfidence
    ↓
ForecastAggregator pools probabilities in log-odds space
    ↓
ForecastResult validation and permanent storage
    ↓
Return model probability, market probability, edge, interval,
evidence, agent disagreement, and methodology
```

After resolution, `POST /v1/resolutions` records the binary outcome. The metrics and experiment endpoints then join forecasts to outcomes and calculate proper scores.

## 2. Domain layer

File: `src/prediction_market_agents/domain.py`

The domain models are the stable language shared by every subsystem:

```python
class ForecastQuestion(BaseModel):
    event_id: UUID
    question: str
    category: Category
    resolution_time: datetime | None
    resolution_criteria: str | None
    market: str | None
    market_event_id: str | None
    features: dict[str, float]


class Evidence(BaseModel):
    source: str
    title: str
    published_at: datetime | None
    summary: str
    relevance: float
    credibility: float
    direction: Direction
    likelihood_ratio: float


class AgentForecast(BaseModel):
    agent: str
    probability: float
    confidence: float
    rationale: str
    weight: float


class ForecastResult(BaseModel):
    market_probability: float | None
    model_probability: float
    edge: float | None
    interval_low: float
    interval_high: float
    prior_probability: float
    evidence: list[Evidence]
    agent_forecasts: list[AgentForecast]
    disagreement: float
    model_version: str
```

Pydantic rejects invalid probabilities and inconsistent intervals before bad research data reaches storage.

## 3. Connector layer

Files: `src/prediction_market_agents/connectors/`

Connectors translate changing external APIs into stable domain objects.

```python
class MarketConnector(ABC):
    name: str

    @abstractmethod
    async def snapshot(self, event_id: str) -> MarketSnapshot:
        ...


class EvidenceConnector(ABC):
    name: str

    @abstractmethod
    async def retrieve(
        self,
        question: ForecastQuestion,
        limit: int = 10,
    ) -> list[Evidence]:
        ...
```

To add Kalshi, implement `MarketConnector`. To add BLS, BEA, EDGAR, GDELT, or polling data, implement `EvidenceConnector`. Vendor response models should remain inside the connector and never leak into agent code.

## 4. Forecast-agent layer

File: `src/prediction_market_agents/agents/forecasting.py`

Every forecasting agent must return a probability rather than a generic answer:

```python
class NewForecastAgent:
    name = "new_agent"

    def forecast(
        self,
        question: ForecastQuestion,
        evidence: list[Evidence],
        prior: float,
    ) -> AgentForecast:
        probability = ...
        return AgentForecast(
            agent=self.name,
            probability=probability,
            confidence=...,
            rationale=...,
            evidence_ids=[...],
            weight=...,
            metadata={...},
        )
```

Agent roles in the base implementation:

- `HistoricalAgent`: establishes a reference-class prior.
- `MacroAgent`: applies economic evidence as reliability-weighted likelihood updates.
- `NewsAgent`: converts directional event evidence into Bayesian updates.
- `StatisticalAgent`: supplies a reproducible non-LLM baseline.
- `SkepticAgent`: shrinks correlated or overly extreme consensus.
- `ForecastAggregator`: performs confidence-weighted logarithmic opinion pooling.

The agents are intentionally independent at forecast time. One agent should not see another agent's probability until the critic and aggregation stages.

## 5. Probability layer

File: `src/prediction_market_agents/math.py`

The core update is:

```python
posterior = sigmoid(logit(prior) + sum(log(lr) for lr in likelihood_ratios))
```

The aggregation rule is:

```python
combined = sigmoid(
    sum(weight * logit(probability) for probability, weight in forecasts)
    / sum(weights)
)
```

Log-odds make evidence multiplication numerically stable. Probability clipping prevents `log(0)` without silently allowing values outside `[0, 1]`.

## 6. Orchestration layer

File: `src/prediction_market_agents/orchestration.py`

LangGraph state contains only serializable research artifacts:

```python
class ForecastState(TypedDict, total=False):
    question: ForecastQuestion
    market_snapshot: MarketSnapshot | None
    evidence: list[Evidence]
    agent_forecasts: list[AgentForecast]
    model_probability: float
    interval_low: float
    interval_high: float
    disagreement: float
```

The graph shape is:

```text
START ─┬─ market retrieval ─┐
       └─ evidence retrieval ┴─ agents ─ critic/aggregate ─ END
```

Production additions belong here: retry policies, timeouts, checkpoints, parallel agent nodes, human review for ambiguous resolution criteria, and tracing.

## 7. Service and API layers

Files:

- `src/prediction_market_agents/service.py`
- `src/prediction_market_agents/api.py`

`ForecastService` is the application boundary. It invokes the graph, constructs the immutable result, calculates descriptive edge, and persists the forecast. FastAPI is a thin transport layer and should not contain forecasting logic.

Base endpoints:

```text
POST /v1/forecasts
GET  /v1/forecasts/{forecast_id}
GET  /v1/events/{event_id}/history
POST /v1/resolutions
GET  /v1/metrics?source=model|market
GET  /v1/experiments/leaderboard
GET  /health
```

## 8. Persistence and analytics

Files:

- `src/prediction_market_agents/storage.py`
- `src/prediction_market_agents/analytics.py`

PostgreSQL is the transactional source of truth. Each forecast stores both searchable columns and the complete validated JSON payload. Resolutions are separate records so outcomes cannot accidentally alter historical forecasts.

DuckDB is the analytical layer for rolling and batch evaluation. Polars prepares columnar data. This split prevents dashboard queries from interfering with forecast writes.

Future tables should include:

```text
events
market_snapshots
evidence_items
evidence_claims
forecast_runs
agent_forecasts
final_forecasts
resolutions
experiment_assignments
model_versions
```

## 9. Statistical baseline

File: `src/prediction_market_agents/statistical.py`

The initial model is scaled logistic regression followed by sigmoid calibration. Its purpose is to provide a transparent, non-LLM benchmark—not to claim that one algorithm works for every event category.

Training must use time-ordered data:

```text
train on events resolved before T
validate on the next time block
freeze preprocessing and model
forecast the later test block
repeat with an expanding or rolling window
```

Gradient boosting, Bayesian hierarchical models, and PyTorch models can implement the same `fit` and `predict_probability` boundary later.

## 10. Evaluation and experiments

Files:

- `src/prediction_market_agents/evaluation.py`
- `src/prediction_market_agents/experiments.py`

Required experiment arms:

```python
class Arm(StrEnum):
    MARKET = "market_alone"
    LLM = "llm_alone"
    STATISTICAL = "statistical_alone"
    MULTI_AGENT = "multi_agent"
    MARKET_AI = "market_plus_ai"
```

Every arm must use the same events and information cutoff. Compare paired Brier score and log loss, then report calibration, sharpness, resolution, category slices, forecast-horizon slices, and bootstrap uncertainty.

## 11. Implementation order

The safest development sequence is:

1. Lock event and forecast schemas.
2. Add authoritative connector fixtures and contract tests.
3. Store point-in-time market snapshots and raw evidence.
4. Improve historical priors and statistical features by category.
5. Add structured-output LLM adapters with frozen prompts.
6. Add provenance-aware claim deduplication.
7. Add proper database migrations and background collection jobs.
8. Run a preregistered paper-quality experiment.
9. Add dashboard views only after metric semantics are stable.

## 12. Definition of done for a forecast

A forecast is research-valid only when it has:

- an unambiguous event definition and authoritative resolution source;
- a timestamp and information cutoff;
- a contemporaneous market probability when a market exists;
- a prior and independently recorded agent probabilities;
- source-linked evidence available at the cutoff;
- a frozen model and prompt version;
- a final probability and uncertainty interval;
- an eventual binary resolution or an explicit invalid/ambiguous status;
- reproducible scoring without editing the original forecast.

