from abc import ABC, abstractmethod
from datetime import date, timedelta

from pydantic import HttpUrl, TypeAdapter

from fin_research.models.domain import Citation, Metric

HTTP_URL_ADAPTER = TypeAdapter(HttpUrl)


class ResearchDataProvider(ABC):
    """Boundary between research logic and changing third-party APIs."""

    @abstractmethod
    async def company_metrics(self, ticker: str) -> tuple[list[Metric], list[Citation]]: ...

    @abstractmethod
    async def filing_facts(self, ticker: str) -> tuple[list[str], list[Citation]]: ...

    @abstractmethod
    async def macro_metrics(self) -> tuple[list[Metric], list[Citation]]: ...

    @abstractmethod
    async def news_events(self, ticker: str) -> tuple[list[str], list[Citation]]: ...

    @abstractmethod
    async def price_history(self, ticker: str) -> list[dict[str, float | date]]: ...


class DemoDataProvider(ResearchDataProvider):
    """Synthetic, explicitly labeled data for local development—not investment research."""

    def _citation(self, identifier: str, name: str, url: str) -> Citation:
        return Citation(
            id=identifier,
            source_name=f"DEMO: {name}",
            source_url=HTTP_URL_ADAPTER.validate_python(url),
            document_date=date(2025, 1, 1),
            excerpt="Synthetic fixture used to exercise the research pipeline.",
        )

    async def company_metrics(self, ticker: str) -> tuple[list[Metric], list[Citation]]:
        citation = self._citation("demo-fundamentals", "Fundamentals", "https://example.com/demo")
        metrics = [
            Metric(name="revenue_growth_yoy", value=0.12, unit="ratio", citation_ids=[citation.id]),
            Metric(name="gross_margin", value=0.48, unit="ratio", citation_ids=[citation.id]),
            Metric(
                name="free_cash_flow", value=1_250_000_000, unit="USD", citation_ids=[citation.id]
            ),
            Metric(name="debt_to_equity", value=0.31, unit="ratio", citation_ids=[citation.id]),
        ]
        return metrics, [citation]

    async def filing_facts(self, ticker: str) -> tuple[list[str], list[Citation]]:
        citation = self._citation("demo-sec", "SEC filing", "https://www.sec.gov/edgar/search/")
        return ["The synthetic filing fixture identifies supply concentration as a risk."], [
            citation
        ]

    async def macro_metrics(self) -> tuple[list[Metric], list[Citation]]:
        citation = self._citation("demo-fred", "FRED", "https://fred.stlouisfed.org/")
        return [
            Metric(name="policy_rate", value=0.045, unit="ratio", citation_ids=[citation.id]),
            Metric(name="cpi_yoy", value=0.028, unit="ratio", citation_ids=[citation.id]),
            Metric(name="unemployment", value=0.041, unit="ratio", citation_ids=[citation.id]),
        ], [citation]

    async def news_events(self, ticker: str) -> tuple[list[str], list[Citation]]:
        citation = self._citation("demo-news", "News fixture", "https://example.com/demo-news")
        return ["A synthetic product-launch event was recorded for pipeline testing."], [citation]

    async def price_history(self, ticker: str) -> list[dict[str, float | date]]:
        start = date(2024, 1, 1)
        rows: list[dict[str, float | date]] = []
        for index in range(260):
            close = 100.0 + index * 0.08 + (index % 9 - 4) * 0.35
            rows.append(
                {
                    "date": start + timedelta(days=index),
                    "close": close,
                    "volume": float(1_000_000 + (index % 20) * 25_000),
                }
            )
        return rows


class LiveDataProvider(ResearchDataProvider):
    """Fail closed until each source adapter is configured and verified."""

    _message = "Live adapters are intentionally not implemented in the base outline"

    async def company_metrics(self, ticker: str) -> tuple[list[Metric], list[Citation]]:
        raise NotImplementedError(self._message)

    async def filing_facts(self, ticker: str) -> tuple[list[str], list[Citation]]:
        raise NotImplementedError(self._message)

    async def macro_metrics(self) -> tuple[list[Metric], list[Citation]]:
        raise NotImplementedError(self._message)

    async def news_events(self, ticker: str) -> tuple[list[str], list[Citation]]:
        raise NotImplementedError(self._message)

    async def price_history(self, ticker: str) -> list[dict[str, float | date]]:
        raise NotImplementedError(self._message)
