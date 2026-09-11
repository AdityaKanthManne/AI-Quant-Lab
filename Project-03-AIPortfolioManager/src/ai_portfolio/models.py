from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from .domain import Forecast
from .features import momentum


class ForecastModel(ABC):
    """Common contract for baselines and future ML models."""

    @abstractmethod
    def fit_predict(self, assets: tuple[str, ...], returns: np.ndarray) -> Forecast:
        raise NotImplementedError


class HistoricalMeanModel(ForecastModel):
    def __init__(self, annualization: int = 252) -> None:
        self.annualization = annualization

    def fit_predict(self, assets: tuple[str, ...], returns: np.ndarray) -> Forecast:
        mu = np.mean(returns, axis=0) * self.annualization
        covariance = np.cov(returns, rowvar=False) * self.annualization
        return Forecast(assets, mu, covariance, signals={"historical_mean": float(mu.mean())})


class MomentumBlendModel(ForecastModel):
    """Shrink noisy momentum toward the historical mean baseline."""

    def __init__(self, momentum_window: int = 63, blend: float = 0.5) -> None:
        if not 0 <= blend <= 1:
            raise ValueError("blend must be in [0, 1]")
        self.momentum_window = momentum_window
        self.blend = blend

    def fit_predict(self, assets: tuple[str, ...], returns: np.ndarray) -> Forecast:
        historical = np.mean(returns, axis=0) * 252
        momentum_forecast = momentum(returns, self.momentum_window) * (252 / self.momentum_window)
        mu = self.blend * momentum_forecast + (1 - self.blend) * historical
        covariance = np.cov(returns, rowvar=False) * 252
        return Forecast(assets, mu, covariance, signals={"mean_momentum": float(mu.mean())})
