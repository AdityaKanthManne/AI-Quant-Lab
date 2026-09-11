from fin_research.agents.base import BaseAgent
from fin_research.analytics import calculate_signals
from fin_research.models.domain import AgentResult, Metric


class QuantitativeSignalAgent(BaseAgent):
    async def run(self, ticker: str) -> AgentResult:
        rows, citations = await self.provider.price_history(ticker)
        signals = calculate_signals(rows)
        metrics = [
            Metric(
                name=name,
                value=value,
                unit="ratio",
                citation_ids=[citation.id for citation in citations],
            )
            for name, value in signals.items()
        ]
        return AgentResult(
            summary=f"Deterministic price and volume signals calculated for {ticker}.",
            metrics=metrics,
            citations=citations,
        )
