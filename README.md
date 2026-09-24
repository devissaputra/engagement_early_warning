# Engagement Early-Warning System

> Interpretable disengagement risk baseline with transparent features and probability bin calibration review.

[![CI](https://github.com/devissaputra/engagement-early-warning/actions/workflows/ci.yml/badge.svg)](https://github.com/devissaputra/engagement-early-warning/actions/workflows/ci.yml)

![Engagement Early-Warning System workflow](assets/architecture.svg)

**Area:** Learning Analytics & Multimodal Evidence    
**Status:** working research prototype  
**Author:** Devis Wawan Saputra

## What this project is for

Early warning systems are useful only when their probabilities are trustworthy and their errors are understood. This prototype estimates disengagement risk from explicit engagement features such as inactive days, missed tasks, forum posts, and prior score, then checks calibration instead of treating a raw score as a decision.

**Who may find it useful:** Learning-analytics researchers and student-support teams studying early intervention with human oversight.

## Research questions

1. How early can disengagement risk be estimated without leaking future information?
2. Are probabilities calibrated enough to support human review?
3. Do subgroup metrics reveal uneven error burdens?

## How it works

The baseline converts four explicit engagement features into a logistic risk probability. A separate function groups predictions into probability bins so observed outcomes can be compared with predicted risk. The coefficients are synthetic and are not fitted from learner data.

![Engagement Early-Warning System data and reasoning flow](assets/data_flow.svg)

The implemented path begins with aggregated engagement features, produces a risk score, checks the score by probability bin, and leaves any outreach decision to a human reviewer.

![Synthetic demo snapshot for Engagement Early-Warning System](assets/demo_snapshot.svg)

This snapshot shows the bundled synthetic example for Engagement Early-Warning System. It checks the software path; it is not an empirical performance result.

## Methods in the current baseline

- logistic risk score
- engagement feature inputs
- probability estimates
- calibration bins
- supportive review framing

## Data

Synthetic weekly engagement records are included. No OULAD adapter is bundled in this baseline.

`data/README.md` documents the sample schema and the conditions that should be recorded before any real dataset is connected. Restricted or identifiable learner data should stay outside the repository.

## Run the demo

```bash
git clone https://github.com/devissaputra/engagement-early-warning.git
cd engagement-early-warning
python scripts/run_demo.py
python -m unittest discover -s tests -v
```

The demo contrasts a low risk and a higher risk synthetic learner, then prints the calibration bins formed from those two examples.

## What to evaluate next

The next study should fit and validate a model on temporally appropriate data, compare it with simple baselines, and report precision, recall, calibration, and lead time at a realistic instructor review budget.

## Evaluation view

![Engagement Early-Warning System evaluation dashboard](assets/evaluation_dashboard.svg)

The Engagement Early-Warning System dashboard is an evaluation checklist rather than a result chart. The bars are illustrative only; the labels show the evidence a real study would need to collect.

## Limits and responsible use

The current coefficients are illustrative. A risk score must never be treated as a label for motivation, ability, or intent, and it should not trigger punitive action. See `docs/ethics_and_risks.md` for the broader risk review.

## Repository map

```text
.
├── .github/workflows/ci.yml
├── assets/
│   ├── architecture.svg
│   ├── data_flow.svg
│   ├── demo_snapshot.svg
│   └── evaluation_dashboard.svg
├── data/
│   ├── README.md
│   └── sample.csv
├── docs/
│   ├── ethics_and_risks.md
│   ├── related_work.md
│   └── research_protocol.md
├── reports/model_card.md
├── scripts/run_demo.py
├── src/engagement_early_warning/core.py
├── tests/test_core.py
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── README.md
```

## Research path

A credible next version would:

1. fit a baseline on historical data using only information available at prediction time
2. select review thresholds from a realistic staff capacity
3. audit calibration and error patterns across relevant learner groups

## Related work

`docs/related_work.md` points to open projects that are relevant to this problem area. They are context for comparison and study design; this repository does not present their code as its own.

## Citation and license

`CITATION.cff` contains the software citation. The code and original SVG visuals use the MIT License. Any external dataset keeps its own license and usage conditions.
