# Research protocol

## Project

Engagement Early-Warning System

## Research questions

1. How early can future disengagement be identified using only information available at a declared prediction cutoff?
2. How well calibrated are the resulting probabilities on a temporally later evaluation set?
3. What precision, recall, and lead time are achieved under a realistic human review budget?
4. Which false alarms and missed-support cases appear at that operational budget?
5. Do descriptive error and calibration diagnostics differ across relevant learner groups or contexts?
6. How often would repeat alerts occur, and what cooldown or escalation process is appropriate?

## Core design rule: time safety

The prediction cutoff is the boundary between evidence and outcome.

Features may use information available on or before the cutoff.

The outcome window begins strictly after the cutoff.

This means, for example:

- an activity event after the cutoff is future information
- a task not yet due cannot be counted as overdue
- an assessment score unavailable at the cutoff cannot be used retrospectively
- a later disengagement event belongs to the outcome window, not the feature vector

The implementation rejects future activity events and validates outcome timing.

## Current synthetic score

The repository uses a transparent hand-authored logistic score with normalized features:

- inactivity ratio
- overdue-task rate
- activity-drop ratio
- recent-activity ratio
- recent assessment score when available

The coefficients are synthetic.

They are not fitted from learner data and should not be interpreted as empirically calibrated effects.

The score exists to exercise the early-warning evaluation pipeline.

## Time-safe feature construction

`construct_time_safe_features()` accepts raw dated activity events, task due/submission dates, dated assessment availability, and a prediction cutoff.

It constructs:

- inactive days and normalized inactivity
- tasks due by the cutoff
- tasks overdue at the cutoff
- recent activity count
- previous-window activity count
- activity-drop ratio
- recent-activity ratio
- latest assessment score actually available by the cutoff

A future assessment remains unavailable even if its eventual score is known in the stored synthetic record.

## Outcome definition

A real study must predefine the support outcome.

Possible outcomes include:

- no activity for a stated future interval
- withdrawal
- non-submission of a future required assessment
- failure to return
- another justified future support need

These outcomes are not interchangeable.

The synthetic dataset uses a generic `future_disengagement` label only to test the software path.

Positive synthetic cases also include an event date so lead time can be calculated.

## Temporal evaluation

Random train/test splits can mix earlier and later course states in ways that do not match deployment.

The repository therefore includes `temporal_holdout()`, which separates prediction cases by prediction date.

For a fitted empirical model, model fitting and any calibration procedure should be completed on earlier data before evaluating on a later holdout period.

## Calibration

The current baseline implements:

- reliability/calibration bins
- Brier score
- expected calibration error

These are descriptive diagnostics.

The repository does not fit a calibration model such as Platt scaling or isotonic regression.

The phrase “calibrated model” should only be used after a proper held-out calibration procedure.

## Review-capacity threshold

A support team may be able to review only a limited number of learners.

`review_queue()` therefore selects the highest-risk eligible cases up to a declared review budget.

The resulting threshold is operational and cohort-dependent.

It is not a universal statement that everyone above a fixed probability is “at risk.”

## Early-warning metrics

`evaluate_review_budget()` reports:

- selected count
- operational threshold
- true positives
- false positives
- false negatives
- true negatives
- precision
- recall
- false-positive rate
- false-negative rate
- lead time for selected true-positive cases
- Brier score
- expected calibration error
- calibration bins

A useful early-warning system needs both predictive quality and enough lead time for support to be meaningful.

## Repeated alerts

The review queue accepts prior alert dates and a cooldown period.

This is a simple alert-fatigue control.

A real intervention protocol should also define:

- what happens after a review
- when a risk change warrants re-alerting
- how urgent concerns override cooldown
- whether repeated non-response changes the support strategy

## Subgroup audit

The current `subgroup_audit()` reports descriptive per-group:

- prevalence
- selected fraction
- precision
- recall
- false-positive rate
- false-negative rate
- Brier score
- expected calibration error

These metrics do not prove fairness.

They are diagnostics for locating differences that require contextual investigation.

A real study should justify which groups are examined and protect privacy, especially for small groups.

## Baselines for an empirical study

A fitted model should be compared with simple operational baselines such as:

- days-since-last-activity rule
- overdue-task rule
- prior-performance rule where timing permits
- random review within the same capacity
- simple transparent logistic model

The point is to show that additional complexity improves a real support decision rather than merely increasing model sophistication.

## Intervention evaluation

Prediction accuracy is not the same as intervention effectiveness.

If the research question becomes “does early outreach help?”, the evaluation needs an appropriate intervention design.

Do not infer causal benefit from the fact that selected learners later improve.

## Threats to validity

Major threats include:

- future-information leakage
- ambiguous disengagement definitions
- due-date changes
- delayed LMS event ingestion
- platform outages
- course redesign
- activity occurring outside the LMS
- low forum use in otherwise engaged learners
- accessibility or connectivity constraints
- missing assessment data
- changing instructor practices
- distribution shift across courses or terms
- small subgroup sizes
- intervention effects contaminating later labels
- alert fatigue
- self-fulfilling labels

The output should remain a support signal for human review, never a statement about motivation, ability, or intent.
