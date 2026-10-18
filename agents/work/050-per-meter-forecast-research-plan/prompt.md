# Task 050: Per-meter forecast research plan

## Aim

Plan simple, offline forecasting research in small subtickets before changing the app.

## Clarifications

- Daily, weekly and irregular manual readings, with detailed synthetic usage
  hidden from the forecasting inputs: Yes.
- Optional starting-rate defaults are research-only; the live app keeps
  Not enough data until its existing requirements are met: Yes.
- Use simple mathematics per meter, not pooled user histories or heavy ML.

## Change

- Reuse Ticket 66 as the parent and add five ordered subtickets:
  1. Reproducible example datasets for several distinct meter profiles.
  2. Top-up-adjusted cumulative consumption and clearly labelled plots.
  3. A small segmented-fit candidate compared with the current weighted average.
  4. Chronological backtests, accuracy checks and an evidence-based go/no-go.
  5. Separately approved app integration only if the candidate earns adoption.
- Give each subticket clear outputs, dependencies and acceptance checks.
- Require meter isolation, UTC timestamps, explicit top-up boundaries, sparse-data
  fallbacks and no hidden-truth/future-data leakage. Do not invent hourly readings.
- Define consumption and no-future-purchase comparisons so later purchases do not
  distort evaluation. Distinguish 30-day usage from additional kWh to buy.
- Update the root roadmap, backend/software READMEs, agent context and changes.md.

## Reuse

- Existing Ticket 66, run_forecast_model, ledger contracts and forecast examples.
- The current model already uses each meter's history; preserve it as the baseline.

## Verify

- Review ticket IDs, sequence, reproducibility, validation criteria and adoption gate.
- Run git diff --check and confirm only planning documentation changed.

## Out of scope

- Dataset/model implementation, new dependencies, live app/API/database changes,
  real household data, hardware/OCR/ML, costs/payments, siblings, commits and pushes.
