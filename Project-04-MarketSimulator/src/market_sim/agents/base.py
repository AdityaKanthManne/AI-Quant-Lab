"""Agent protocol and state containers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from market_sim.core.types import BookSnapshot, OrderRequest, Trade


@dataclass(slots=True)
class AgentState:
    cash: int
    inventory: int = 0
    belief: float = 0.5
    risk_tolerance: float = 0.5
    realized_pnl: int = 0
    memory: list[dict[str, Any]] = field(default_factory=list)


class Agent(ABC):
    """Strategies only emit intents; the exchange owns execution."""

    def __init__(self, agent_id: str, state: AgentState, seed: int) -> None:
        self.agent_id = agent_id
        self.state = state
        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def act(self, snapshot: BookSnapshot, timestamp: int) -> list[OrderRequest]:
        """Return zero or more orders based only on observable state."""

    def on_trade(self, trade: Trade) -> None:
        self.state.memory.append({"kind": "trade", "trade": trade})

