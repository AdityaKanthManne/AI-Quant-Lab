from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class StatisticalResult:
    estimate: float
    confidence_interval: tuple[float, float]
    p_value: float | None
    effect_size: float | None
    interpretation: str


def bootstrap_mean_difference(
    treatment: np.ndarray, control: np.ndarray, *, samples: int = 10_000, seed: int = 42
) -> StatisticalResult:
    """Estimate an independent-sample mean difference and percentile bootstrap CI."""
    if treatment.size < 2 or control.size < 2:
        raise ValueError("Both samples require at least two observations")
    rng = np.random.default_rng(seed)
    differences = np.empty(samples)
    for index in range(samples):
        a = rng.choice(treatment, treatment.size, replace=True)
        b = rng.choice(control, control.size, replace=True)
        differences[index] = a.mean() - b.mean()
    estimate = float(treatment.mean() - control.mean())
    ci = tuple(float(x) for x in np.quantile(differences, [0.025, 0.975]))
    test = stats.ttest_ind(treatment, control, equal_var=False)
    pooled_sd = np.sqrt((treatment.var(ddof=1) + control.var(ddof=1)) / 2)
    effect = estimate / pooled_sd if pooled_sd else 0.0
    return StatisticalResult(estimate, ci, float(test.pvalue), float(effect),
                             "Association is not causation; inspect design and robustness checks.")


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Control false discovery rate while preserving original hypothesis order."""
    if any(not 0 <= p <= 1 for p in p_values):
        raise ValueError("p-values must be between zero and one")
    n = len(p_values)
    order = np.argsort(p_values)
    adjusted = np.empty(n)
    running = 1.0
    for rank_index in range(n - 1, -1, -1):
        original_index = order[rank_index]
        rank = rank_index + 1
        running = min(running, p_values[original_index] * n / rank)
        adjusted[original_index] = running
    return adjusted.tolist()

