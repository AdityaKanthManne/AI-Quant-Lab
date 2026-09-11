# Agent-Based Prediction Market Simulator

A configuration-driven computational economics platform for studying price discovery,
liquidity, information diffusion, heterogeneous beliefs, and AI-agent behavior in a
binary-contract continuous double auction.

## Current milestone

This first milestone establishes the deterministic research kernel:

- integer-tick binary contracts, avoiding floating-point price ambiguity;
- price-time-priority limit-order matching;
- immutable order requests, trades, and book snapshots;
- modular agent interface with seeded local random-number generators;
- reference noise and informed traders;
- a deterministic event-loop skeleton;
- pure Brier-score and information-incorporation metrics;
- explicit extension boundaries for LLM agents, Gymnasium, FastAPI, persistence, and Ray.

Accounting, collateral reservation, settlement, information delivery, complete agent
families, experiment runners, plotting, RL, database persistence, and Docker are deliberate
next milestones. The simulator should not be used for research conclusions before those
invariants and validation tests are implemented.

## Market mechanics

A YES contract settles to 1 if an event occurs and 0 otherwise. Prices are represented as
integer ticks: at the default scale, `6500` means `0.6500`. Incoming orders match the best
opposite price, and orders at one price execute in arrival order. Trades execute at the
resting order's price, making the resting order the maker and the incoming order the taker.

## Design assumptions

1. Simulation time is discrete, although multiple events may occur at each timestamp.
2. Strategy code produces order intentions; only the exchange changes order-book state.
3. Every stochastic component receives an explicit seed.
4. Hidden latent probability is owned by the world process, never by agent observations.
5. Metrics are observational and must not affect simulation state.

## Architecture

```text
configuration -> world/information -> agents -> exchange -> ledger
                         ^                        |
                         +---- observations -----+
                                      |
                               metrics/results
```

The `src/market_sim` package is organized by responsibility:

- `core/`: messages and the simulation clock;
- `market/`: matching and, next, accounting/settlement;
- `agents/`: strategy-independent state and modular policies;
- `metrics/`: side-effect-free research estimators;
- `llm/`: evidence-only forecasting protocol;
- `rl/`: Gymnasium adapter around the same exchange;
- `api/`: optional experiment-control service.

## Mathematical formulation

For binary payoff `Y in {0, 1}`, a risk-neutral belief `q` gives expected contract value
`E[Y] = q`. Forecast quality is measured by the Brier score

```text
BS = (1 / N) * sum((p_i - y_i)^2).
```

Market quality requires more than forecast accuracy. Planned measurements include quoted
and effective spread, depth, order imbalance, realized volatility, slippage, volume,
wealth concentration, strategy survival, and time required to incorporate information.

## Setup and tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

Optional stacks are installed independently with `.[api]`, `.[rl]`, `.[plot]`, and
`.[scale]`, keeping the research kernel lightweight.

## Experiment roadmap

1. Entry of informed traders and convergence speed.
2. Liquidity versus prediction accuracy.
3. AI exploitation of noisy or miscalibrated traders.
4. Ensemble LLM participation and price discovery.
5. Correlated LLM beliefs, crowded positioning, and endogenous systemic behavior.

Experiment 5 will vary both forecast-error correlation and policy correlation. This is
important because agents can share beliefs without trading identically, or trade alike even
when their point forecasts differ.

## Reproducibility

Configurations live in `configs/`; generated tables and figures go under
`experiments/results/`. Each run will record the resolved configuration, root seed, package
versions, source revision, agent seeds, and result schema version.

## Limitations of the outline

The present code demonstrates boundaries and matching semantics, not a validated economic
model. It does not yet reserve collateral, update cash and inventory, model latency, charge
fees, handle self-trading, or define multi-contract arbitrage. Those are the next correctness
layer because agent-profitability results are meaningless until accounting invariants hold.

