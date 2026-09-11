from abc import ABC, abstractmethod

from fin_research.data.providers import ResearchDataProvider
from fin_research.models.domain import AgentResult


class BaseAgent(ABC):
    def __init__(self, provider: ResearchDataProvider) -> None:
        self.provider = provider

    @abstractmethod
    async def run(self, ticker: str) -> AgentResult: ...

