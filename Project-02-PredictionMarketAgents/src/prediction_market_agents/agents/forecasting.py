import math
from dataclasses import dataclass, field
from statistics import pstdev
from typing import ClassVar

import numpy as np

from prediction_market_agents.domain import AgentForecast, Category, Evidence, ForecastQuestion
from prediction_market_agents.math import bayesian_update, log_opinion_pool, sigmoid


class HistoricalAgent:
    name = "historical_base_rate"

    DEFAULTS: ClassVar[dict[Category, float]] = {
        Category.MACRO: 0.35,
        Category.CRYPTO: 0.40,
        Category.POLITICS: 0.50,
        Category.EARNINGS: 0.55,
        Category.OTHER: 0.50,
    }

    def forecast(self, question: ForecastQuestion, evidence: list[Evidence]) -> AgentForecast:
        prior = question.features.get("base_rate", self.DEFAULTS[question.category])
        return AgentForecast(
            agent=self.name,
            probability=prior,
            confidence=0.45 if "base_rate" not in question.features else 0.75,
            rationale="Reference-class prior supplied by features or category-level default.",
            weight=1.0,
            metadata={"prior": prior},
        )


class MacroAgent:
    name = "macro"

    def forecast(
        self, question: ForecastQuestion, evidence: list[Evidence], prior: float
    ) -> AgentForecast:
        macro = [e for e in evidence if e.source in {"fred", "bls", "bea", "federal_reserve"}]
        ratios = [e.likelihood_ratio ** (e.relevance * e.credibility) for e in macro]
        probability = bayesian_update(prior, ratios)
        return AgentForecast(
            agent=self.name,
            probability=probability,
            confidence=min(0.85, 0.35 + 0.08 * len(macro)),
            rationale=f"Applied {len(macro)} macro releases as reliability-weighted likelihood updates.",
            weight=0.9,
        )


class NewsAgent:
    name = "news_event"

    def forecast(
        self, question: ForecastQuestion, evidence: list[Evidence], prior: float
    ) -> AgentForecast:
        ratios = [e.likelihood_ratio ** (e.relevance * e.credibility) for e in evidence]
        probability = bayesian_update(prior, ratios)
        return AgentForecast(
            agent=self.name,
            probability=probability,
            confidence=min(0.8, 0.3 + 0.05 * len(evidence)),
            rationale=f"Updated the prior with {len(evidence)} relevance/credibility-weighted items.",
            weight=0.8,
        )


class StatisticalAgent:
    name = "statistical"

    def forecast(self, question: ForecastQuestion, prior: float) -> AgentForecast:
        intercept = question.features.get("intercept", math.log(prior / (1 - prior)))
        score = intercept + sum(
            value * question.features.get(f"coef_{feature}", 0.0)
            for feature, value in question.features.items()
            if not feature.startswith("coef_") and feature not in {"intercept", "base_rate"}
        )
        probability = sigmoid(score)
        has_coefficients = any(key.startswith("coef_") for key in question.features)
        return AgentForecast(
            agent=self.name,
            probability=probability,
            confidence=0.7 if has_coefficients else 0.3,
            rationale="Logistic baseline over supplied numeric features; falls back to prior without fitted coefficients.",
            weight=1.1 if has_coefficients else 0.5,
            metadata={"linear_score": score},
        )


class SkepticAgent:
    name = "skeptic_critic"

    def critique(self, forecasts: list[AgentForecast], evidence: list[Evidence]) -> AgentForecast:
        raw = float(np.mean([f.probability for f in forecasts]))
        sources = [e.source for e in evidence]
        duplicate_fraction = 0 if not sources else 1 - len(set(sources)) / len(sources)
        extremity = raw - 0.5
        shrinkage = min(0.45, 0.15 + duplicate_fraction * 0.4)
        probability = 0.5 + extremity * (1 - shrinkage)
        return AgentForecast(
            agent=self.name,
            probability=probability,
            confidence=0.6,
            rationale=(
                f"Shrank consensus toward 50% by {shrinkage:.0%}; "
                f"estimated source duplication is {duplicate_fraction:.0%}."
            ),
            weight=0.7,
            metadata={"duplicate_fraction": duplicate_fraction, "shrinkage": shrinkage},
        )


@dataclass
class AgentSuite:
    historical: HistoricalAgent = field(default_factory=HistoricalAgent)
    macro: MacroAgent = field(default_factory=MacroAgent)
    news: NewsAgent = field(default_factory=NewsAgent)
    statistical: StatisticalAgent = field(default_factory=StatisticalAgent)
    skeptic: SkepticAgent = field(default_factory=SkepticAgent)

    def run(self, question: ForecastQuestion, evidence: list[Evidence]) -> list[AgentForecast]:
        base = self.historical.forecast(question, evidence)
        forecasts = [
            base,
            self.macro.forecast(question, evidence, base.probability),
            self.news.forecast(question, evidence, base.probability),
            self.statistical.forecast(question, base.probability),
        ]
        forecasts.append(self.skeptic.critique(forecasts, evidence))
        return forecasts


class ForecastAggregator:
    def aggregate(self, forecasts: list[AgentForecast]) -> tuple[float, float, float, float]:
        probabilities = [f.probability for f in forecasts]
        weights = [f.weight * (0.5 + f.confidence) for f in forecasts]
        probability = log_opinion_pool(probabilities, weights)
        disagreement = pstdev(probabilities) if len(probabilities) > 1 else 0.0
        # A transparent research baseline interval. Replace with conformal intervals once enough outcomes exist.
        half_width = min(0.35, 0.08 + 1.5 * disagreement)
        return (
            probability,
            max(0.0, probability - half_width),
            min(1.0, probability + half_width),
            disagreement,
        )
