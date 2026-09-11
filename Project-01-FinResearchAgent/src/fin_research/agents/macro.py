from fin_research.agents.base import BaseAgent
from fin_research.models.domain import AgentResult, Claim, ClaimKind


class MacroAgent(BaseAgent):
    async def run(self, ticker: str) -> AgentResult:
        metrics, citations = await self.provider.macro_metrics()
        return AgentResult(
            summary="Rates, inflation, labor, and growth indicators collected.",
            metrics=metrics,
            claims=[
                Claim(
                    text="Macro observations came from the configured provider.",
                    kind=ClaimKind.FACT,
                    citation_ids=[citation.id for citation in citations],
                )
            ],
            citations=citations,
        )

