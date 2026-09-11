"""Pure metric functions suitable for batch experiments."""

from __future__ import annotations

import numpy as np


def brier_score(probabilities: list[float], outcomes: list[int]) -> float:
    if len(probabilities) != len(outcomes) or not probabilities:
        raise ValueError("probabilities and outcomes must have equal non-zero length")
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    return float(np.mean((p - y) ** 2))


def information_incorporation_time(prices: list[float], truth: float, tolerance: float) -> int | None:
    """First index after which price remains within tolerance of truth."""
    for index in range(len(prices)):
        if all(abs(price - truth) <= tolerance for price in prices[index:]):
            return index
    return None

