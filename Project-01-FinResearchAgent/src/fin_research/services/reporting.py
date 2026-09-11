from fin_research.models.domain import AgentResult, Claim, Metric, ResearchReport


def _metrics(metrics: list[Metric]) -> list[str]:
    return [f"- {metric.name}: {metric.value} {metric.unit}" for metric in metrics] or [
        "- Unavailable"
    ]


def _claims(claims: list[Claim]) -> list[str]:
    return [
        f"- {claim.text} _({claim.kind.value}; sources: {', '.join(claim.citation_ids) or 'none'})_"
        for claim in claims
    ] or ["- Unavailable"]


def _agent_section(title: str, result: AgentResult) -> list[str]:
    return [
        f"## {title}",
        "",
        result.summary,
        "",
        *_metrics(result.metrics),
        *_claims(result.claims),
        "",
    ]


def render_markdown(report: ResearchReport) -> str:
    lines = [
        f"# Research Report: {report.ticker}",
        "",
        f"Generated: {report.generated_at.isoformat()}",
        f"Status: {report.status} | Confidence: {report.model_confidence:.0%}",
        "",
        "> Research output, not investment advice. Verify primary sources before acting.",
        "",
        "## Company overview",
        "",
        report.company_overview,
        "",
        "## Key financial metrics",
        "",
        *_metrics(report.key_financial_metrics),
        "",
        *_agent_section("Recent SEC developments", report.recent_sec_developments),
        *_agent_section("Macro environment", report.macro_environment),
        *_agent_section("Recent events", report.recent_events),
        *_agent_section("Quantitative signals", report.quantitative_signals),
        "## Bull thesis",
        "",
        *_claims(report.bull_thesis),
        "",
        "## Bear thesis",
        "",
        *_claims(report.bear_thesis),
        "",
        "## Catalysts",
        "",
        *_claims(report.catalysts),
        "",
        "## Risks",
        "",
        *_claims(report.risks),
        "",
        "## Sources",
        "",
        *[
            f"- [{citation.id}] [{citation.source_name}]({citation.source_url})"
            for citation in report.citations
        ],
        "",
    ]
    if report.warnings:
        lines.extend(["## Warnings", "", *[f"- {warning}" for warning in report.warnings], ""])
    return "\n".join(lines)
