from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
from fastapi import FastAPI

from .config import DEFAULT_UNIVERSE
from .models import HistoricalMeanModel
from .optimization import inverse_volatility
from .reporting import portfolio_report

app = FastAPI(
    title="AI Portfolio Research Engine",
    version="0.1.0",
    description="Research and simulation API. Not a live-money trading system.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "purpose": "research-only"}


@app.get("/demo-report")
def demo_report(seed: int = 7) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0003, 0.012, size=(504, len(DEFAULT_UNIVERSE)))
    forecast = HistoricalMeanModel().fit_predict(DEFAULT_UNIVERSE, returns)
    allocation = inverse_volatility(forecast)
    return portfolio_report(datetime.now(UTC).date(), allocation, forecast, cvar=0.0)
