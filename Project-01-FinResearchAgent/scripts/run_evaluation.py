import asyncio
import json
from pathlib import Path

from fin_research.evaluation import evaluate_report
from fin_research.models.domain import ResearchRequest
from fin_research.services import ResearchService


async def main() -> None:
    cases = json.loads(Path("evaluation/sample_queries.json").read_text(encoding="utf-8"))
    service = ResearchService(data_mode="demo")
    for case in cases:
        report = await service.research(ResearchRequest(ticker=case["ticker"]))
        print(case["ticker"], evaluate_report(report))


if __name__ == "__main__":
    asyncio.run(main())
