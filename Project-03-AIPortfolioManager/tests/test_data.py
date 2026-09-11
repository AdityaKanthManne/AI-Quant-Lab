from datetime import date

import polars as pl
import pytest

from ai_portfolio.data import point_in_time_slice, prices_to_returns


def test_point_in_time_slice_excludes_unavailable_records() -> None:
    frame = pl.DataFrame(
        {
            "date": [date(2024, 1, 1), date(2024, 1, 2)],
            "asset": ["SPY", "SPY"],
            "close": [100.0, 101.0],
            "available_at": [date(2024, 1, 1), date(2024, 1, 3)],
        }
    )
    assert point_in_time_slice(frame, date(2024, 1, 2)).height == 1


def test_prices_to_returns_rejects_nonpositive_prices() -> None:
    frame = pl.DataFrame(
        {
            "date": [date(2024, 1, 1)],
            "asset": ["SPY"],
            "close": [0.0],
            "available_at": [date(2024, 1, 1)],
        }
    )
    with pytest.raises(ValueError, match="positive"):
        prices_to_returns(frame)
