"""Core immutable messages shared across the simulation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


@dataclass(frozen=True, slots=True)
class Contract:
    contract_id: str
    question: str
    expires_at: int
    tick_size: int = 1
    price_scale: int = 10_000

    def validate_price(self, price: int) -> None:
        if not 0 < price < self.price_scale:
            raise ValueError("prediction-market price must be strictly between 0 and 1")
        if price % self.tick_size:
            raise ValueError("price does not lie on the contract tick grid")


@dataclass(frozen=True, slots=True)
class OrderRequest:
    agent_id: str
    side: Side
    quantity: int
    order_type: OrderType = OrderType.LIMIT
    price: int | None = None


@dataclass(slots=True)
class Order:
    order_id: int
    sequence: int
    agent_id: str
    side: Side
    price: int
    quantity: int
    remaining: int
    created_at: int


@dataclass(frozen=True, slots=True)
class Trade:
    trade_id: int
    timestamp: int
    price: int
    quantity: int
    buyer_id: str
    seller_id: str
    maker_order_id: int
    taker_order_id: int


@dataclass(frozen=True, slots=True)
class BookSnapshot:
    timestamp: int
    best_bid: int | None
    best_ask: int | None
    bid_depth: int
    ask_depth: int
    last_trade: int | None

