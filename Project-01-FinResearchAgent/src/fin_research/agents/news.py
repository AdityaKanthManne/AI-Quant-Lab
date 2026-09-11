from fin_research.agents.base import BaseAgent
from fin_research.models.domain import AgentResult, Claim, ClaimKind


class NewsSentimentAgent(BaseAgent):
    async def run(self, ticker: str) -> AgentResult:
        events, citations = await self.provider.news_events(ticker)
        citation_ids = [citation.id for citation in citations]
        return AgentResult(
            summary=f"Recent factual events separated from commentary for {ticker}.",
            claims=[
                Claim(text=event, kind=ClaimKind.FACT, citation_ids=citation_ids)
                for event in events
            ],
            citations=citations,
        )
