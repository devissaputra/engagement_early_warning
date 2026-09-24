# Research protocol

## Project

Engagement Early-Warning System

## Questions

1. How early can disengagement risk be estimated without leaking future information?
2. Are probabilities calibrated enough to support human review?
3. Do subgroup metrics reveal uneven error burdens?

## Baseline methods

- logistic risk score
- engagement feature inputs
- probability estimates
- calibration bins
- supportive review framing

## Evidence to collect

Start from the current transparent baseline and record every transformation needed to produce an interpretable disengagement risk probability and calibration bin summaries. Keep a clear boundary between synthetic demonstration data and any future empirical dataset.

## Validation

Use temporal holdout data and compare against simple recency or inactivity rules. Report calibration, precision and recall at operational thresholds, lead time, and the consequences of false alarms and misses.

## What counts as a useful result

The next study should fit and validate a model on temporally appropriate data, compare it with simple baselines, and report precision, recall, calibration, and lead time at a realistic instructor review budget.

## Threats to validity

Course design, assessment timing, access constraints, and changes in platform use can create spurious risk signals or distribution shift.
