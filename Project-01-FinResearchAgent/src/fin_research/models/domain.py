from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ClaimKind(StrEnum):
    FACT = "fact"
    INTERPRETATION = "interpretation"
    FORECAST = "forecast"


class Citation(BaseModel):
    id: str
    source_name: str
    source_url: HttpUrl
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    document_date: date | None = None
    excerpt: str | None = None


class Claim(BaseModel):
    text: str
    kind: ClaimKind
    citation_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

    @field_validator("citation_ids")
    @classmethod
    def facts_require_citations(cls, value: list[str], info: Any) -> list[str]:
        if info.data.get("kind") == ClaimKind.FACT and not value:
            raise ValueError("fact claims require at least one citation")
        return value


class Metric(BaseModel):
    name: str
    value: float | int | None
    unit: str
    as_of: date | None = None
    citation_ids: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    status: Literal["complete", "partial", "unavailable"] = "complete"
    summary: str
    claims: list[Claim] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ResearchRequest(BaseModel):
    ticker: Annotated[str, Field(min_length=1, max_length=10, pattern=r"^[A-Z][A-Z0-9.-]*$")]

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


class ResearchReport(BaseModel):
    ticker: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: Literal["complete", "partial", "failed"]
    company_overview: str
    key_financial_metrics: list[Metric]
    recent_sec_developments: AgentResult
    macro_environment: AgentResult
    recent_events: AgentResult
    quantitative_signals: AgentResult
    bull_thesis: list[Claim]
    bear_thesis: list[Claim]
    catalysts: list[Claim]
    risks: list[Claim]
    model_confidence: Annotated[float, Field(ge=0, le=1)]
    citations: list[Citation]
    warnings: list[str] = Field(default_factory=list)

