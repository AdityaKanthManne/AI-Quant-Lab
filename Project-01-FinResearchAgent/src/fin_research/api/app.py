from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request

from fin_research.config import get_settings
from fin_research.models.domain import ResearchReport, ResearchRequest
from fin_research.services import ResearchService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.research_service = ResearchService(get_settings().data_mode)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Autonomous Financial Research Agent",
        version="0.1.0",
        description="Evidence-first research for US-listed equities.",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "data_mode": get_settings().data_mode}

    @app.post("/research", response_model=ResearchReport)
    async def research(payload: ResearchRequest, request: Request) -> ResearchReport:
        service: ResearchService = request.app.state.research_service
        return await service.research(payload)

    return app


app = create_app()

