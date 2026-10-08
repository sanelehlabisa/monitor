# Task 008: Software-only product refocus

## Aim

Refocus Monitor's active V1 documentation and roadmap on a free, software-only electricity planning application based on quick manual kWh entries and simple, honest forecasts.

## Clarifications

- Question: What does V1 record? Answer: Users manually record remaining meter balance in kWh and top-up energy in kWh, each at a selected date/time that defaults to now.
- Question: Should V1 accept Rand values or require a tariff? Answer: No; assume energy values are in kWh for the simplest reliable first version. Defer tariffs, Rand conversion and cost estimates.
- Question: What should V1 predict? Answer: Estimate daily kWh usage, current remaining kWh, remaining days, a likely run-out/next-top-up date and recommended monthly top-up energy in kWh. Show "Not enough data" instead of inventing results.
- Question: What happens to hardware, OCR and machine learning? Answer: Move them out of active V1 into clearly deferred future work. Preserve their files and history so automation can be reconsidered if manual entry proves too inconvenient.
- Question: What happens to `refocus.md`? Answer: Leave it completely unchanged and do not include it in a commit.
- Question: May sibling repositories inform later design work? Answer: Yes. Use the sibling Switch dashboard only as read-only UI inspiration, and approved Roventics brand assets as a future source. Never modify either sibling repository as part of Monitor work.

## Change

- Rewrite the active product definition in the root README and `agents/context.md`: Monitor V1 is a mobile-friendly web app that helps households estimate how much prepaid electricity to add and when.
- Replace the active V1 flow with email OTP -> create/select a named meter/property -> record balance/top-up kWh -> view history -> receive transparent mathematical estimates -> optionally receive email reminders.
- Document the two primary manual actions and their date/time behavior, including chronological validation, corrections and explicit actual-versus-estimated labels.
- Document the minimum forecasting contract and edge cases: top-ups between readings, elapsed time, insufficient data, impossible negative consumption, reordered readings and inconsistent values.
- Update every affected component README so frontend, backend, database and software documentation agree with the software-only V1.
- Mark existing hardware, device-ingestion, OCR, anomaly ML, automated payment/top-up and municipal roadmap tickets as deferred or superseded without deleting files, rewriting completed work or renumbering ticket IDs.
- Retain the passwordless email OTP tickets that still apply.
- Add a modular active roadmap using new stable IDs for the product pivot, cleanup of obsolete active assumptions, user/meter ownership, balance entry, top-up entry, forecast calculations, history/dashboard APIs, Material UI screens, email reminders, end-to-end testing and deployment preparation.
- Record the approved read-only UI/brand references for later frontend work: `../switch/hardware/web/` for compact mobile interaction ideas and `../roventics/frontend/images/` or `../switch/assets/branding/roventics/` for company artwork. Do not copy assets in this task.
- Create `changes.md` with the before/after product boundary, retained/deferred tickets, new execution order, affected documentation and verification results.
- After verification, commit and push only the tracked Task 008 changes. Explicitly exclude the untracked `refocus.md`.

## Reuse

- Keep FastAPI, PostgreSQL, raw SQL through Psycopg, React, Vite, Material UI, Docker Compose and the planned email OTP/cookie-session architecture.
- Reuse existing numbered ticket history and work records instead of deleting or rewriting them.
- Keep hardware/OCR documentation as deferred evidence for a later automation decision.
- Reuse the Switch UI's mobile-first clarity as inspiration only; implement future Monitor UI natively in React and Material UI.

## Verify

- Confirm all active README/context descriptions agree that V1 is software-only, manual-entry and kWh-only.
- Confirm hardware, OCR, ML, device upload and payment integration appear only as deferred/future work rather than active dependencies.
- Confirm roadmap IDs are unique and existing IDs/history remain stable.
- Confirm the active execution order is modular and includes an explicit cleanup ticket before feature development.
- Confirm local Markdown links resolve and repository trees remain accurate.
- Confirm `refocus.md` is byte-for-byte unchanged, remains untracked and is excluded from the commit.
- Run `git diff --check` before committing and verify the pushed branch is clean apart from untracked `refocus.md`.

## Out of scope

- Implementing or changing application code, database migrations, APIs, forecasting functions, authentication, UI screens, reminders or deployment.
- Tariffs, Rand values, cost forecasts, automated purchases or payment-provider integration.
- Hardware, firmware, camera capture, OCR, LLMs, anomaly ML, MQTT or municipal features.
- Copying UI code or brand assets into Monitor.
- Editing, deleting, staging or committing `refocus.md`.
- Modifying the sibling Switch or Roventics repositories.
