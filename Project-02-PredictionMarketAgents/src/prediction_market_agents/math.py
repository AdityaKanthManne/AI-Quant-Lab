import math
from collections.abc import Iterable, Sequence

import numpy as np


def clip_probability(p: float, epsilon: float = 1e-6) -> float:
    return min(1 - epsilon, max(epsilon, float(p)))


def logit(p: float) -> float:
    p = clip_probability(p)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)


def bayesian_update(prior: float, likelihood_ratios: Iterable[float]) -> float:
    """Update binary-event odds by independent likelihood ratios."""
    log_odds = logit(prior)
    for ratio in likelihood_ratios:
        if ratio <= 0:
            raise ValueError("likelihood ratios must be positive")
        log_odds += math.log(ratio)
    return sigmoid(log_odds)


def log_opinion_pool(probabilities: Sequence[float], weights: Sequence[float]) -> float:
    """Weighted geometric pooling in odds space; robust to probability extremes."""
    if not probabilities or len(probabilities) != len(weights):
        raise ValueError("probabilities and weights must be non-empty and equally sized")
    total = sum(weights)
    if total <= 0:
        raise ValueError("at least one weight must be positive")
    return sigmoid(sum(w * logit(p) for p, w in zip(probabilities, weights, strict=True)) / total)


def brier_score(probability: float, outcome: int) -> float:
    return (probability - outcome) ** 2


def logarithmic_loss(probability: float, outcome: int) -> float:
    p = clip_probability(probability)
    return -(outcome * math.log(p) + (1 - outcome) * math.log(1 - p))


def forecast_resolution(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    """Murphy resolution: weighted variance of bin outcome rates around base rate."""
    if len(probabilities) != len(outcomes) or not outcomes:
        raise ValueError("probabilities and outcomes must be non-empty and equally sized")
    base = float(np.mean(outcomes))
    bins = np.minimum((np.asarray(probabilities) * 10).astype(int), 9)
    return float(
        sum(
            np.sum(bins == i) * (np.mean(np.asarray(outcomes)[bins == i]) - base) ** 2
            for i in np.unique(bins)
        )
        / len(outcomes)
    )


def sharpness(probabilities: Sequence[float]) -> float:
    """Variance around 0.5; larger means forecasts are more decisive."""
    if not probabilities:
        raise ValueError("probabilities must not be empty")
    return float(np.mean((np.asarray(probabilities) - 0.5) ** 2))
