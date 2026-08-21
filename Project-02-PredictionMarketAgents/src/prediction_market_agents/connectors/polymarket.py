import json
from datetime import UTC, datetime

import httpx

from prediction_market_agents.domain import MarketSnapshot

from .base import MarketConnector


class PolymarketConnector(MarketConnector):
    """Read-only connector for Polymarket's public Gamma/CLOB APIs."""

    name = "polymarket"

    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def snapshot(self, event_id: str) -> MarketSnapshot:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/markets/{event_id}")
            response.raise_for_status()
            market = response.json()
        prices = market.get("outcomePrices", [0.5])
        if isinstance(prices, str):
            prices = json.loads(prices)
        probability = float(prices[0])
        return MarketSnapshot(
            market=self.name,
            market_event_id=str(market.get("id", event_id)),
            probability=probability,
            observed_at=datetime.now(UTC),
            volume=_optional_float(market.get("volume")),
            liquidity=_optional_float(market.get("liquidity")),
            change_24h=_optional_float(market.get("oneDayPriceChange")),
        )

    async def search(self, query: str, limit: int = 10) -> list[MarketSnapshot]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/markets",
                params={"limit": limit, "active": "true", "closed": "false"},
            )
            response.raise_for_status()
            records = response.json()
        matches = [r for r in records if query.lower() in r.get("question", "").lower()]
        result = []
        for market in matches[:limit]:
            prices = market.get("outcomePrices", [0.5])
            if isinstance(prices, str):
                prices = json.loads(prices)
            result.append(
                MarketSnapshot(
                    market=self.name,
                    market_event_id=str(market["id"]),
                    probability=float(prices[0]),
                    volume=_optional_float(market.get("volume")),
                    liquidity=_optional_float(market.get("liquidity")),
                    change_24h=_optional_float(market.get("oneDayPriceChange")),
                )
            )
        return result


def _optional_float(value: object) -> float | None:
    return None if value in (None, "") else float(value)  # type: ignore[arg-type]
