import re

from fin_research.models.domain import Claim, ClaimKind, ResearchReport

NUMBER_PATTERN = re.compile(r"(?:\$|\b)\d[\d,.]*(?:%|\b)")


def validate_claim(claim: Claim, known_citation_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if claim.kind == ClaimKind.FACT and not claim.citation_ids:
        errors.append(f"Uncited factual claim: {claim.text}")
    missing = set(claim.citation_ids) - known_citation_ids
    if missing:
        errors.append(f"Unknown citations {sorted(missing)} in claim: {claim.text}")
    if (
        claim.kind != ClaimKind.FACT
        and NUMBER_PATTERN.search(claim.text)
        and not claim.citation_ids
    ):
        errors.append(f"Untraceable numerical statement: {claim.text}")
    if claim.kind == ClaimKind.FORECAST and not claim.assumptions:
        errors.append(f"Forecast lacks assumptions: {claim.text}")
    return errors


def validate_report(report: ResearchReport) -> list[str]:
    citation_ids = {citation.id for citation in report.citations}
    claims = [*report.bull_thesis, *report.bear_thesis, *report.catalysts, *report.risks]
    for section in (
        report.recent_sec_developments,
        report.macro_environment,
        report.recent_events,
        report.quantitative_signals,
    ):
        claims.extend(section.claims)
    return [error for claim in claims for error in validate_claim(claim, citation_ids)]
