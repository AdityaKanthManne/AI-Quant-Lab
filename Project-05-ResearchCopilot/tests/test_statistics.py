import numpy as np

from research_copilot.statistics import benjamini_hochberg, bootstrap_mean_difference


def test_benjamini_hochberg_preserves_order_and_bounds():
    adjusted = benjamini_hochberg([0.01, 0.04, 0.03])
    assert adjusted == [0.03, 0.04, 0.04]


def test_bootstrap_is_reproducible():
    a = np.array([2.0, 3.0, 4.0, 5.0])
    b = np.array([1.0, 2.0, 2.0, 3.0])
    first = bootstrap_mean_difference(a, b, samples=200, seed=7)
    second = bootstrap_mean_difference(a, b, samples=200, seed=7)
    assert first == second
    assert first.effect_size is not None

