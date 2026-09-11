from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class PointInTimeRecord:
    """A datum may be used only when ``available_at`` is no later than decision time."""

    event_time: datetime
    published_at: datetime
    available_at: datetime
    source: str
    values: Mapping[str, float | str]

    def __post_init__(self) -> None:
        if self.published_at < self.event_time:
            raise ValueError("published_at cannot precede event_time")
        if self.available_at < self.published_at:
            raise ValueError("available_at cannot precede published_at")


@dataclass(frozen=True)
class Forecast:
    assets: tuple[str, ...]
    expected_returns: np.ndarray
    covariance: np.ndarray
    regime: str = "unknown"
    signals: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        n = len(self.assets)
        if self.expected_returns.shape != (n,):
            raise ValueError("expected_returns shape must match assets")
        if self.covariance.shape != (n, n):
            raise ValueError("covariance shape must be square and match assets")


@dataclass(frozen=True)
class Scenario:
    name: str
    probability: float
    return_shocks: Mapping[str, float]
    volatility_multipliers: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0 <= self.probability <= 1:
            raise ValueError("probability must be in [0, 1]")


@dataclass(frozen=True)
class Allocation:
    assets: tuple[str, ...]
    weights: np.ndarray
    method: str
    warnings: tuple[str, ...] = ()

