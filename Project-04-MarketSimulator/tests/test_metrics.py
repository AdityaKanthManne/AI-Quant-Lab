from market_sim.metrics.core import brier_score, information_incorporation_time


def test_brier_score() -> None:
    assert brier_score([0.8, 0.3], [1, 0]) == 0.065


def test_information_incorporation_requires_persistence() -> None:
    prices = [0.4, 0.64, 0.5, 0.63, 0.65]
    assert information_incorporation_time(prices, 0.65, 0.03) == 3

