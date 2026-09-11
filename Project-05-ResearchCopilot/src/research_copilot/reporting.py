from __future__ import annotations

from collections import defaultdict

from research_copilot.models import ClaimType, ReportClaim

REPORT_SECTIONS = (
    "Abstract",
    "Research question",
    "Literature review",
    "Hypothesis",
    "Data",
    "Methodology",
    "Results",
    "Robustness tests",
    "Limitations",
    "Future research",
)


def render_claims(claims: list[ReportClaim]) -> str:
    """Render claims under labels that prevent interpretation from masquerading as evidence."""
    grouped: dict[ClaimType, list[ReportClaim]] = defaultdict(list)
    for claim in claims:
        grouped[claim.claim_type].append(claim)

    blocks: list[str] = []
    for claim_type in ClaimType:
        blocks.append(f"### {claim_type.value.replace('_', ' ').title()}")
        selected = grouped[claim_type]
        if not selected:
            blocks.append("No claims recorded.")
            continue
        for claim in selected:
            evidence = ", ".join(claim.evidence_ids) or "no linked evidence"
            blocks.append(f"- {claim.text} ({evidence})")
    return "\n\n".join(blocks)


def report_template(title: str) -> str:
    sections = "\n\n".join(f"## {section}\n\n_TBD_" for section in REPORT_SECTIONS)
    return f"# {title}\n\n{sections}\n"

