from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_UNIVERSE = ("SPY", "QQQ", "TLT", "GLD", "BTC", "NVDA", "AMD", "META")


@dataclass(frozen=True)
class RiskConstraints:
    """Portfolio limits applied after every allocation decision."""

    long_only: bool = True
    max_asset_weight: float = 0.35
    max_turnover: float = 0.50
    target_volatility: float | None = 0.15
    cvar_limit: float | None = 0.04

    def __post_init__(self) -> None:
        if not 0 < self.max_asset_weight <= 1:
            raise ValueError("max_asset_weight must be in (0, 1]")
        if not 0 <= self.max_turnover <= 2:
            raise ValueError("max_turnover must be in [0, 2]")


@dataclass(frozen=True)
class BacktestConfig:
    universe: tuple[str, ...] = DEFAULT_UNIVERSE
    lookback_days: int = 252
    rebalance_every: int = 21
    annualization: int = 252
    transaction_cost_bps: float = 5.0
    risk_free_rate: float = 0.02
    constraints: RiskConstraints = field(default_factory=RiskConstraints)
