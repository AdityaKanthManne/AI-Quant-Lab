"""Deterministic price-time-priority limit order book."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import replace

from market_sim.core.types import BookSnapshot, Contract, Order, OrderRequest, OrderType, Side, Trade


class LimitOrderBook:
    """Single-contract continuous double auction using integer price ticks."""

    def __init__(self, contract: Contract) -> None:
        self.contract = contract
        self._orders: dict[int, Order] = {}
        self._levels: dict[Side, dict[int, deque[int]]] = {
            Side.BUY: defaultdict(deque),
            Side.SELL: defaultdict(deque),
        }
        self._next_order_id = 1
        self._next_trade_id = 1
        self._sequence = 1
        self.last_trade: int | None = None

    def submit(self, request: OrderRequest, timestamp: int) -> tuple[Order, list[Trade]]:
        if request.quantity <= 0:
            raise ValueError("quantity must be positive")
        if request.order_type is OrderType.LIMIT:
            if request.price is None:
                raise ValueError("limit orders require a price")
            self.contract.validate_price(request.price)
            price = request.price
        else:
            price = self.contract.price_scale - 1 if request.side is Side.BUY else 1

        order = Order(
            order_id=self._next_order_id,
            sequence=self._sequence,
            agent_id=request.agent_id,
            side=request.side,
            price=price,
            quantity=request.quantity,
            remaining=request.quantity,
            created_at=timestamp,
        )
        self._next_order_id += 1
        self._sequence += 1
        trades = self._match(order, timestamp)
        if order.remaining and request.order_type is OrderType.LIMIT:
            self._orders[order.order_id] = order
            self._levels[order.side][order.price].append(order.order_id)
        return replace(order), trades

    def cancel(self, order_id: int, agent_id: str) -> bool:
        order = self._orders.get(order_id)
        if order is None or order.agent_id != agent_id:
            return False
        del self._orders[order_id]
        return True

    def snapshot(self, timestamp: int) -> BookSnapshot:
        bids = self._active_prices(Side.BUY)
        asks = self._active_prices(Side.SELL)
        return BookSnapshot(
            timestamp=timestamp,
            best_bid=max(bids) if bids else None,
            best_ask=min(asks) if asks else None,
            bid_depth=sum(o.remaining for o in self._orders.values() if o.side is Side.BUY),
            ask_depth=sum(o.remaining for o in self._orders.values() if o.side is Side.SELL),
            last_trade=self.last_trade,
        )

    def _active_prices(self, side: Side) -> list[int]:
        return [p for p, ids in self._levels[side].items() if any(i in self._orders for i in ids)]

    def _best_opposite(self, side: Side) -> int | None:
        prices = self._active_prices(Side.SELL if side is Side.BUY else Side.BUY)
        if not prices:
            return None
        return min(prices) if side is Side.BUY else max(prices)

    def _crosses(self, incoming: Order, opposite_price: int) -> bool:
        return incoming.price >= opposite_price if incoming.side is Side.BUY else incoming.price <= opposite_price

    def _match(self, incoming: Order, timestamp: int) -> list[Trade]:
        trades: list[Trade] = []
        opposite = Side.SELL if incoming.side is Side.BUY else Side.BUY
        while incoming.remaining:
            price = self._best_opposite(incoming.side)
            if price is None or not self._crosses(incoming, price):
                break
            queue = self._levels[opposite][price]
            while queue and queue[0] not in self._orders:
                queue.popleft()
            maker = self._orders[queue[0]]
            quantity = min(incoming.remaining, maker.remaining)
            buyer = incoming.agent_id if incoming.side is Side.BUY else maker.agent_id
            seller = maker.agent_id if incoming.side is Side.BUY else incoming.agent_id
            trades.append(Trade(self._next_trade_id, timestamp, maker.price, quantity, buyer, seller, maker.order_id, incoming.order_id))
            self._next_trade_id += 1
            incoming.remaining -= quantity
            maker.remaining -= quantity
            self.last_trade = maker.price
            if maker.remaining == 0:
                del self._orders[maker.order_id]
                queue.popleft()
        return trades

