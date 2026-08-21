from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    research_question: str = Field(min_length=10)
    description: str = ""


class ResearchProject(ProjectCreate):
    id: UUID = Field(default_factory=uuid4)
    slug: str
    created_at: datetime = Field(default_factory=utc_now)


class PaperIdentifier(BaseModel):
    doi: str | None = None
    arxiv_id: str | None = None
    semantic_scholar_id: str | None = None

    @model_validator(mode="after")
    def has_verifiable_id(self) -> PaperIdentifier:
        if not any((self.doi, self.arxiv_id, self.semantic_scholar_id)):
            raise ValueError("At least one verifiable paper identifier is required")
        return self


class PaperMetadata(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    abstract: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    url: HttpUrl | None = None
    identifiers: PaperIdentifier
    citation_count: int | None = None
    source: Literal["arxiv", "semantic_scholar", "crossref", "ssrn", "github", "manual"]
    retrieved_at: datetime = Field(default_factory=utc_now)


class PaperExtraction(BaseModel):
    paper_id: UUID
    research_question: str | None = None
    hypotheses: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    methodology: list[str] = Field(default_factory=list)
    models: list[str] = Field(default_factory=list)
    baselines: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    results: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    evidence_spans: dict[str, list[str]] = Field(default_factory=dict)


class ExperimentSpec(BaseModel):
    research_question: str
    hypothesis: str
    dependent_variable: str
    independent_variables: list[str]
    control_variables: list[str] = Field(default_factory=list)
    dataset: str
    baseline: list[str]
    models: list[str]
    evaluation_metrics: list[str]
    statistical_tests: list[str]
    split_strategy: Literal["train_validation_test", "time_series", "walk_forward"]
    potential_leakage: list[str] = Field(default_factory=list)
    potential_confounders: list[str] = Field(default_factory=list)
    robustness_tests: list[str] = Field(default_factory=list)
    multiple_comparison_correction: str | None = None
    random_seed: int = 42


class ReviewStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class CodeArtifact(BaseModel):
    experiment_id: UUID
    code: str
    status: ReviewStatus = ReviewStatus.DRAFT
    review_notes: list[str] = Field(default_factory=list)


class ExperimentRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    spec: ExperimentSpec
    status: Literal["planned", "approved", "running", "completed", "failed"] = "planned"
    created_at: datetime = Field(default_factory=utc_now)
    dataset_version: str | None = None
    environment: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    results: dict[str, Any] = Field(default_factory=dict)


class LiteratureSearchRequest(BaseModel):
    project_id: UUID
    query: str = Field(min_length=3)
    sources: list[str] = Field(default_factory=lambda: ["arxiv", "crossref"])
    limit: int = Field(default=10, ge=1, le=100)


class ClaimType(StrEnum):
    OBSERVED = "observed_empirical_result"
    INFERENCE = "statistical_inference"
    INTERPRETATION = "ai_interpretation"


class ReportClaim(BaseModel):
    text: str
    claim_type: ClaimType
    evidence_ids: list[str] = Field(default_factory=list)
