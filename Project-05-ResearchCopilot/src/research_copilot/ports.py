"""Interfaces between research logic and external infrastructure.

The core workflow depends on these protocols. Concrete PostgreSQL, Qdrant, MLflow,
and model-provider adapters can be added without changing agent behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol
from uuid import UUID

from research_copilot.models import CodeArtifact, ExperimentRecord, PaperExtraction, PaperMetadata


class LanguageModel(Protocol):
    async def structured(self, *, system: str, prompt: str, schema: type[Any]) -> Any:
        """Return output validated against ``schema``."""


class PaperRepository(Protocol):
    async def upsert(self, project_id: UUID, papers: list[PaperMetadata]) -> None: ...

    async def get(self, paper_id: UUID) -> PaperMetadata | None: ...

    async def save_extraction(self, extraction: PaperExtraction) -> None: ...


class SemanticIndex(Protocol):
    async def index_paper(self, paper: PaperMetadata, extraction: PaperExtraction) -> None: ...

    async def search(self, project_id: UUID, query: str, limit: int = 10) -> list[UUID]: ...


class DatasetCatalog(Protocol):
    async def discover(self, query: str) -> list[dict[str, Any]]: ...

    async def snapshot(self, dataset_id: str, destination: Path) -> dict[str, str]:
        """Return provenance including version, checksum, license, and retrieval time."""


class ExperimentRepository(Protocol):
    async def create(self, experiment: ExperimentRecord) -> None: ...

    async def approve_code(self, artifact: CodeArtifact, reviewer: str) -> None: ...

    async def record_run(self, experiment_id: UUID, run_path: Path) -> None: ...


class ExperimentTracker(Protocol):
    def start_run(self, experiment: ExperimentRecord) -> str: ...

    def log_parameters(self, run_id: str, parameters: dict[str, Any]) -> None: ...

    def log_metrics(self, run_id: str, metrics: dict[str, float]) -> None: ...

    def log_artifact(self, run_id: str, path: Path) -> None: ...


class CodeExecutor(Protocol):
    def execute(self, project_slug: str, artifact: CodeArtifact) -> Path: ...

