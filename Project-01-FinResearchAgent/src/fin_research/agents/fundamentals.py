from fin_research.agents.base import BaseAgent
from fin_research.models.domain import AgentResult, Claim, ClaimKind


class FundamentalsAgent(BaseAgent):
    async def run(self, ticker: str) -> AgentResult:
        metrics, citations = await self.provider.company_metrics(ticker)
        return AgentResult(
            summary=f"Structured fundamental metrics collected for {ticker}.",
            metrics=metrics,
            claims=[
                Claim(
                    text="The reported fundamental values came from the configured data provider.",
                    kind=ClaimKind.FACT,
                    citation_ids=[citation.id for citation in citations],
                )
            ],
            citations=citations,
        )

