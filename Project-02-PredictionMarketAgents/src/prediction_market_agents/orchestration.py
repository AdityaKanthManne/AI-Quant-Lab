from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from prediction_market_agents.agents import AgentSuite, ForecastAggregator
from prediction_market_agents.connectors.base import EvidenceConnector, MarketConnector
from prediction_market_agents.domain import (
    AgentForecast,
    Evidence,
    ForecastQuestion,
    MarketSnapshot,
)


class ForecastState(TypedDict, total=False):
    question: ForecastQuestion
    market_snapshot: MarketSnapshot | None
    evidence: Annotated[list[Evidence], add]
    agent_forecasts: list[AgentForecast]
    model_probability: float
    interval_low: float
    interval_high: float
    disagreement: float


class ForecastGraph:
    """LangGraph workflow with parallel market and evidence retrieval branches."""

    def __init__(
        self,
        evidence_connectors: list[EvidenceConnector],
        market_connectors: dict[str, MarketConnector],
        suite: AgentSuite | None = None,
        aggregator: ForecastAggregator | None = None,
    ) -> None:
        self.evidence_connectors = evidence_connectors
        self.market_connectors = market_connectors
        self.suite = suite or AgentSuite()
        self.aggregator = aggregator or ForecastAggregator()
        graph = StateGraph(ForecastState)
        graph.add_node("market", self._market)
        graph.add_node("evidence", self._evidence)
        graph.add_node("agents", self._agents)
        graph.add_node("aggregate", self._aggregate)
        graph.add_edge(START, "market")
        graph.add_edge(START, "evidence")
        graph.add_edge("market", "agents")
        graph.add_edge("evidence", "agents")
        graph.add_edge("agents", "aggregate")
        graph.add_edge("aggregate", END)
        self.compiled = graph.compile()

    async def _market(self, state: ForecastState) -> dict:
        question = state["question"]
        if not question.market or not question.market_event_id:
            return {"market_snapshot": None}
        connector = self.market_connectors.get(question.market)
        if connector is None:
            raise ValueError(f"unsupported market: {question.market}")
        return {"market_snapshot": await connector.snapshot(question.market_event_id)}

    async def _evidence(self, state: ForecastState) -> dict:
        question = state["question"]
        evidence: list[Evidence] = []
        for connector in self.evidence_connectors:
            evidence.extend(await connector.retrieve(question))
        evidence.sort(
            key=lambda item: (item.relevance * item.credibility, item.retrieved_at), reverse=True
        )
        return {"evidence": evidence[:30]}

    async def _agents(self, state: ForecastState) -> dict:
        return {"agent_forecasts": self.suite.run(state["question"], state.get("evidence", []))}

    async def _aggregate(self, state: ForecastState) -> dict:
        probability, low, high, disagreement = self.aggregator.aggregate(state["agent_forecasts"])
        return {
            "model_probability": probability,
            "interval_low": low,
            "interval_high": high,
            "disagreement": disagreement,
        }

    async def run(self, question: ForecastQuestion) -> ForecastState:
        return await self.compiled.ainvoke({"question": question, "evidence": []})
