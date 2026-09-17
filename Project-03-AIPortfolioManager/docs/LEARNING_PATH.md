# AI Portfolio Management and Decision Engine — Learning Path

This project asks a research question: **can point-in-time prediction-market information and
AI-derived event signals improve risk-adjusted portfolio allocation?** It does not assume that
they can, and it is not a live-money trading system.

## Learning contract

Every quantitative topic follows the same sequence:

1. Theory and assumptions
2. Mathematics and notation
3. A calculation by hand
4. A NumPy implementation
5. Integration into the research system
6. A point-in-time backtest against a simpler baseline
7. Review, failure analysis, and explanation in plain English

Advanced models earn their place only by beating appropriate baselines out of sample after
costs. A more complicated model that does not do so is rejected.

## Mathematical prerequisite map

```text
prices -> arithmetic/log returns -> compounding
                    |
                    v
        mean, variance, sampling
                    |
                    v
 vectors + matrices -> covariance/correlation
                    |              |
                    +------v-------+
                           |
              portfolio return and variance
                           |
          constrained optimization + MPT
                           |
             Sharpe / Sortino / VaR / CVaR

probability -> conditional probability -> scenarios
     |                    |                    |
     +-----------> sampling distributions     |
                          |                    |
                     inference <--------------+

time ordering -> lags -> stationarity/autocorrelation
      |                              |
      +-> walk-forward validation <-+
                     |
          forecasting and regime models
```

Minimum prerequisites, in dependency order:

- Algebra: percentages, exponents, logarithms, summation notation.
- Linear algebra: vectors, dot products, matrices, transpose, quadratic forms.
- Statistics: samples, location, dispersion, covariance, correlation, distributions.
- Probability: conditional probability, expectation, weighted scenarios, simulation.
- Optimization: objective, decision variable, constraint, convexity, Lagrange intuition.
- Time series: chronological dependence, stationarity, lags, autocorrelation.
- Programming: Python functions, arrays, shapes, indexing, tests, reproducible randomness.

Calculus is useful for optimization intuition but is not a gate for the early milestones.

## Research architecture

```text
Point-in-time sources
  market | macro vintages | prediction markets | timestamped AI research
                              |
                              v
Immutable raw data -> validation -> versioned analytical data
                              |
                              v
                       feature pipeline
                              |
             +----------------+----------------+
             v                v                v
        return model    risk/covariance    regime model
             |                |                |
             +----------------+----------------+
                              |
                     scenario processor
                              |
                     portfolio optimizer
                              |
                       risk constraints
                              |
          walk-forward simulator (costs and slippage)
                              |
       benchmark comparison, diagnostics, MLflow evidence
```

Boundaries matter:

- The data layer enforces `available_at`; it does not make forecasts.
- Models output estimates and uncertainty; they do not choose allocations.
- The optimizer converts estimates into weights under explicit constraints.
- The backtester controls the clock, rebalance timing, and execution costs.
- Reporting compares every experiment with SPY, equal weight, and 60/40 when applicable.
- FastAPI is an interface to research results, never a brokerage/execution gateway.

## Twenty milestones

Each milestone ends with tests, a short written interpretation, and a baseline comparison.

