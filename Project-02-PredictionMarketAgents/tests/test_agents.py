from prediction_market_agents.agents import AgentSuite, ForecastAggregator
from prediction_market_agents.domain import Category, ForecastQuestion


def test_agent_suite_produces_independent_named_forecasts() -> None:
    forecasts = AgentSuite().run(
        ForecastQuestion(
            question="Will the central bank cut rates next month?", category=Category.MACRO
        ),
        [],
    )
    assert {forecast.agent for forecast in forecasts} == {
        "historical_base_rate",
        "macro",
        "news_event",
        "statistical",
        "skeptic_critic",
    }


def test_disagreement_expands_interval() -> None:
    suite = AgentSuite()
    question = ForecastQuestion(question="Will this well-specified event occur before year end?")
    forecasts = suite.run(question, [])
    probability, low, high, disagreement = ForecastAggregator().aggregate(forecasts)
    assert low <= probability <= high
    assert disagreement >= 0
