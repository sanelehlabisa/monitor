# Task 042: Validation and release roadmap

## Aim

Document Monitor's next usability, validation and release tickets without implementing them.

## Clarifications

- Keep costs deferred and validate the existing kWh-only app: confirmed.
- Reuse Tickets 56, 57 and 58 instead of duplicating them: confirmed.
- Update both repositories' planning only; product implementation needs separate approval.

## Change

- Add 65 Usability Review, 66 Forecasting Algorithm Validation, 67 External User Testing and 68 Installable Web App (future).
- Refine 56 Personal Usage Validation, 57 Web Deployment and 58 Monitor App Identity; preserve completed history and stable IDs.
- Define usability scope: onboarding, dashboard, actual/estimate distinction, mobile layout, empty/loading/error states, wording, removal of unnecessary screens and branding through 58.
- Define synthetic forecast validation for consumption, daily use, current balance, days, run-out and purchase quantity: normal/changing/high/zero usage, intervening top-ups, missing/irregular readings, negative consumption and insufficient data. Distinguish total monthly usage from additional kWh to buy.
- Define real-household prediction comparisons and repeat-entry feedback in 56; define a 3-5-user deployed pilot in 67 without commercial-demand claims.
- Define 57's remaining production Docker, HTTPS, env, migrations, SMTP/OTP, backup/restore, monitoring, privacy and error-logging acceptance; retain Task 036's completed images.
- Order 65 -> 66 -> 57 -> begin 56 and 67. Logo placement awaits the supplied asset; other usability work need not wait. Defer 68 until web-usage evidence supports it.
- Record the shared priority: while waiting for Monitor feedback, Switch 84 assembly -> measured enclosure -> two-week internal test -> 85 PCB replacement after arrival. SPII/supplier timelines stay parallel.
- Update README.md, agents/context.md, software/README.md, software/frontend/README.md and software/backend/README.md; put detailed ticket acceptance in the closest README and write this task's changes.md.

## Reuse

- Existing ticket IDs, work template/history, simple model/tests, React/MUI, raw SQL and production-image documentation.

## Verify

- Check unique ticket definitions, links, dependencies, deferred boundaries and git diff --check.
- Confirm Markdown-only changes and report ticket numbers, changed READMEs, work records and dependencies.

## Out of scope

- Executing tickets, code/tests/fixtures/schema/runtime changes, DB data, costs/tariffs, ML/OCR/LLMs, hardware, deployment, invitations, new logos, React Native/stores, commits/pushes and refocus.md edits.
