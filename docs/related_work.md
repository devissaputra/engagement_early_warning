# Related work and methodological context

Engagement Early-Warning System is an original transparent implementation.

It does not reproduce the models or claim the empirical results of the work below.

## Course Signals

Arnold and Pistilli described Course Signals at Purdue as an early-intervention learning-analytics system intended to help instructors identify students who may need support and provide timely feedback.

- Kimberly E. Arnold & Matthew D. Pistilli (2012)
- *Course signals at Purdue: using learning analytics to increase student success*
- LAK 2012, pp. 267–270
- DOI: https://doi.org/10.1145/2330601.2330666

This repository takes from that line of work the basic idea that prediction must connect to a human support process, not simply produce a score.

## Open Academic Analytics Initiative

Jayaprakash and colleagues reported the Open Academic Analytics Initiative, which studied early alerts, portability across institutions, and interventions for academically at-risk students.

- Jayaprakash, S. M., Moody, E. W., Lauría, E. J. M., Regan, J. R., & Baron, J. D. (2014)
- *Early Alert of Academically At-Risk Students: An Open Source Analytics Initiative*
- Journal of Learning Analytics, 1(1), 6–47
- DOI: https://doi.org/10.18608/jla.2014.11.3

That work is relevant to this repository's emphasis on evaluation context, portability, and the distinction between prediction and intervention.

## Time-series behavior

Research on LMS time-series behavior has shown why prediction timing matters: the available behavior sequence changes as a course unfolds.

A practical early-warning evaluation should therefore state the prediction point and ensure later behavior does not leak into earlier predictions.

The current repository implements this principle directly through prediction cutoffs, feature windows, future outcome windows, and a temporal holdout utility.

## Algorithmic bias in education

Baker and Hawn review how algorithmic bias can enter educational systems through data, models, deployment choices, and broader sociotechnical processes.

- Ryan S. Baker & Aaron Hawn (2022)
- *Algorithmic Bias in Education*
- International Journal of Artificial Intelligence in Education, 32, 1052–1092
- DOI: https://doi.org/10.1007/s40593-021-00285-9

This is relevant because early-warning errors do not have equal consequences: false alarms can stigmatize or over-monitor learners, while false negatives can withhold support.

The current code therefore exposes subgroup error and calibration diagnostics as descriptive audits rather than presenting aggregate accuracy as sufficient.

## Calibration and operational review

For a support system, probability quality and operational capacity both matter.

This repository therefore separates:

- probability diagnostics such as Brier score and reliability bins
- the operational review budget
- precision and recall at that budget
- lead time for selected true-positive cases

A probability model can have acceptable ranking while still being poorly calibrated, and a model can have good global metrics while producing an unusable review queue.

## Scope boundary

Implemented:

- prediction-cutoff validation
- time-safe feature construction
- future outcome windows
- transparent synthetic risk coefficients
- component-level score explanation
- calibration bins
- Brier score
- expected calibration error
- review-budget queue
- precision/recall/error diagnostics
- lead-time analysis
- repeat-alert cooldown
- subgroup descriptive audit
- temporal holdout

Not implemented:

- empirical coefficient fitting
- probability recalibration
- causal intervention-effect estimation
- deep sequence models
- embeddings
- automated outreach
- inferred motivation or psychological state
- institution-wide deployment governance

The current repository is a research scaffold for testing the logic of an early-warning evaluation pipeline before any claim of real predictive validity.
