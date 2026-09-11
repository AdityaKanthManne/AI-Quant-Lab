from __future__ import annotations

import json
from datetime import UTC, datetime

import numpy as np

from .config import DEFAULT_UNIVERSE
from .models import MomentumBlendModel
from .optimization import inverse_volatility
from .reporting import portfolio_report


def main() -> None:
    rng = np.random.default_rng(42)
    returns = rng.normal(0.00025, 0.012, size=(504, len(DEFAULT_UNIVERSE)))
    forecast = MomentumBlendModel().fit_predict(DEFAULT_UNIVERSE, returns)
    allocation = inverse_volatility(forecast)
    report_date = datetime.now(UTC).date()
    print(json.dumps(portfolio_report(report_date, allocation, forecast, 0.0), indent=2))


if __name__ == "__main__":
    main()
