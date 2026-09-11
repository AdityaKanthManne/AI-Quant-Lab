from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from .domain import Allocation, Forecast


def _normalize(weights: np.ndarray) -> np.ndarray:
    total = weights.sum()
    if total <= 0:
        raise ValueError("weights must have a positive sum")
    return weights / total


def equal_weight(assets: tuple[str, ...]) -> Allocation:
    return Allocation(assets, np.full(len(assets), 1 / len(assets)), "equal_weight")


def inverse_volatility(forecast: Forecast) -> Allocation:
    volatility = np.sqrt(np.maximum(np.diag(forecast.covariance), 1e-12))
    return Allocation(forecast.assets, _normalize(1 / volatility), "inverse_volatility")


def optimize(
    forecast: Forecast,
    method: str = "minimum_variance",
    risk_free_rate: float = 0.02,
    max_weight: float = 1.0,
) -> Allocation:
    n = len(forecast.assets)
    if max_weight * n < 1:
        raise ValueError("max_weight is infeasible for the number of assets")
    bounds = [(0.0, max_weight)] * n
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}

    def variance(w: np.ndarray) -> float:
        return float(w @ forecast.covariance @ w)

    if method == "minimum_variance":
        objective = variance
    elif method == "maximum_sharpe":
        objective = lambda w: (
            -float(
                (w @ forecast.expected_returns - risk_free_rate) / np.sqrt(max(variance(w), 1e-12))
            )
        )
    elif method == "mean_variance":
        objective = lambda w: -(float(w @ forecast.expected_returns) - 0.5 * variance(w))
    else:
        raise ValueError(f"unknown optimization method: {method}")

    result = minimize(
        objective,
        np.full(n, 1 / n),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    if not result.success:
        return Allocation(
            forecast.assets,
            equal_weight(forecast.assets).weights,
            method,
            (f"optimizer fallback: {result.message}",),
        )
    return Allocation(forecast.assets, _normalize(result.x), method)
