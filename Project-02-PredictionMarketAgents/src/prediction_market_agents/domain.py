from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class Category(StrEnum):
    MACRO = "macro"
    CRYPTO = "crypto"
    POLITICS = "politics"
    EARNINGS = "earnings"
    OTHER = "other"


class Direction(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"
    NEUTRAL = "neutral"


class ForecastQuestion(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    question: str = Field(min_length=10)
    description: str | None = None
    category: Category = Category.OTHER
    resolution_time: datetime | None = None
    resolution_criteria: str | None = None
    market: str | None = None
    market_event_id: str | None = None
    features: dict[str, float] = Field(default_factory=dict)


class Evidence(BaseModel):
    source: str
    title: str
    url: str | None = None
    published_at: datetime | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    summary: str
    relevance: float = Field(ge=0, le=1)
    credibility: float = Field(default=0.7, ge=0, le=1)
    direction: Direction = Direction.NEUTRAL
    likelihood_ratio: float = Field(default=1.0, gt=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentForecast(BaseModel):
    agent: str
    probability: float = Field(ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)
    weight: float = Field(default=1.0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MarketSnapshot(BaseModel):
    market: str
    market_event_id: str
    probability: float = Field(ge=0, le=1)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    volume: float | None = None
    liquidity: float | None = None
    change_24h: float | None = None
    history: list[tuple[datetime, float]] = Field(default_factory=list)


class ForecastResult(BaseModel):
    forecast_id: UUID = Field(default_factory=uuid4)
    event_id: UUID
    question: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    market_probability: float | None = Field(default=None, ge=0, le=1)
    model_probability: float = Field(ge=0, le=1)
    edge: float | None = None
    interval_low: float = Field(ge=0, le=1)
    interval_high: float = Field(ge=0, le=1)
    prior_probability: float = Field(ge=0, le=1)
    evidence: list[Evidence]
    agent_forecasts: list[AgentForecast]
    positive_evidence: list[str] = Field(default_factory=list)
    negative_evidence: list[str] = Field(default_factory=list)
    disagreement: float = Field(ge=0)
    final_reasoning: str
    model_version: str

    @model_validator(mode="after")
    def validate_interval_and_edge(self) -> "ForecastResult":
        if not self.interval_low <= self.model_probability <= self.interval_high:
            raise ValueError("model probability must fall inside uncertainty interval")
        expected = (
            None
            if self.market_probability is None
            else self.model_probability - self.market_probability
        )
        if expected is not None and self.edge is not None and abs(expected - self.edge) > 1e-8:
            raise ValueError("edge must equal model_probability - market_probability")
        return self


class Resolution(BaseModel):
    event_id: UUID
    outcome: int = Field(ge=0, le=1)
    resolved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_url: str | None = None
    notes: str | None = None
