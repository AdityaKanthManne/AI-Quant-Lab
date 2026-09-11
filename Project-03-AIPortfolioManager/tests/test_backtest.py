import numpy as np

from ai_portfolio.backtest import WalkForwardBacktester
from ai_portfolio.config import BacktestConfig
from ai_portfolio.models import HistoricalMeanModel


def test_walk_forward_backtest_produces_expected_length() -> None:
    assets = ("SPY", "TLT", "GLD")
    rng = np.random.default_rng(4)
    returns = rng.normal(0.0002, 0.01, size=(180, len(assets)))
    config = BacktestConfig(universe=assets, lookback_days=60, rebalance_every=20)
    result = WalkForwardBacktester(config).run(
        returns, HistoricalMeanModel(), "inverse_volatility"
    )
    assert result.returns.shape == (120,)
    assert result.weights.shape == (120, 3)
    assert "sharpe" in result.metrics
    assert result.metrics["turnover"] >= 0