1. **Returns:** prices, arithmetic/log/cumulative returns; manual and NumPy calculations.
2. **Statistics:** mean, median, variance, standard deviation, sampling uncertainty.
3. **Portfolio algebra:** vectors, covariance matrices, `w.T @ mu`, and `w.T @ Sigma @ w`.
4. **NumPy fluency:** shapes, broadcasting, axis semantics, matrix multiplication, tests.
5. **Risk measures:** Sharpe, Sortino, drawdown, historical/parametric/Monte Carlo VaR, CVaR.
6. **Data contract:** adjusted prices, calendars, missing data, symbol mapping, `available_at`.
7. **Simple allocations:** equal weight and inverse volatility with turnover diagnostics.
8. **MPT:** minimum variance, mean-variance, maximum Sharpe, and an efficient frontier.
9. **Optimization foundations:** objectives, constraints, convexity, and solver verification.
10. **Risk-aware allocations:** risk parity, Kelly-inspired caps, CVaR-constrained allocation.
11. **Backtest engine:** lagged decisions, realistic rebalances, costs, slippage, benchmarks.
12. **Walk-forward evaluation:** expanding/rolling windows and nested chronological tuning.
13. **Time-series foundations:** stationarity, ACF/PACF, AR/MA/ARIMA, residual diagnostics.
14. **Features:** lag, momentum, moving average, volatility, volume, macro and event features.
15. **Forecast baselines:** historical mean, momentum, linear and logistic regression.
16. **Tree models:** trees, random forest, boosting, XGBoost/LightGBM, overfit controls.
17. **Regimes:** observable bull/bear and volatility rules, clustering, then HMMs.
18. **Alternative information:** timestamped probabilities and AI signals; ablation experiments.
19. **Advanced models:** PyTorch sequence models only after baselines; compare, do not presume.
20. **Research platform:** scenarios, sensitivity tests, MLflow, Optuna, API, Docker, final audit.

## Backtesting methodology

### Clock and information set

At decision time `t`, a strategy may use only records whose `available_at <= t`. Features are fit
on the training window only. Weights decided after the close at `t` first earn returns at `t+1`
(or later if the assumed execution delay requires it). Target labels are never features.

### Walk-forward protocol

1. Freeze a point-in-time universe and data/version manifest.
2. Choose an initial training window before looking at test results.
3. Fit preprocessing and the model using only that window.
4. Select hyperparameters inside that window using chronological inner folds.
5. Form weights using only information available at the decision timestamp.
6. Apply the specified execution lag, turnover cost, spread/slippage, and constraints.
7. Record the next out-of-sample interval, advance the clock, and repeat.
8. Concatenate untouched out-of-sample intervals and compute final metrics once.

The primary experiment is an ablation with identical dates, universe, constraints, and costs:

- quantitative baseline;
- baseline plus prediction-market features;
- baseline plus AI-derived features;
- baseline plus both.

Report annualized return and volatility, Sharpe, Sortino, maximum drawdown, CVaR, turnover,
concentration, and performance relative to benchmarks. Add confidence intervals for paired
return differences and test sensitivity to costs, execution delay, lookback, and constraints.

### Fake-good backtests to recognize

- Using today's index constituents throughout history creates survivorship bias.
- Trading on a same-day closing price using a signal computed from that close is look-ahead.
- Using revised GDP values before their revision date leaks future information.
- Standardizing all dates before splitting lets the test set influence training.
- Selecting the best of 1,000 strategies on one test period is data snooping.
- Ignoring turnover can make an untradeable strategy appear excellent.
- Random train/test splits leak temporal structure into financial forecasts.
- Repeatedly inspecting the test period quietly turns it into training data.

## Interview skills produced

By the end, you should be able to:

- derive portfolio expected return and variance and explain covariance's role;
- implement return and risk metrics from NumPy primitives;
- distinguish arithmetic average return, CAGR, and log return;
- explain why diversification depends on correlation rather than asset count alone;
- formulate an optimizer with an objective and explicit constraints;
- identify leakage, survivorship bias, data snooping, and unrealistic execution assumptions;
- design walk-forward and nested chronological validation;
- compare VaR with CVaR and state each method's assumptions;
- defend baselines and explain why a complex model failed to improve on them;
- describe point-in-time alternative-data experiments without making causal claims;
- discuss statistical uncertainty, multiple testing, costs, turnover, and capacity;
- review a research result as evidence rather than a promise of future profit.

## Start here

Complete [Module 1 — Returns](MODULE_01_RETURNS.md) without running the answer checks first.
Write out the manual calculations, implement the NumPy functions, then use the tests only to
diagnose discrepancies.
