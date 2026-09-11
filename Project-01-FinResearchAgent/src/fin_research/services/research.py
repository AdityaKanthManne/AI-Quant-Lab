from typing import cast

from fin_research.data.providers import DemoDataProvider, LiveDataProvider
from fin_research.models.domain import ResearchReport, ResearchRequest
from fin_research.services.graph import build_research_graph
from fin_research.services.guardrails import validate_report


class ResearchService:
    def __init__(self, data_mode: str = "demo") -> None:
        provider = DemoDataProvider() if data_mode == "demo" else LiveDataProvider()
        self.graph = build_research_graph(provider)

    async def research(self, request: ResearchRequest) -> ResearchReport:
        state = await self.graph.ainvoke({"request": request, "errors": []})
        report = cast(ResearchReport, state["report"])
        errors = validate_report(report)
        if errors:
            raise ValueError("Report failed evidence validation: " + "; ".join(errors))
        return report
