# Data documentation

## Included data

All records in this folder are synthetic.

- `sample.csv` contains 24 prediction-time cases across two prediction dates.
- `history_example.json` contains one small raw-history example used to demonstrate cutoff-safe feature construction.

No real learner, instructor, course, LMS, or institutional record is included.

## Core time boundary

Every prediction must define a **prediction cutoff**.

Features may use only information that was available on or before that date.

The future outcome window must begin strictly after the prediction cutoff.

This is the main leakage boundary in the repository.

## `sample.csv` schema

### Identity and timing

- `learner_id`: synthetic learner id
- `course_id`: synthetic course/context id
- `group`: synthetic evaluation group used only to exercise subgroup diagnostics
- `prediction_week`: prediction checkpoint
- `prediction_cutoff`: last date information may enter the prediction
- `outcome_window_start`
- `outcome_window_end`

### Time-safe synthetic features

- `inactivity_ratio`: inactivity normalized to a declared cap
- `overdue_task_rate`: tasks already due and not submitted by cutoff / tasks due by cutoff
- `activity_drop_ratio`: drop from the previous activity window to the current window
- `recent_activity_ratio`: recent activity relative to the current window length
- `recent_score`: assessment score only when it was available by the cutoff

These features are already normalized for the synthetic evaluation table.

They are not claimed to be universally valid engagement constructs.

### Future outcome

- `future_disengagement`: synthetic binary outcome
- `disengagement_event_on`: date of the synthetic future event for positive cases

The event date must lie inside the future outcome window.

It is used to calculate lead time for selected true-positive alerts.

## Raw history example

`history_example.json` demonstrates the leakage guards.

### Activity events

Only activity events on or before the prediction cutoff are accepted.

An activity event after the cutoff is rejected rather than silently ignored.

### Tasks

A task contributes to the overdue-task rate only if its due date is on or before the prediction cutoff.

A submission made after the cutoff does not erase the fact that the task was overdue at prediction time.

### Assessments

Only assessment scores available on or before the cutoff can enter the feature vector.

A future score is ignored as unavailable rather than used retrospectively.

## Outcome definition

A real study must define disengagement before fitting or evaluating a model.

Possible outcomes include:

- no activity for a stated future interval
- non-submission of a future required assessment
- withdrawal
- failure to return
- another explicitly justified support outcome

These targets are not interchangeable.

The synthetic repository uses a generic binary future-disengagement label only to exercise the software path.

## Review capacity

The baseline assumes that staff cannot review every learner.

Evaluation therefore selects the highest-risk cases up to a declared review budget.

The threshold is an operational consequence of the budget, not a universal risk cutoff.

## Repeated alerts

A learner can be temporarily suppressed from a new alert if they were reviewed recently.

The cooldown exists to demonstrate alert-fatigue control.

A real support process should document whether suppression is appropriate and how urgent changes override it.

## Subgroup diagnostics

The `group` field is synthetic and intentionally generic.

The current subgroup audit reports descriptive error and calibration diagnostics.

It does not prove fairness.

A real study should only evaluate sensitive or protected characteristics when collection and analysis are lawful, ethically justified, privacy-protective, and relevant to identifying harmful disparities.

## Before real data are connected

Document:

- course and learning design
- population
- outcome definition
- prediction checkpoints
- feature windows
- due-date semantics
- assessment-release timing
- data availability delays
- exclusions
- missingness
- platform outages
- temporal split strategy
- intervention/support process
- review capacity
- alert cooldown rules
- subgroup audit plan
- consent or other lawful basis
- retention and access controls

## Do not commit

Do not commit identifiable learner records, private LMS exports, messages, free text, disability/health information, disciplinary information, private grades, audio/video, or proprietary course data.

Keep sensitive data outside Git and use an approved secure environment.
