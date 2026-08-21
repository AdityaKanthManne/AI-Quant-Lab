from prediction_market_agents.config import Settings
from prediction_market_agents.domain import Direction, ForecastQuestion, ForecastResult
from prediction_market_agents.orchestration import ForecastGraph
from prediction_market_agents.storage import ForecastRepository


class ForecastService:
    def __init__(
        self, graph: ForecastGraph, repository: ForecastRepository, settings: Settings
    ) -> None:
        self.graph = graph
        self.repository = repository
        self.settings = settings

    async def forecast(self, question: ForecastQuestion) -> ForecastResult:
        state = await self.graph.run(question)
        evidence = state.get("evidence", [])
        snapshot = state.get("market_snapshot")
        market_probability = None if snapshot is None else snapshot.probability
        model_probability = state["model_probability"]
        base = next(f for f in state["agent_forecasts"] if f.agent == "historical_base_rate")
        positive = [e.title for e in evidence if e.direction == Direction.INCREASE]
        negative = [e.title for e in evidence if e.direction == Direction.DECREASE]
        result = ForecastResult(
            event_id=question.event_id,
            question=question.question,
            market_probability=market_probability,
            model_probability=model_probability,
            edge=None if market_probability is None else model_probability - market_probability,
            interval_low=state["interval_low"],
            interval_high=state["interval_high"],
            prior_probability=base.probability,
            evidence=evidence,
            agent_forecasts=state["agent_forecasts"],
            positive_evidence=positive,
            negative_evidence=negative,
            disagreement=state["disagreement"],
            final_reasoning=(
                "The final estimate is a confidence-weighted logarithmic opinion pool. "
                "The interval expands with cross-agent disagreement and is not a trade recommendation."
            ),
            model_version=self.settings.model_version,
        )
        self.repository.save_forecast(result)
        return result
