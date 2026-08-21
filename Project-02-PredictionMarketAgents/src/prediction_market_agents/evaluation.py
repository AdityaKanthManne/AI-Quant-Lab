from collections import defaultdict
from typing import Any

import numpy as np
import polars as pl

from prediction_market_agents.math import (
    brier_score,
    forecast_resolution,
    logarithmic_loss,
    sharpness,
)


def calibration_bins(
    probabilities: list[float], outcomes: list[int], bins: int = 10
) -> list[dict[str, Any]]:
    if len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must be equally sized")
    grouped: dict[int, list[tuple[float, int]]] = defaultdict(list)
    for p, y in zip(probabilities, outcomes, strict=True):
        grouped[min(int(p * bins), bins - 1)].append((p, y))
    return [
        {
            "bin": index,
            "mean_probability": float(np.mean([p for p, _ in values])),
            "observed_frequency": float(np.mean([y for _, y in values])),
            "count": len(values),
        }
        for index, values in sorted(grouped.items())
    ]


def evaluate_rows(
    rows: list[dict[str, Any]], probability_field: str = "model_probability"
) -> dict[str, Any]:
    usable = [row for row in rows if row.get(probability_field) is not None]
    if not usable:
        return {"count": 0, "brier_score": None, "log_loss": None, "calibration": []}
    frame = pl.DataFrame(usable)
    probabilities = frame[probability_field].cast(pl.Float64).to_list()
    outcomes = frame["outcome"].cast(pl.Int64).to_list()
    return {
        "count": len(usable),
        "brier_score": float(
            np.mean([brier_score(p, y) for p, y in zip(probabilities, outcomes, strict=True)])
        ),
        "log_loss": float(
            np.mean([logarithmic_loss(p, y) for p, y in zip(probabilities, outcomes, strict=True)])
        ),
        "sharpness": sharpness(probabilities),
        "resolution": forecast_resolution(probabilities, outcomes),
        "calibration": calibration_bins(probabilities, outcomes),
    }
