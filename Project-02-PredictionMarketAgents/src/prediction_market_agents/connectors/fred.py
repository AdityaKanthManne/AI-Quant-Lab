from datetime import UTC, datetime

import httpx

from prediction_market_agents.domain import Direction, Evidence, ForecastQuestion

from .base import EvidenceConnector


class FredConnector(EvidenceConnector):
    name = "fred"

    def __init__(self, api_key: str | None, timeout: float = 15.0) -> None:
        self.api_key = api_key
        self.timeout = timeout

    async def retrieve(self, question: ForecastQuestion, limit: int = 10) -> list[Evidence]:
        if not self.api_key:
            return []
        series = _series_for_question(question.question)
        evidence: list[Evidence] = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for series_id in series[:limit]:
                response = await client.get(
                    "https://api.stlouisfed.org/fred/series/observations",
                    params={
                        "series_id": series_id,
                        "api_key": self.api_key,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 2,
                    },
                )
                response.raise_for_status()
                observations = [x for x in response.json()["observations"] if x["value"] != "."]
                if not observations:
                    continue
                latest = observations[0]
                evidence.append(
                    Evidence(
                        source=self.name,
                        title=f"FRED {series_id}: {latest['value']}",
                        url=f"https://fred.stlouisfed.org/series/{series_id}",
                        published_at=datetime.fromisoformat(latest["date"]).replace(tzinfo=UTC),
                        summary=f"Latest {series_id} observation is {latest['value']}.",
                        relevance=0.85,
                        credibility=0.98,
                        direction=Direction.NEUTRAL,
                        metadata={"series_id": series_id, "value": float(latest["value"])},
                    )
                )
        return evidence


def _series_for_question(question: str) -> list[str]:
    q = question.lower()
    series: list[str] = []
    if any(word in q for word in ("fed", "rate", "fomc")):
        series += ["FEDFUNDS", "DGS2", "UNRATE", "CPIAUCSL"]
    if any(word in q for word in ("cpi", "inflation")):
        series += ["CPIAUCSL", "CPILFESL", "PCEPI"]
    if any(word in q for word in ("recession", "gdp")):
        series += ["GDPC1", "T10Y2Y", "UNRATE"]
    return list(dict.fromkeys(series))
