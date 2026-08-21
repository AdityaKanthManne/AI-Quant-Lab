from abc import ABC, abstractmethod

from prediction_market_agents.domain import Evidence, ForecastQuestion, MarketSnapshot


class MarketConnector(ABC):
    name: str

    @abstractmethod
    async def snapshot(self, event_id: str) -> MarketSnapshot: ...

    async def search(self, query: str, limit: int = 10) -> list[MarketSnapshot]:
        raise NotImplementedError(f"{self.name} does not support search")


class EvidenceConnector(ABC):
    name: str

    @abstractmethod
    async def retrieve(self, question: ForecastQuestion, limit: int = 10) -> list[Evidence]: ...
