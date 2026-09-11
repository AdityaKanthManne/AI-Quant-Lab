from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import BacktestConfig
from .models import ForecastModel
from .optimization import equal_weight, inverse_volatility, optimize
from .risk import concentration, risk_metrics, turnover


@dataclass(frozen=True)
class BacktestResult:
    returns: np.ndarray
    weights: np.ndarray
    metrics: dict[str, float]


class WalkForwardBacktester:
    """Fit strictly before each rebalance and hold weights over future observations."""

    def __init__(self, config: BacktestConfig) -> None:
        self.config = config

    def run(
        self,
        returns: np.ndarray,
        model: ForecastModel,
        portfolio_method: str = "inverse_volatility",
    ) -> BacktestResult:
        if returns.ndim != 2 or returns.shape[1] != len(self.config.universe):
            raise ValueError("returns shape must be time x configured universe")
        if len(returns) <= self.config.lookback_days:
            raise ValueError("not enough observations for configured lookback")

        weights = np.zeros_like(returns)
        strategy_returns = np.zeros(len(returns))
        previous = equal_weight(self.config.universe).weights
        total_turnover = 0.0

        for start in range(
            self.config.lookback_days,
            len(returns),
            self.config.rebalance_every,
        ):
            train = returns[start - self.config.lookback_days : start]
            forecast = model.fit_predict(self.config.universe, train)
            if portfolio_method == "equal_weight":
                allocation = equal_weight(self.config.universe)
            elif portfolio_method == "inverse_volatility":
                allocation = inverse_volatility(forecast)
            else:
                allocation = optimize(
                    forecast,
                    portfolio_method,
                    self.config.risk_free_rate,
                    self.config.constraints.max_asset_weight,
                )

            end = min(start + self.config.rebalance_every, len(returns))
            current = allocation.weights
            trade_turnover = turnover(previous, current)
            total_turnover += trade_turnover
            costs = trade_turnover * self.config.transaction_cost_bps / 10_000
            # The decision made at `start` earns only returns from `start` onward.
            strategy_returns[start:end] = returns[start:end] @ current
            strategy_returns[start] -= costs
            weights[start:end] = current
            previous = current

        live = strategy_returns[self.config.lookback_days :]
        benchmark = returns[self.config.lookback_days :, 0]
        metrics = risk_metrics(
            live,
            benchmark,
            self.config.annualization,
            self.config.risk_free_rate,
        )
        metrics.update(
            turnover=total_turnover,
            exposure_concentration=concentration(previous),
        )
        return BacktestResult(live, weights[self.config.lookback_days :], metrics)
