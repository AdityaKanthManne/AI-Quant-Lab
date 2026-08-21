from pathlib import Path
from typing import Any

import duckdb
import polars as pl


class AnalyticsWarehouse:
    """DuckDB/Polars analytical layer kept separate from transactional PostgreSQL."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = duckdb.connect(str(path))

    def replace_scored_forecasts(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        frame = pl.DataFrame(rows).to_arrow()
        self.connection.register("scored_frame", frame)
        self.connection.execute(
            "CREATE OR REPLACE TABLE scored_forecasts AS SELECT * FROM scored_frame"
        )

    def rolling_brier(self, window: int = 50) -> list[dict[str, Any]]:
        query = """
            SELECT created_at, AVG(POWER(model_probability - outcome, 2))
              OVER (ORDER BY created_at ROWS BETWEEN ? PRECEDING AND CURRENT ROW) AS rolling_brier
            FROM scored_forecasts ORDER BY created_at
        """
        return [
            dict(zip(["created_at", "rolling_brier"], row, strict=True))
            for row in self.connection.execute(query, [max(0, window - 1)]).fetchall()
        ]
