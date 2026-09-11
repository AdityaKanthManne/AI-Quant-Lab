import numpy as np

from ai_portfolio.domain import Forecast, Scenario
from ai_portfolio.scenarios import apply_scenarios


def test_scenario_uses_probability_weighted_return_shock() -> None:
    forecast = Forecast(("SPY", "TLT"), np.zeros(2), np.eye(2))
    scenario = Scenario("event", 0.25, {"SPY": 0.04})
    adjusted = apply_scenarios(forecast, [scenario])
    assert np.isclose(adjusted.expected_returns[0], 0.01)
    assert adjusted.signals["scenario:event"] == 0.25

