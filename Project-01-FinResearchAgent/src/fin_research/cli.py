import argparse
import asyncio
from pathlib import Path

from fin_research.config import get_settings
from fin_research.models.domain import ResearchRequest
from fin_research.services import ResearchService
from fin_research.services.reporting import render_markdown


async def _run(ticker: str, output_dir: Path) -> None:
    service = ResearchService(get_settings().data_mode)
    report = await service.research(ResearchRequest(ticker=ticker))
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{report.ticker.lower()}-research.md"
    report_path.write_text(render_markdown(report), encoding="utf-8")
    print(report.model_dump_json(indent=2))
    print(f"\nMarkdown report: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run evidence-first equity research")
    parser.add_argument("--ticker", required=True, help="US-listed equity ticker")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    asyncio.run(_run(args.ticker, args.output_dir))
