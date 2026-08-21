from dataclasses import dataclass

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class StatisticalBaseline:
    """Calibrated logistic baseline; time-based splits should be supplied by the experiment runner."""

    model: Pipeline | None = None

    def fit(self, features: np.ndarray, outcomes: np.ndarray) -> "StatisticalBaseline":
        if len(np.unique(outcomes)) < 2:
            raise ValueError("training outcomes must contain both classes")
        base = Pipeline(
            [
                ("scale", StandardScaler()),
                ("logistic", LogisticRegression(max_iter=2_000, class_weight="balanced")),
            ]
        )
        self.model = Pipeline(
            [("calibrated", CalibratedClassifierCV(base, method="sigmoid", cv=3))]
        )
        self.model.fit(features, outcomes)
        return self

    def predict_probability(self, features: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("fit must be called before prediction")
        return self.model.predict_proba(features)[:, 1]
