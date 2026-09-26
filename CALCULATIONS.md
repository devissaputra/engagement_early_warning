# Calculation guide

## Question and evidence

What support signal was available at the prediction date?

Synthetic dated activity, task and assessment histories with future outcome windows.

**Status:** SYNTHETIC / RULE-BASED PROTOTYPE | no educational validity claim.

## Design

Build cutoff-safe features; apply explicit synthetic coefficients; evaluate review capacity, lead time, calibration and subgroup diagnostics.

## Calculation and interpretation

`Risk = 1/(1+exp(-z)); z = intercept + sum(coefficient×available feature).`

The coefficients are authored, not fitted. A probability-shaped score is not necessarily calibrated. Review-budget performance and future outcome windows must remain separate from feature construction.

## Evidence table

Worked example — illustrative, not a measured research result. Full precision below is for traceability, not a claim of measurement precision.

| Quantity | Value | Unit / meaning | JSON path |
|---|---:|---|---|
| sigmoid of zero | 0.5 | unitless | `outputs.sigmoid of zero` |
| Brier: predictions .8,.3; outcomes 1,0 | 0.06499999999999999 | unitless | `outputs.Brier: predictions .8,.3; outcomes 1,0` |

Source: [results/review_examples.json](results/review_examples.json). Values resolve directly from this file when figures are regenerated.

This early-warning prototype enforces a time boundary between evidence available at prediction and outcomes observed later. It exposes synthetic risk coefficients and evaluates a capacity-limited review queue alongside calibration and subgroup diagnostics. The code demonstrates leakage guards and support-oriented reporting, while explicitly withholding claims of predictive validity for real learners.

## Verification performed in this review

29 existing unittest checks passed. The bundled demonstration executed successfully in this review.

The figure-generation check verifies agreement between the selected source values and SVGs. It does not validate the raw dataset, fitted model, identification assumptions, or external generalization.

```bash
python scripts/build_review_figures.py
python scripts/build_review_figures.py --check
```

For the explicitly illustrative example:

```bash
python scripts/review_examples.py
```

## Implementation map

Follow these functions to inspect each transformation. Validation helpers and private functions remain visible in the linked modules.

| Function | Purpose / documented behavior |
|---|---|
| [`load_cases`](scripts/run_demo.py#L19) | Inspect the explicit implementation and its callers. |
| [`sigmoid`](src/engagement_early_warning/core.py#L69) | Numerically stable logistic function. |
| [`validate_coefficients`](src/engagement_early_warning/core.py#L79) | Inspect the explicit implementation and its callers. |
| [`construct_time_safe_features`](src/engagement_early_warning/core.py#L147) | Build features using only information available by the prediction cutoff. |
| [`risk_from_features`](src/engagement_early_warning/core.py#L271) | Return a transparent synthetic risk probability and contributions. |
| [`risk_probability`](src/engagement_early_warning/core.py#L306) | Backward-compatible synthetic score for the original four inputs. |
| [`validate_prediction_case`](src/engagement_early_warning/core.py#L330) | Validate timing, prediction, outcome, and optional subgroup metadata. |
| [`calibration_bins`](src/engagement_early_warning/core.py#L422) | Group probabilities into reliability bins. |
| [`brier_score`](src/engagement_early_warning/core.py#L478) | Inspect the explicit implementation and its callers. |
| [`expected_calibration_error`](src/engagement_early_warning/core.py#L498) | Inspect the explicit implementation and its callers. |
| [`review_queue`](src/engagement_early_warning/core.py#L507) | Select highest-risk cases within a human review budget and cooldown. |
| [`evaluate_review_budget`](src/engagement_early_warning/core.py#L594) | Evaluate a capacity-constrained human review queue. |
| [`subgroup_audit`](src/engagement_early_warning/core.py#L693) | Report descriptive group error and calibration diagnostics. |
| [`temporal_holdout`](src/engagement_early_warning/core.py#L782) | Split prediction cases by prediction date without random leakage. |
| [`contribution_explanation`](src/engagement_early_warning/core.py#L813) | Explain a synthetic score using only its actual component contributions. |

## What remains before a stronger research claim

The coefficients are authored, not fitted. A probability-shaped score is not necessarily calibrated. Review-budget performance and future outcome windows must remain separate from feature construction. A successful software test is not validation of a scientific construct. New experiments should state their split unit, comparator, outcome, uncertainty procedure and failure criteria before examining final test results.
