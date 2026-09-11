from typing import TypedDict

from fin_research.models.domain import AgentResult, ResearchReport, ResearchRequest


class ResearchState(TypedDict, total=False):
    request: ResearchRequest
    fundamentals: AgentResult
    filings: AgentResult
    macro: AgentResult
    news: AgentResult
    quant: AgentResult
    report: ResearchReport
    errors: list[str]
