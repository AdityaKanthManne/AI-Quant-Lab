from fin_research.models.domain import ClaimKind, ResearchReport
from fin_research.services.guardrails import validate_report


def evaluate_report(report: ResearchReport) -> dict[str, float]:
    sections = [
        report.recent_sec_developments,
        report.macro_environment,
        report.recent_events,
        report.quantitative_signals,
    ]
    claims = [
        *report.bull_thesis,
        *report.bear_thesis,
        *report.catalysts,
        *report.risks,
        *(claim for section in sections for claim in section.claims),
    ]
    facts = [claim for claim in claims if claim.kind == ClaimKind.FACT]
    cited_facts = [claim for claim in facts if claim.citation_ids]
    citation_accuracy = len(cited_facts) / len(facts) if facts else 1.0
    completeness = sum(section.status != "unavailable" for section in sections) / len(sections)
    guardrail_errors = validate_report(report)
    hallucination_rate = min(1.0, len(guardrail_errors) / max(1, len(claims)))
    return {
        "citation_accuracy": citation_accuracy,
        "factual_consistency": 1.0 - hallucination_rate,
        "retrieval_relevance": 1.0,  # populated by human/LLM judge in the full implementation
        "response_completeness": completeness,
        "hallucination_rate": hallucination_rate,
    }

