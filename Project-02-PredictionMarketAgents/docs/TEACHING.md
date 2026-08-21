# Learning path and quizzes

## Module 1 — Probabilities, odds, and Bayes

A probability is bounded between zero and one. Odds are `p / (1-p)`. Bayes' rule is easiest to audit in odds form:

`posterior odds = prior odds × likelihood ratio`.

The implementation in `math.py` uses log-odds, turning multiplication into addition and avoiding numerical instability.

**Quiz**

1. A prior is 25% and new evidence has likelihood ratio 3. What is the posterior?
2. Why is “this source sounds credible” not enough to assign a likelihood ratio?
3. What goes wrong if two articles repeat the same underlying report and are treated as independent?

Answers: (1) prior odds are 1:3, so posterior odds are 1:1 and probability is 50%; (2) a likelihood ratio compares how expected the evidence is under Yes versus No; (3) the evidence is double-counted and the forecast becomes overconfident.

## Module 2 — Proper scoring and calibration

Brier score is squared probability error. Log loss punishes confident errors much more strongly. Calibration asks whether events forecast at 70% occur about 70% of the time. Sharpness measures decisiveness; it is useful only when calibration is retained. Resolution measures whether forecasts separate events with different empirical outcome rates.

**Quiz**

1. Which is better: a Brier score of 0.12 or 0.20?
2. Can a forecaster be calibrated but useless?
3. Why must model versions and forecast timestamps be stored?

Answers: (1) 0.12; (2) yes—always predicting the unconditional base rate may be calibrated but have no resolution; (3) to prevent look-ahead leakage and reproduce out-of-sample evaluation.

## Module 3 — Multi-agent aggregation

Agents should contribute distinct information, not distinct prose. The aggregator pools log-odds using confidence-adjusted weights. The critic estimates duplicate-source risk and shrinks excessive certainty. Agent dispersion expands the initial uncertainty interval.

**Quiz**

1. Why might five news agents be worse than one news agent plus one base-rate model?
2. Why should weights be learned only on past, resolved events?
3. Is disagreement the same as uncertainty?

Answers: (1) correlated evidence creates an illusion of independent confirmation; (2) fitting on current outcomes leaks future information; (3) no—agents may agree and all be wrong, so disagreement is only one uncertainty component.

## Module 4 — Research design

Every experimental arm must forecast the same event universe at the same cutoff time. Use walk-forward validation, freeze prompts/models, and compare paired proper scores. Report confidence intervals and category/time-period slices. Market prices should be sampled at the same timestamp as model evidence.

**Quiz**

1. Why is comparing a 9 a.m. model forecast with a closing market price unfair?
2. What is survivorship bias in this project?
3. What evidence would support the claim that multi-agent AI beats markets?

Answers: (1) the market has later information; (2) evaluating only events/connectors that remained easy to resolve; (3) lower out-of-sample paired proper scores across a preregistered event set, with uncertainty estimates and robustness checks.

