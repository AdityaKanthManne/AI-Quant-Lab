# AI Portfolio Management and Decision Engine

A research and simulation platform for testing whether prediction-market probabilities and
time-stamped AI research signals improve risk-adjusted portfolio allocation. It is explicitly
**not a live-money trading bot**.

## Current milestone

This baseline establishes the contracts that advanced models must beat:

- point-in-time market-data validation with Polars and DuckDB;
- historical-mean and momentum-blend return forecasts;
- sample covariance volatility/correlation forecast;
- equal-weight, inverse-volatility, minimum-variance, mean-variance, and maximum-Sharpe methods;
- configurable probability-weighted event scenarios;
- walk-forward backtesting with transaction costs;
- volatility, Sharpe, Sortino, drawdown, VaR, CVaR, beta, turnover, and concentration;
- MLflow run helper, FastAPI research API, Docker stack, and pytest coverage.

HMM, boosted trees, ARIMA, PyTorch sequence models, CVaR optimization, risk parity, Kelly
sizing, macro vintages, AI ingestion, and reinforcement learning are planned milestones—not
unearned complexity hidden in the baseline.

## Architecture

```text
point-in-time sources
        |
        v
Polars validation --> DuckDB research store
        |
        v
features --> return + covariance + regime forecasts
        |                     |
        +--> event scenarios -+
                              v
                    constrained optimizer
                              |
                              v
                walk-forward backtest + costs
                              |
                              v
                 risk report + MLflow evidence
```

PostgreSQL stores API/application metadata; DuckDB remains the local analytical store. Raw data
is immutable, processed datasets are versioned, and every derived row carries an
`available_at` timestamp.

## Quantitative methodology

For asset return vector \(r_t\), the historical baseline estimates

\[
\hat{\mu}=252\,\bar r, \qquad \hat{\Sigma}=252\,\mathrm{Cov}(r).
\]

Minimum variance solves

\[
\min_w w^\top\hat{\Sigma}w
\quad\text{s.t.}\quad \mathbf{1}^\top w=1,\;0\le w_i\le u_i.
\]

Maximum Sharpe maximizes

\[
\frac{w^\top\hat{\mu}-r_f}{\sqrt{w^\top\hat{\Sigma}w}}.
\]

For scenario \(s\), event probability \(p_s\), and configurable asset shock \(\delta_s\), the
initial mixture adjusts expected return as

\[
\hat{\mu}_{scenario}=\hat{\mu}+\sum_s p_s\delta_s.
\]

The shock is a versioned research assumption and never a hard-coded economic claim.

## Anti-leakage methodology

- Training windows end before the first return earned by a new allocation.
- Market, macro, news, and event data are filtered by `available_at`.
- Macro observations will retain both release vintage and later revisions.
- Feature normalization and hyperparameter tuning must be fit inside each training fold.
- Alternative-information experiments compare identical dates and portfolio constraints.
- Universe membership will be point-in-time where a historical constituent dataset permits it.

## Benchmarks and statistical comparisons

Every completed experiment will compare against SPY, equal weight, and (where the universe
supports it) a 60/40 stock/bond portfolio. In addition to cumulative return, reports will include
paired return differences, confidence intervals, bootstrap tests, drawdown comparisons, turnover,
and sensitivity to transaction costs.

## Data sources

Source adapters are intentionally not selected in the base outline. Before implementation, each
source must document licensing, adjustment methodology, timestamps, revision policy, symbol
mapping, and delisting coverage. Synthetic data is used by the demo so the repository is fully
reproducible without credentials.

## Reproduce the baseline

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
portfolio-demo
uvicorn ai_portfolio.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for the research API. Or run the full local services with:

```bash
docker compose up --build
```

## Experiment contract

An MLflow run must record model name and parameters, dataset identity and date range, feature
version, portfolio method, constraints, costs, benchmark, random seed, code revision, and all
performance metrics. The primary ablation is:

1. quantitative baseline;
2. baseline plus prediction-market features;
3. baseline plus AI research features;
4. baseline plus both alternative sources.

## Limitations

The scaffold uses sample covariance, synthetic demonstrations, Gaussian historical VaR, and
long-only baseline optimization. It does not yet model liquidity, taxes, borrow costs, market
impact, delistings, macro vintage databases, execution latency, or uncertainty in scenario shock
estimates. Backtest success is research evidence—not evidence of future profitability.

## Learning map

The guided curriculum, prerequisite graph, research milestones, backtesting protocol, and
interview outcomes are in [`docs/LEARNING_PATH.md`](docs/LEARNING_PATH.md). Begin the hands-on
sequence with [`docs/MODULE_01_RETURNS.md`](docs/MODULE_01_RETURNS.md); it includes manual
calculations, NumPy exercises, edge cases, and answer checks.

Read the implementation in this order:

1. `domain.py` defines the research vocabulary and timestamp contract.
2. `data.py` prevents unavailable observations from entering a decision.
3. `models.py` produces expected return and covariance forecasts.
4. `optimization.py` converts forecasts into weights.
5. `backtest.py` ensures those weights earn only future returns and charges costs.
6. `risk.py` evaluates whether the result was worth taking.
