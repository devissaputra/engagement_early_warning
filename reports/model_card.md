# Analytic system card

## System

Engagement Early-Warning System

## Purpose

Interpretable disengagement risk baseline with transparent features and probability bin calibration review.

## Current maturity

Working research prototype. The bundled example checks the software path with synthetic inputs. It does not establish validity for real learners, instructors, courses, or workplaces.

## Inputs

See `../data/README.md` for the current synthetic schema and the documentation expected before real data are connected.

## Outputs

The current code produces an interpretable disengagement risk probability and calibration bin summaries. These outputs are research signals and should be interpreted with the educational context that produced them.

## Evidence needed before real use

Use temporal holdout data and compare against simple recency or inactivity rules. Report calibration, precision and recall at operational thresholds, lead time, and the consequences of false alarms and misses.

## Main limitation

The current coefficients are illustrative. A risk score must never be treated as a label for motivation, ability, or intent, and it should not trigger punitive action.

## Human oversight

A person must review any output before it can affect a learner, instructor, applicant, or employee.
