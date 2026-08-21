import pytest

from prediction_market_agents.math import (
    bayesian_update,
    brier_score,
    log_opinion_pool,
    logarithmic_loss,
)


def test_bayesian_update_operates_on_odds() -> None:
    assert bayesian_update(0.5, [2.0]) == pytest.approx(2 / 3)
    assert bayesian_update(0.2, [4.0]) == pytest.approx(0.5)


def test_log_pool_equal_opposing_forecasts_is_neutral() -> None:
    assert log_opinion_pool([0.2, 0.8], [1, 1]) == pytest.approx(0.5)


def test_proper_scores_reward_correct_confidence() -> None:
    assert brier_score(0.9, 1) < brier_score(0.6, 1)
    assert logarithmic_loss(0.9, 1) < logarithmic_loss(0.6, 1)


def test_invalid_likelihood_ratio_is_rejected() -> None:
    with pytest.raises(ValueError):
        bayesian_update(0.5, [0])
