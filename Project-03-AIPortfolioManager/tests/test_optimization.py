import numpy as np

from ai_portfolio.domain import Forecast
from ai_portfolio.optimization import equal_weight, inverse_volatility, optimize


ASSETS = ("SPY", "TLT", "GLD")
FORECAST = Forecast(
    ASSETS,
    np.array([0.08, 0.03, 0.04]),
    np.diag([0.04, 0.01, 0.0225]),
)


def test_allocations_sum_to_one() -> None:
    for allocation in (
        equal_weight(ASSETS),
        inverse_volatility(FORECAST),
        optimize(FORECAST, "minimum_variance", max_weight=0.8),
        optimize(FORECAST, "maximum_sharpe", max_weight=0.8),
    ):
        assert np.isclose(allocation.weights.sum(), 1.0)
        assert np.all(allocation.weights >= 0)


def test_inverse_volatility_favors_low_volatility_asset() -> None:
    weights = inverse_volatility(FORECAST).weights
    assert weights[1] > weights[2] > weights[0]

