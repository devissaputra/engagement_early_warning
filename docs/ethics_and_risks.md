# Ethics, safety, and misuse risks

## Intended use

Engagement Early-Warning System is intended for research and supportive learner review.

It is not a disciplinary system, motivation detector, psychological assessment, admissions tool, or automated decision maker.

## Risk is not identity

A probability describes a model output under a particular course, prediction date, feature definition, and outcome definition.

It does not mean a learner is:

- unmotivated
- incapable
- irresponsible
- certain to fail
- certain to disengage

Language shown to staff and learners should avoid turning a temporary support signal into a personal label.

## Time-safe evidence

Using future information can make a system appear much better than it could be in practice.

Feature construction should therefore preserve what was actually knowable at the prediction cutoff.

Examples:

- future grades must not enter earlier predictions
- tasks not yet due must not become missed-task evidence
- future submissions must not rewrite the state that existed at the cutoff
- data ingestion delays should be documented

Leakage is both a methodological and governance problem because it can create unjustified confidence in a support system.

## Engagement is context dependent

Low LMS activity is not equivalent to disengagement.

A learner may be working:

- offline
- in another platform
- in a group
- through downloaded materials
- under an accessibility accommodation
- in a course that does not require frequent LMS use

Forum participation is especially context dependent and should not be treated as a universal sign of engagement.

## False alarms

A false-positive alert can create:

- unwanted contact
- stigma
- surveillance concerns
- unnecessary workload
- a self-fulfilling expectation of failure

Human reviewers should see why a case was selected and have enough context to dismiss an inappropriate alert.

## Missed support

False negatives matter too.

A system that looks precise because it flags only obvious cases may miss learners who would benefit from support.

Evaluation should therefore report recall and false-negative burden at the actual review capacity.

## Review capacity

The operational threshold should reflect the support team's realistic capacity.

If a system flags more learners than staff can meaningfully review, a nominally high-sensitivity model may not create useful support.

The repository uses a review-budget queue rather than pretending that one universal probability threshold fits every deployment.

## Alert fatigue

Repeated alerts for the same learner can overwhelm staff and create intrusive support experiences.

The baseline includes a simple cooldown.

A real system needs escalation rules, case closure, review outcomes, and a way to override cooldown when circumstances materially change.

## Privacy and data minimization

Early-warning systems can accumulate detailed behavioral traces.

Collect only the data needed for the support question.

Avoid collecting or storing sensitive free text, private messages, health information, disability information, or unrelated browsing data simply because they might improve prediction.

Define:

- data access
- retention
- deletion
- correction
- permitted uses
- whether instructors can see raw traces
- whether data can be reused for grading or discipline

## Fairness and subgroup diagnostics

Overall metrics can hide uneven false alarms, missed support, or miscalibration.

Where lawful and ethically justified, evaluate descriptive error and calibration patterns across relevant groups and contexts.

Do not treat one parity statistic as proof that the system is fair.

Small groups also create privacy and statistical-stability concerns.

## Sensitive attributes

Sensitive attributes should not be added merely to improve prediction.

When such attributes are used for fairness auditing, access and reporting should be tightly controlled and justified by the audit purpose.

## Intervention effects

Once support is delivered, later behavior may change because of the intervention.

That creates a feedback loop.

Future labels and retraining datasets should distinguish natural course progression from outcomes affected by prior alerts and support.

## Excluded uses

Do not use this prototype alone for:

- autonomous grading
- admissions
- discipline
- academic-integrity enforcement
- scholarship removal
- employment decisions
- psychological or medical diagnosis
- covert surveillance
- ranking learners by worth or motivation

## Before real deployment

Document the outcome definition, prediction cutoffs, feature windows, data delays, model-development period, temporal holdout, calibration, review capacity, intervention protocol, alert cooldown, privacy controls, subgroup evaluation, correction/appeal path, and clear rollback criteria.

Affected learners should have meaningful information about how support analytics are used in their learning environment.
