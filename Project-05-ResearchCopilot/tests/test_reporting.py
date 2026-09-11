from research_copilot.models import ClaimType, ReportClaim
from research_copilot.reporting import REPORT_SECTIONS, render_claims, report_template


def test_report_template_contains_required_sections():
    report = report_template("Volatility research")
    assert all(f"## {section}" in report for section in REPORT_SECTIONS)


def test_claim_rendering_separates_observation_from_interpretation():
    output = render_claims(
        [
            ReportClaim(text="QLIKE fell by 2%.", claim_type=ClaimType.OBSERVED, evidence_ids=["run-1"]),
            ReportClaim(text="The feature may contain information.", claim_type=ClaimType.INTERPRETATION),
        ]
    )
    assert "Observed Empirical Result" in output
    assert "Ai Interpretation" in output
    assert "run-1" in output

