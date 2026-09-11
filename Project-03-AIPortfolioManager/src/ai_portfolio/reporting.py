from __future__ import annotations

from datetime import date

import numpy as np

from .domain import Allocation, Forecast


def portfolio_report(
    portfolio_date: date,
    allocation: Allocation,
    forecast: Forecast,
    cvar: float,
) -> dict[str, object]:
    weights = dict(zip(allocation.assets, map(float, allocation.weights), strict=True))
    portfolio_return = float(allocation.weights @ forecast.expected_returns)
    portfolio_vol = float(np.sqrt(allocation.weights @ forecast.covariance @ allocation.weights))
    return {
        "portfolio_date": portfolio_date.isoformat(),
        "asset_weights": weights,
        "expected_return": portfolio_return,
        "expected_volatility": portfolio_vol,
        "cvar": cvar,
        "detected_regime": forecast.regime,
        "top_signals": dict(forecast.signals),
        "risk_warnings": list(allocation.warnings),
    }
