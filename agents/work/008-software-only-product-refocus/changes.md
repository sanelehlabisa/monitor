# Task 008: Software-only product refocus

## Result

Monitor's active V1 is now documented as a free, mobile-friendly software
application for manual prepaid-electricity planning. Users record actual meter
balances and purchased top-up energy in kWh at selected times; transparent
calculations later estimate usage, remaining days, next top-up date and a 30-day
kWh recommendation.

No application code, schema, API, UI behavior or deployment was implemented.

## Before and after

- Before: the active roadmap led with camera hardware, OCR, device credentials,
  upload and a dashboard sourced from automated readings.
- After: the active path is email OTP, named meter profiles, manual kWh balance
  and top-up entries, raw-SQL history, deterministic forecasts, Material UI,
  email reminders, validation and deployment preparation.
- Hardware, OCR, device integration and ML remain preserved as deferred research
  and require evidence that manual entry is too inconvenient before resuming.
- "Top-up" means a manual record of energy already purchased. V1 has no tariff,
  Rand conversion, payment execution or automated vending.

## Documentation changes

- Rewrote `README.md` with the V1 actions, value, formula boundary, technology,
  deferrals, repository tree, execution roadmap and design references.
- Rewrote `agents/context.md` and updated `AGENTS.md` so future agents receive the
  software-only boundary before starting work.
- Updated the software, backend, database and frontend READMEs with the manual
  ledger, ownership, forecasting and mobile-flow direction.
- Marked the hardware root and every hardware component README as deferred.
- Marked the OCR README as deferred while preserving its research guidance.

## Roadmap

- Tickets 1-6 and 42 retain their completed historical status.
- Ticket 47 records this product/context pivot.
- Ticket 48 explicitly audits and removes obsolete active device/OCR domain
  assumptions before feature development.
- Tickets 43-46 remain the active email OTP/session sequence.
- Tickets 49-57 modularise meter profiles, balance entries, top-up entries,
  forecasting, dashboard/history APIs, Material UI, reminders, V1 validation and
  deployment preparation.
- Tickets 7-41 remain stable and are individually or by clear range marked
  superseded/deferred in the root roadmap.

## Forecasting guardrails

- Store and calculate energy in kWh only for V1.
- Require at least two valid actual balance readings with positive elapsed time
  before deriving usage.
- Include top-up kWh recorded between balance readings.
- Reject or surface negative consumption, impossible chronology and inconsistent
  entries.
- Keep actual records visibly distinct from estimates and show "Not enough data"
  when history cannot support a result.

## Reuse

- Retained FastAPI, PostgreSQL, direct Psycopg SQL, React, Vite, Material UI,
  Docker Compose and the planned email OTP/cookie-session architecture.
- Preserved all historical work records and deferred research sources.
- Recorded `../switch/hardware/web/` as read-only mobile UI inspiration and the
  sibling Roventics/Switch branding directories as future approved asset sources.
  No sibling file was modified or copied.

## Source-file protection

- `refocus.md` was left byte-for-byte unchanged.
- Its SHA-256 before and after the work is
  `8EE807DBC69F88F225D93D608DA7A5537FF2745454109F659342521B90849257`.
- It remains untracked and is explicitly excluded from the Task 008 commit.

## Verification

- `git diff --check` passed.
- The tracked diff contains Markdown documentation only.
- Roadmap IDs 1-57 are present exactly once across completed, active and
  superseded/deferred definitions.
- All repository-local Markdown links resolve.
- Active-context phrase checks found no remaining hardware/OCR-first runtime
  direction; the canonical files consistently state software-only, kWh and
  deferred automation boundaries.
- The final `refocus.md` SHA-256 matches the captured pre-change value.
- No application tests were run because application code and configuration did
  not change.
