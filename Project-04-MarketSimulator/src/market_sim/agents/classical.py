"""Reference strategies; intentionally simple enough to audit."""

from market_sim.agents.base import Agent
from market_sim.core.types import BookSnapshot, OrderRequest, Side


class NoiseTrader(Agent):
    def act(self, snapshot: BookSnapshot, timestamp: int) -> list[OrderRequest]:
        side = Side.BUY if self.rng.random() < 0.5 else Side.SELL
        center = snapshot.last_trade or 5_000
        price = int(min(9_999, max(1, center + self.rng.integers(-150, 151))))
        return [OrderRequest(self.agent_id, side, 1, price=price)]


class InformedTrader(Agent):
    def act(self, snapshot: BookSnapshot, timestamp: int) -> list[OrderRequest]:
        fair = int(round(self.state.belief * 10_000))
        if snapshot.best_ask is not None and fair > snapshot.best_ask:
            return [OrderRequest(self.agent_id, Side.BUY, 1, price=snapshot.best_ask)]
        if snapshot.best_bid is not None and fair < snapshot.best_bid:
            return [OrderRequest(self.agent_id, Side.SELL, 1, price=snapshot.best_bid)]
        return []

