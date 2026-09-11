from datetime import date, timedelta

from fin_research.analytics import calculate_signals


def test_calculate_signals() -> None:
    rows = [
        {"date": date(2025, 1, 1) + timedelta(days=i), "close": 100.0 + i, "volume": 1000.0}
        for i in range(30)
    ]
    result = calculate_signals(rows)
    assert result["return_20d"] > 0
    assert result["max_drawdown"] == 0
    assert result["volume_ratio_20d"] == 1
