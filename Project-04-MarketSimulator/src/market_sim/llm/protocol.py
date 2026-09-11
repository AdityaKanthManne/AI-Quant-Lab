"""Provider-independent and leakage-resistant LLM forecasting boundary."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Forecast:
    probability: float
    confidence: float
    rationale: str


class Forecaster(Protocol):
    def forecast(self, evidence: list[str], market_context: str) -> Forecast: ...

