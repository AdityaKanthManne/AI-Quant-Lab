from fin_research.models.domain import AgentResult, Claim, ClaimKind, ResearchReport
from fin_research.models.state import ResearchState


class SupervisorAgent:
    """Synthesizes cited agent outputs; replace heuristics with a grounded LLM later."""

    def run(self, state: ResearchState) -> ResearchReport:
        request = state["request"]
        fundamentals = state["fundamentals"]
        filings = state["filings"]
        macro = state["macro"]
        news = state["news"]
        quant = state["quant"]
        sections = [fundamentals, filings, macro, news, quant]
        citations = self._unique_citations(sections)
        citation_ids = [citation.id for citation in citations]
        warnings = [warning for section in sections for warning in section.warnings]
        is_demo = any(citation.source_name.startswith("DEMO:") for citation in citations)
        if is_demo:
            warnings.insert(0, "DEMO DATA: output is synthetic and must not be used for investment decisions.")

        available = sum(section.status != "unavailable" for section in sections)
        confidence = round(available / len(sections) * (0.55 if is_demo else 0.9), 2)
        supporting = citation_ids[:2]
        return ResearchReport(
            ticker=request.ticker,
            status="complete" if available == len(sections) else "partial",
            company_overview=f"Evidence-backed research outline for {request.ticker}.",
            key_financial_metrics=fundamentals.metrics,
            recent_sec_developments=filings,
            macro_environment=macro,
            recent_events=news,
            quantitative_signals=quant,
            bull_thesis=[
                Claim(
                    text="Growth and cash generation may support the constructive case.",
                    kind=ClaimKind.INTERPRETATION,
                    citation_ids=supporting,
                )
            ],
            bear_thesis=[
                Claim(
                    text="Disclosure and macro risks may weaken the investment case.",
                    kind=ClaimKind.INTERPRETATION,
                    citation_ids=citation_ids[1:3],
                )
            ],
            catalysts=[
                Claim(
                    text="New verified corporate events could act as catalysts.",
                    kind=ClaimKind.INTERPRETATION,
                    citation_ids=citation_ids[-1:],
                )
            ],
            risks=filings.claims,
            model_confidence=confidence,
            citations=citations,
            warnings=warnings,
        )

    @staticmethod
    def _unique_citations(sections: list[AgentResult]):
        citations = {}
        for section in sections:
            citations.update({citation.id: citation for citation in section.citations})
        return list(citations.values())

