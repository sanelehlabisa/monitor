# Task 050: Per-meter forecast research plan

## Result

Documentation-only planning; zero changed implementation lines. Preserved Ticket
66 as the parent and added five stable, ordered subtickets:

- 66.1: reproducible distinct-meter datasets with daily/weekly/irregular manual
  records, separate hidden truth and hand-checked examples.
- 66.2: top-up-adjusted cumulative consumption and labelled offline plots.
- 66.3: a limited segmented candidate versus the current weighted mean, with
  minimum-support/fallback rules and optional research-only starting defaults.
- 66.4: chronological backtests, correctness checks and an adoption decision.
- 66.5: integration only after positive evidence and fresh approval.

Each has dependencies, outputs and acceptance checks in the backend README.
Updated the root roadmap, software overview and agent context consistently.
The current forecast already uses each meter's own history; no model was replaced.
The live insufficient-data policy remains unchanged. A no-go retains the baseline;
candidate adoption is not needed for deployment if baseline validation passes.
Next work number is 051; propose 66.1 first within forecasting, without treating
these tickets as implementation approval. Usability Ticket 65 remains open.

## Reuse

Existing Ticket 66 requirements, the single run_forecast_model boundary, ledger
contracts, forecast tests/examples and roadmap IDs. Retained the 15 kWh/day
example distinguishing 450 kWh monthly use from 150 kWh extra when 300 remains.

## Verification

- PASS: reviewed current model and dashboard/reminder callers; no runtime edits.
- PASS: each 66.1-66.5 definition occurs once in both root/backend READMEs.
- PASS: independent cross-document review found no ID, sequence or policy blockers.
- PASS: reviewed sequence, sparse-data assumptions, UTC/top-up boundaries,
  reproducibility and scoring/adoption gates. Hidden truth/future records cannot
  train the candidate; unknown future purchases cannot distort run-out scoring.
- PASS: tracked file-scope check allows only the four approved Markdown docs.
  The work directory contains only prompt.md and this changes.md.
- PASS: git diff --check. No application suites rerun: this task changes only
  planning documentation and claims no new accuracy or household validation.

## Boundaries

No generator, dataset, plot, model implementation, dependency, live app/API/DB,
real/demo data, hardware/OCR/ML, costs/payments or sibling changes. No commits or
pushes. All five subtickets remain unimplemented and require their own approval.
