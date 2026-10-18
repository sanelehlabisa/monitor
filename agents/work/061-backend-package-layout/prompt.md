# Task 061: Backend package layout

## Aim

Make backend modules, validation schemas and endpoints easy to find.

## Clarifications

- Use modules/, schemas/ and endpoints/ under app/, with raw SQL and existing
  dataclasses, not ORM models or new architecture. Depends on Task 060.

## Change

- Move existing domain/raw-SQL/auth/email/forecast/reminder logic into modules/;
  move the four API routers into endpoints/ and extract their existing Pydantic
  request/response classes and validators into schemas/ by feature.
- Keep main.py, settings.py, database.py and version-bearing __init__.py at app
  root; move HealthResponse to schemas/. Update imports, monkeypatch targets and
  documented reminder-runner command. Keep app.main:app and reload working.
- Preserve exact API paths/payloads, auth scopes, UTC/Decimal validation,
  forecasting and runner behavior. No compatibility shims or eager re-exports.
- Update component guidance/context and changes.md. Line-budget exception covers
  mechanical moves/imports and extraction of existing schemas, not new behavior.

## Reuse

- Existing modules, dataclasses, validation, endpoint functions and checks.

## Verify

- Confirm source app services remain stopped before moving bind-mounted code;
  if unexpectedly running, ask before changing their state or moving code.
- Compare before/after OpenAPI contracts; check imports and run the full remaining
  backend suite against isolated DB/Mailpit. Never invoke the reminder CLI as a
  smoke test or write source fixtures. Check stale imports, links and whitespace.

## Out of scope

- ORM/framework/layer additions, feature or database changes, sharing/model
  integration, source service actions, research/history deletion, commits/pushes.
