from __future__ import annotations

import re
from dataclasses import dataclass

from research_copilot.models import PaperMetadata, ReportClaim


@dataclass(frozen=True)
class EvaluationFinding:
    severity: str
    check: str
    message: str


def evaluate_research_output(papers: list[PaperMetadata], claims: list[ReportClaim]) -> list[EvaluationFinding]:
    findings: list[EvaluationFinding] = []
    known_ids = {str(p.id) for p in papers}
    for paper in papers:
        if not any((paper.identifiers.doi, paper.identifiers.arxiv_id, paper.identifiers.semantic_scholar_id)):
            findings.append(EvaluationFinding("error", "citation_verification", f"Missing identifier: {paper.title}"))
    for claim in claims:
        if not claim.evidence_ids:
            findings.append(EvaluationFinding("warning", "unsupported_conclusion", claim.text))
        for evidence_id in claim.evidence_ids:
            if evidence_id not in known_ids:
                findings.append(EvaluationFinding("error", "unknown_evidence", evidence_id))
        if re.search(r"\b\d+(?:\.\d+)?%\b", claim.text) and not claim.evidence_ids:
            findings.append(EvaluationFinding("error", "numerical_claim", claim.text))
    return findings

