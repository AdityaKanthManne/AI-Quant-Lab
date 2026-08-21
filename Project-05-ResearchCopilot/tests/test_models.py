import pytest
from pydantic import ValidationError

from research_copilot.models import ExperimentSpec, PaperIdentifier


def test_paper_requires_verifiable_identifier():
    with pytest.raises(ValidationError):
        PaperIdentifier()


def test_experiment_spec_requires_rigorous_fields():
    spec = ExperimentSpec(
        research_question="Do prediction markets forecast short-term equity volatility?",
        hypothesis="Market probability changes improve out-of-sample volatility forecasts.",
        dependent_variable="five-day realized volatility",
        independent_variables=["prediction-market probability change"],
        control_variables=["lagged realized volatility", "VIX"],
        dataset="timestamp-aligned market and equity observations",
        baseline=["HAR-RV"],
        models=["HAR-RV with prediction-market features"],
        evaluation_metrics=["out-of-sample R2", "QLIKE"],
        statistical_tests=["Diebold-Mariano", "block bootstrap confidence interval"],
        split_strategy="walk_forward",
        potential_leakage=["mismatched publication and market timestamps"],
        potential_confounders=["scheduled macroeconomic announcements"],
        robustness_tests=["alternate horizons", "event exclusions"],
    )
    assert spec.split_strategy == "walk_forward"

