import pytest

from prediction_market_agents.evaluation import calibration_bins, evaluate_rows


def test_metrics_are_computed_for_resolved_forecasts() -> None:
    rows = [
        {"model_probability": 0.8, "market_probability": 0.6, "outcome": 1},
        {"model_probability": 0.2, "market_probability": 0.4, "outcome": 0},
    ]
    result = evaluate_rows(rows)
    assert result["count"] == 2
    assert result["brier_score"] == pytest.approx(0.04)
    assert result["sharpness"] > 0


def test_calibration_includes_probability_one_in_last_bin() -> None:
    result = calibration_bins([1.0], [1])
    assert result[0]["bin"] == 9
