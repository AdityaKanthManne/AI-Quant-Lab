from datetime import date

import polars as pl


def calculate_signals(rows: list[dict[str, float | date]]) -> dict[str, float | None]:
    if len(rows) < 21:
        raise ValueError("at least 21 price observations are required")

    frame = (
        pl.DataFrame(rows)
        .sort("date")
        .with_columns(
            pl.col("close").pct_change().alias("return"),
            pl.col("close").rolling_mean(20).alias("sma_20"),
            pl.col("volume").rolling_mean(20).alias("volume_mean_20"),
            pl.col("close").cum_max().alias("peak"),
        )
        .with_columns(
            (pl.col("close") / pl.col("peak") - 1).alias("drawdown"),
            (pl.col("volume") / pl.col("volume_mean_20")).alias("volume_ratio"),
        )
    )
    latest = frame.tail(1).to_dicts()[0]
    closes = frame["close"]
    return {
        "return_20d": float(closes[-1] / closes[-21] - 1),
        "volatility_daily": float(frame["return"].std()),
        "price_vs_sma_20": float(latest["close"] / latest["sma_20"] - 1),
        "max_drawdown": float(frame["drawdown"].min()),
        "volume_ratio_20d": float(latest["volume_ratio"]),
    }

