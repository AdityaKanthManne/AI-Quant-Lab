from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import polars as pl


REQUIRED_MARKET_COLUMNS = {"date", "asset", "close", "available_at"}


def validate_market_data(frame: pl.DataFrame) -> pl.DataFrame:
    missing = REQUIRED_MARKET_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"market data missing columns: {sorted(missing)}")
    if frame.select(pl.col("close").is_null().any()).item():
        raise ValueError("close prices may not contain nulls")
    if frame.filter(pl.col("close") <= 0).height:
        raise ValueError("close prices must be positive")
    if frame.filter(pl.col("available_at") < pl.col("date")).height:
        raise ValueError("available_at may not precede market date")
    return frame.sort(["date", "asset"])


def point_in_time_slice(frame: pl.DataFrame, decision_date: date) -> pl.DataFrame:
    """Return only records observable by the specified portfolio decision date."""

    return frame.filter(pl.col("available_at") <= decision_date)


def prices_to_returns(frame: pl.DataFrame) -> pl.DataFrame:
    validated = validate_market_data(frame)
    return (
        validated.sort(["asset", "date"])
        .with_columns(pl.col("close").pct_change().over("asset").alias("return"))
        .drop_nulls("return")
    )


class DuckDBStore:
    """Small analytical store; PostgreSQL is reserved for service metadata."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.connection = duckdb.connect(str(path))

    def write_market_data(self, frame: pl.DataFrame) -> None:
        validated = validate_market_data(frame)
        self.connection.register("incoming_market_data", validated.to_arrow())
        self.connection.execute(
            "CREATE OR REPLACE TABLE market_data AS SELECT * FROM incoming_market_data"
        )

    def read_market_data(self) -> pl.DataFrame:
        return self.connection.sql("SELECT * FROM market_data ORDER BY date, asset").pl()

