from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, HTTPException

from research_copilot.config import settings
from research_copilot.literature import LiteratureClient
from research_copilot.models import (
    ExperimentRecord,
    ExperimentSpec,
    LiteratureSearchRequest,
    ProjectCreate,
    ResearchProject,
)
from research_copilot.storage import ProjectStore

app = FastAPI(title=settings.app_name, version="0.1.0")
store = ProjectStore(settings.research_copilot_home)
literature = LiteratureClient()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/research/projects", response_model=ResearchProject, status_code=201)
def create_project(request: ProjectCreate) -> ResearchProject:
    slug = store.slugify(request.name)
    project = ResearchProject(**request.model_dump(), slug=slug)
    try:
        store.create_project(project)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return project


@app.post("/research/literature/search")
async def search_literature(request: LiteratureSearchRequest) -> dict:
    try:
        store.find_project(request.project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    papers = await literature.search(request.query, request.sources, request.limit)
    store.save_papers(request.project_id, papers)
    return {"count": len(papers), "papers": [paper.model_dump(mode="json") for paper in papers]}


@app.post("/research/hypothesis")
def validate_hypothesis(spec: ExperimentSpec) -> dict:
    return {"status": "validated", "experiment_spec": spec}


@app.post("/research/experiment", response_model=ExperimentRecord, status_code=201)
def create_experiment(project_id: UUID, spec: ExperimentSpec) -> ExperimentRecord:
    record = ExperimentRecord(project_id=project_id, spec=spec)
    try:
        store.create_experiment(record)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return record


@app.get("/research/results/{experiment_id}")
def get_results(experiment_id: UUID) -> dict:
    for result in settings.research_copilot_home.glob(f"*/experiments/{experiment_id}/runs/*/result.json"):
        return {"experiment_id": experiment_id, "result_path": str(result)}
    raise HTTPException(status_code=404, detail="No result found")

