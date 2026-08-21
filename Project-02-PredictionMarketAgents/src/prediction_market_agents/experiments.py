from enum import StrEnum
from typing import Any

from prediction_market_agents.evaluation import evaluate_rows


class Arm(StrEnum):
    MARKET = "market_alone"
    LLM = "llm_alone"
    STATISTICAL = "statistical_alone"
    MULTI_AGENT = "multi_agent"
    MARKET_AI = "market_plus_ai"


def compare_experiment_arms(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Score comparable experiment arms on the same resolved event set."""
    enriched = []
    for row in rows:
        item = dict(row)
        model = item.get("model_probability")
        market = item.get("market_probability")
        item[Arm.MULTI_AGENT] = model
        item[Arm.MARKET] = market
        item[Arm.MARKET_AI] = None if model is None or market is None else 0.5 * (model + market)
        # LLM/statistical arm probabilities are populated by the full experiment runner.
        enriched.append(item)
    return {arm: evaluate_rows(enriched, arm) for arm in Arm}
