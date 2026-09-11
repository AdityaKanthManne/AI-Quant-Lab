from __future__ import annotations

import numpy as np


def momentum(returns: np.ndarray, window: int = 63) -> np.ndarray:
    """Compounded trailing return by asset; input shape is time x assets."""

    if returns.ndim != 2 or len(returns) < window:
        raise ValueError("returns must be 2D with at least `window` rows")
    return np.prod(1.0 + returns[-window:], axis=0) - 1.0


def realized_volatility(returns: np.ndarray, annualization: int = 252) -> np.ndarray:
    return np.std(returns, axis=0, ddof=1) * np.sqrt(annualization)


def correlation_matrix(returns: np.ndarray) -> np.ndarray:
    return np.corrcoef(returns, rowvar=False)

