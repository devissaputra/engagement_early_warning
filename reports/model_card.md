# Analytic system card

## System

Engagement Early-Warning System

## Purpose

Time-safe early-warning analytics for supportive human review, with explicit leakage boundaries, calibration diagnostics, review-budget evaluation, lead-time analysis, and subgroup audits.

## Current maturity

Working research prototype.

The coefficients, histories, outcomes, groups, and evaluation results in the repository are synthetic.

The repository demonstrates the software path and evaluation logic.

It does not establish predictive validity for real learners.

## Intended decision

The output is intended to help a support team prioritize cases for human review when review capacity is limited.

It is not intended to decide grading, discipline, admissions, financial support, employment, or learner status.

## Inputs

### Dated source information

The cutoff-safe feature builder accepts:

- activity-event dates
- task due dates
- submission dates
- assessment availability dates
- assessment scores

### Prediction timing

Each evaluated case specifies:

- prediction week
- prediction cutoff
- future outcome-window start
- future outcome-window end

### Synthetic risk features

The transparent baseline uses normalized:

- inactivity
- overdue-task rate
- activity drop
- recent activity
- recent assessment score when available

### Outcome

The synthetic evaluation uses a binary future-disengagement outcome plus an event date for positive cases.

A real deployment must define its outcome precisely.

## Leakage controls

The software:

- rejects activity events after the cutoff
- counts only tasks due by the cutoff
- treats submissions after the cutoff as unavailable at prediction time
- ignores assessment scores not yet available
- requires the outcome window to begin after the prediction cutoff
- requires positive outcome events to occur inside the future outcome window

These checks reduce obvious temporal leakage but do not replace a complete real-data audit.

## Risk model

The current coefficients are hand-authored synthetic values.

The model is intentionally transparent and is not claimed to be fitted, calibrated, or optimal.

Each score exposes its feature values and linear contributions.

## Calibration outputs

The repository implements:

- calibration/reliability bins
- Brier score
- expected calibration error

It does not implement probability recalibration.

A real model should evaluate calibration on data that were not used to fit either the prediction model or a calibration transform.

## Operational review

The review queue ranks synthetic cases by risk and selects up to a declared staff review budget.

The resulting threshold is operational and can change across cohorts.

A cooldown can suppress repeat alerts for learners reviewed recently.

## Early-warning outputs

At a declared review budget the evaluation reports:

- precision
- recall
- false-positive rate
- false-negative rate
- confusion counts
- operational threshold
- lead time for selected true positives
- calibration diagnostics

## Subgroup diagnostics

The descriptive subgroup audit reports selection, error, Brier, and calibration metrics.

These diagnostics do not establish fairness and may be unstable for small groups.

## Temporal validation

`temporal_holdout()` separates earlier prediction cases from later prediction cases.

For a real fitted model, all fitting, tuning, and calibration decisions should be completed without using the later holdout labels.

## Main limitations

The current baseline:

- uses synthetic coefficients rather than learned parameters
- uses a small hand-designed feature set
- assumes source timestamps are accurate
- does not model data-ingestion delays
- does not learn course-specific behavior patterns
- does not handle rich missing-data mechanisms
- does not estimate statistical uncertainty
- does not fit or recalibrate probabilities
- does not evaluate an actual support intervention
- does not model feedback loops after intervention
- does not infer motivation, ability, or intent

## Evidence required before real use

A real study should provide:

- precise future outcome definition
- timestamp/data-availability audit
- pre-specified prediction checkpoints
- temporal development/holdout design
- simple operational baselines
- calibration evaluation
- review-budget evaluation
- lead-time analysis
- intervention protocol
- alert-fatigue analysis
- subgroup diagnostics
- privacy/governance review
- documentation of course and platform changes

## Human oversight

A reviewer should see:

- prediction date
- relevant time-safe features
- score contributions
- recent alert history
- uncertainty/validation limitations
- contextual information not captured by LMS traces

Reviewers must be able to dismiss an alert without treating the model output as evidence of motivation or character.
