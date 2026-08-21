from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
from pydantic import BaseModel

from research_copilot.models import ExperimentRecord, PaperMetadata, ResearchProject


class ProjectStore:
    """Append-oriented local artifact store; PostgreSQL adapters can index these artifacts."""

    folders = ("literature", "datasets", "hypotheses", "experiments", "results", "reports")

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug[:80] or "research-project"

    def create_project(self, project: ResearchProject) -> Path:
        path = self.root / project.slug
        if path.exists():
            raise FileExistsError(f"Project already exists: {project.slug}")
        path.mkdir(parents=True)
        for folder in self.folders:
            (path / folder).mkdir()
        self._write_yaml_new(path / "question.yaml", project.model_dump(mode="json"))
        return path

    def find_project(self, project_id: UUID) -> tuple[ResearchProject, Path]:
        for question_file in self.root.glob("*/question.yaml"):
            payload = yaml.safe_load(question_file.read_text())
            if payload.get("id") == str(project_id):
                return ResearchProject.model_validate(payload), question_file.parent
        raise KeyError(f"Unknown project: {project_id}")

    def save_papers(self, project_id: UUID, papers: list[PaperMetadata]) -> Path:
        _, path = self.find_project(project_id)
        target = path / "literature" / "papers.jsonl"
        with target.open("a", encoding="utf-8") as stream:
            for paper in papers:
                stream.write(paper.model_dump_json() + "\n")
        return target

    def create_experiment(self, experiment: ExperimentRecord) -> Path:
        _, project_path = self.find_project(experiment.project_id)
        path = project_path / "experiments" / str(experiment.id)
        path.mkdir()
        self._write_json_new(path / "spec.json", experiment)
        return path

    @staticmethod
    def _write_json_new(path: Path, value: BaseModel | dict[str, Any]) -> None:
        payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
        with path.open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2)

    @staticmethod
    def _write_yaml_new(path: Path, value: dict[str, Any]) -> None:
        with path.open("x", encoding="utf-8") as stream:
            yaml.safe_dump(value, stream, sort_keys=False)

