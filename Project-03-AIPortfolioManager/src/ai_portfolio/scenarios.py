from __future__ import annotations

import numpy as np

from .domain import Forecast, Scenario


def apply_scenarios(forecast: Forecast, scenarios: list[Scenario]) -> Forecast:
    """Create a probability-weighted forecast without encoding economic directionality."""

    mu = forecast.expected_returns.copy()
    covariance = forecast.covariance.copy()
    index = {asset: i for i, asset in enumerate(forecast.assets)}
    signals = dict(forecast.signals)

    for scenario in scenarios:
        signals[f"scenario:{scenario.name}"] = scenario.probability
        for asset, shock in scenario.return_shocks.items():
            if asset in index:
                mu[index[asset]] += scenario.probability * shock
        for asset, multiplier in scenario.volatility_multipliers.items():
            if asset in index:
                i = index[asset]
                scale = 1 + scenario.probability * (multiplier - 1)
                covariance[i, :] *= scale
                covariance[:, i] *= scale

    return Forecast(forecast.assets, mu, covariance, forecast.regime, signals)

