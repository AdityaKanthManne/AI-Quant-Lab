from fin_research.agents.base import BaseAgent
from fin_research.models.domain import AgentResult, Claim, ClaimKind


class SecFilingAgent(BaseAgent):
    async def run(self, ticker: str) -> AgentResult:
        facts, citations = await self.provider.filing_facts(ticker)
        citation_ids = [citation.id for citation in citations]
        return AgentResult(
            summary=f"Recent 10-K, 10-Q, and 8-K disclosures reviewed for {ticker}.",
            claims=[
                Claim(text=fact, kind=ClaimKind.FACT, citation_ids=citation_ids) for fact in facts
            ],
            citations=citations,
        )
