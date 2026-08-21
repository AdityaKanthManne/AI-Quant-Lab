from pathlib import Path

import pytest

from prediction_market_agents.config import Settings
from prediction_market_agents.connectors.static import (
    StaticEvidenceConnector,
    StaticMarketConnector,
)
from prediction_market_agents.domain import ForecastQuestion
from prediction_market_agents.orchestration import ForecastGraph
from prediction_market_agents.service import ForecastService
from prediction_market_agents.storage import ForecastRepository


def test_repository_creates_nested_sqlite_parent(tmp_path: Path) -> None:
    database = tmp_path / "nested" / "forecasts.db"
    repository = ForecastRepository(f"sqlite:///{database}")
    repository.create_schema()
    assert database.exists()


@pytest.mark.asyncio
async def test_forecast_is_persisted(tmp_path: Path) -> None:
    repository = ForecastRepository(f"sqlite:///{tmp_path / 'test.db'}")
    repository.create_schema()
    graph = ForecastGraph(
        evidence_connectors=[StaticEvidenceConnector()],
        market_connectors={"static": StaticMarketConnector(0.43)},
    )
    service = ForecastService(graph, repository, Settings(database_url="sqlite:///:memory:"))
    result = await service.forecast(
        ForecastQuestion(
            question="Will the Federal Reserve cut rates at its next meeting?",
            market="static",
            market_event_id="fed-cut",
        )
    )
    assert result.market_probability == 0.43
    assert result.edge == pytest.approx(result.model_probability - 0.43)
    assert repository.get_forecast(result.forecast_id) == result
