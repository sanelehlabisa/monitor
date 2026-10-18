# Task 051: Forecast research workspace

## Aim

Generate synthetic meter data and initial graph images outside the live app.

## Clarifications

- Location: software/backend/research/forecasting/.
- Use Matplotlib for saved images, not dependency-free SVG.
- Start with dataset generation and initial plots; app adoption remains later.

## Change

- Add small generation and plotting scripts, a research README and one documented
  run workflow. Save data and PNGs under forecasting/out/, ignored by Git.
- Create reproducible distinct-meter examples with UTC times, top-ups and
  daily/weekly/irregular readings. Keep observed records separate from hidden truth.
- Plot balances/top-ups and adjusted cumulative consumption, clearly distinguishing
  observations, inferred segments and synthetic truth. Do not silently repair data.
- Isolate Matplotlib in research requirements/a local environment; use headless
  rendering. Keep backend runtime requirements, Dockerfile and app imports unchanged.
- Exclude research from the backend Docker build context and keep research checks
  out of normal backend test discovery. Preserve uncommitted Task 050 work.
- Update relevant READMEs, context and changes.md. This is an initial slice of
  66.1/66.2; record remaining acceptance work rather than declaring them complete.
- Allow up to 250 changed implementation lines as a review-size exception for
  the separate generator and plotting modules; tests/docs/output are excluded.

## Reuse

- Ticket 66's kWh/UTC, top-up-boundary and observation/truth contracts.
- Python standard library for data generation/checks; Matplotlib for images only.

## Verify

- Run generation/plotting and isolated checks: seeded data reproducibility,
  energy conservation, meter isolation and hand-calculated consumption.
- Inspect generated PNGs and labels; require valid images, not cross-platform
  byte-identical PNGs. Check Git/build exclusions and git diff --check.

## Out of scope

- Candidate forecasting algorithms, backtests, app integration, live default-rate
  changes, real/demo data, database/API/UI changes, ML/hardware/OCR, siblings,
  commits and pushes.
