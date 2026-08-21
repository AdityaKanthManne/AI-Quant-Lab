from prediction_market_agents.domain import Evidence, ForecastQuestion, MarketSnapshot

from .base import EvidenceConnector, MarketConnector


class StaticMarketConnector(MarketConnector):
    name = "static"

    def __init__(self, probability: float = 0.5) -> None:
        self.probability = probability

    async def snapshot(self, event_id: str) -> MarketSnapshot:
        return MarketSnapshot(
            market=self.name, market_event_id=event_id, probability=self.probability
        )


class StaticEvidenceConnector(EvidenceConnector):
    name = "static"

    def __init__(self, evidence: list[Evidence] | None = None) -> None:
        self.evidence = evidence or []

    async def retrieve(self, question: ForecastQuestion, limit: int = 10) -> list[Evidence]:
        return sorted(self.evidence, key=lambda item: item.relevance, reverse=True)[:limit]
