from fin_research.evaluation import evaluate_report
from fin_research.models.domain import ResearchRequest
from fin_research.services import ResearchService
from fin_research.services.reporting import render_markdown


async def test_demo_research_is_cited_and_labeled() -> None:
    report = await ResearchService(data_mode="demo").research(ResearchRequest(ticker="AMD"))
    assert report.ticker == "AMD"
    assert report.citations
    assert any("DEMO DATA" in warning for warning in report.warnings)
    assert all(metric.citation_ids for metric in report.quantitative_signals.metrics)
    assert evaluate_report(report)["citation_accuracy"] == 1.0


async def test_markdown_contains_core_sections() -> None:
    report = await ResearchService(data_mode="demo").research(ResearchRequest(ticker="NVDA"))
    markdown = render_markdown(report)
    assert "# Research Report: NVDA" in markdown
    assert "## Bull thesis" in markdown
    assert "## Sources" in markdown
