from __future__ import annotations

import numpy as np


def drawdown_series(returns: np.ndarray) -> np.ndarray:
    wealth = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(wealth)
    return wealth / peak - 1


def risk_metrics(
    returns: np.ndarray,
    benchmark_returns: np.ndarray | None = None,
    annualization: int = 252,
    risk_free_rate: float = 0.0,
    confidence: float = 0.95,
) -> dict[str, float]:
    returns = np.asarray(returns, dtype=float)
    annual_return = float(np.mean(returns) * annualization)
    volatility = float(np.std(returns, ddof=1) * np.sqrt(annualization))
    downside = returns[returns < 0]
    downside_vol = float(np.std(downside, ddof=1) * np.sqrt(annualization)) if len(downside) > 1 else 0.0
    loss_cutoff = float(np.quantile(returns, 1 - confidence))
    tail = returns[returns <= loss_cutoff]
    metrics = {
        "annual_return": annual_return,
        "volatility": volatility,
        "sharpe": (annual_return - risk_free_rate) / volatility if volatility else 0.0,
        "sortino": (annual_return - risk_free_rate) / downside_vol if downside_vol else 0.0,
        "max_drawdown": float(drawdown_series(returns).min()),
        "var": -loss_cutoff,
        "cvar": float(-tail.mean()) if len(tail) else 0.0,
    }
    if benchmark_returns is not None:
        benchmark = np.asarray(benchmark_returns, dtype=float)
        covariance = np.cov(returns, benchmark, ddof=1)
        metrics["beta"] = float(covariance[0, 1] / covariance[1, 1]) if covariance[1, 1] else 0.0
    return metrics


def turnover(previous: np.ndarray, current: np.ndarray) -> float:
    return float(np.abs(current - previous).sum())


def concentration(weights: np.ndarray) -> float:
    """Herfindahl-Hirschman concentration; 1/n is diversified, 1 is concentrated."""

    return float(np.square(weights).sum())

