from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query

from prediction_market_agents.config import Settings, get_settings
from prediction_market_agents.connectors.fred import FredConnector
from prediction_market_agents.connectors.polymarket import PolymarketConnector
from prediction_market_agents.domain import ForecastQuestion, ForecastResult, Resolution
from prediction_market_agents.evaluation import evaluate_rows
from prediction_market_agents.experiments import compare_experiment_arms
from prediction_market_agents.orchestration import ForecastGraph
from prediction_market_agents.service import ForecastService
from prediction_market_agents.storage import ForecastRepository


@lru_cache
def get_repository() -> ForecastRepository:
    repository = ForecastRepository(get_settings().database_url)
    repository.create_schema()
    return repository


def get_service(
    settings: Annotated[Settings, Depends(get_settings)],
    repository: Annotated[ForecastRepository, Depends(get_repository)],
) -> ForecastService:
    graph = ForecastGraph(
        evidence_connectors=[
            FredConnector(settings.fred_api_key, settings.request_timeout_seconds)
        ],
        market_connectors={
            "polymarket": PolymarketConnector(
                settings.polymarket_base_url, settings.request_timeout_seconds
            )
        },
    )
    return ForecastService(graph, repository, settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_repository().create_schema()
    yield


app = FastAPI(
    title="Prediction Market Intelligence API",
    version="0.1.0",
    description="Calibrated forecasts for research; never an automatic trade recommendation.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/forecasts", response_model=ForecastResult, status_code=201)
async def create_forecast(
    question: ForecastQuestion,
    service: Annotated[ForecastService, Depends(get_service)],
) -> ForecastResult:
    try:
        return await service.forecast(question)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"forecast pipeline failed: {error}") from error


@app.get("/v1/forecasts/{forecast_id}", response_model=ForecastResult)
def read_forecast(
    forecast_id: UUID,
    repository: Annotated[ForecastRepository, Depends(get_repository)],
) -> ForecastResult:
    forecast = repository.get_forecast(forecast_id)
    if forecast is None:
        raise HTTPException(status_code=404, detail="forecast not found")
    return forecast


@app.get("/v1/events/{event_id}/history", response_model=list[ForecastResult])
def probability_history(
    event_id: UUID,
    repository: Annotated[ForecastRepository, Depends(get_repository)],
) -> list[ForecastResult]:
    return repository.history(event_id)


@app.post("/v1/resolutions", status_code=201)
def resolve_event(
    resolution: Resolution,
    repository: Annotated[ForecastRepository, Depends(get_repository)],
) -> dict[str, str]:
    repository.resolve(resolution)
    return {"status": "resolved"}


@app.get("/v1/metrics")
def metrics(
    repository: Annotated[ForecastRepository, Depends(get_repository)],
    source: Annotated[str, Query(pattern="^(model|market)$")] = "model",
) -> dict[str, Any]:
    return evaluate_rows(repository.scored_rows(), f"{source}_probability")


@app.get("/v1/experiments/leaderboard")
def experiment_leaderboard(
    repository: Annotated[ForecastRepository, Depends(get_repository)],
) -> dict[str, Any]:
    return compare_experiment_arms(repository.scored_rows())
