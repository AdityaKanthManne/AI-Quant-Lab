"""Clean, deterministic event loop."""

from __future__ import annotations

from dataclasses import dataclass, field

from market_sim.agents.base import Agent
from market_sim.core.types import Trade
from market_sim.market.book import LimitOrderBook


@dataclass(slots=True)
class SimulationResult:
    trades: list[Trade] = field(default_factory=list)
    snapshots: list[object] = field(default_factory=list)


class Simulation:
    def __init__(self, book: LimitOrderBook, agents: list[Agent], horizon: int) -> None:
        self.book = book
        self.agents = agents
        self.horizon = horizon

    def run(self) -> SimulationResult:
        result = SimulationResult()
        for timestamp in range(self.horizon):
            for agent in self.agents:
                snapshot = self.book.snapshot(timestamp)
                for request in agent.act(snapshot, timestamp):
                    _, trades = self.book.submit(request, timestamp)
                    result.trades.extend(trades)
                    for trade in trades:
                        agent.on_trade(trade)
            result.snapshots.append(self.book.snapshot(timestamp))
        return result

