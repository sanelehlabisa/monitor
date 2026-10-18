# Task 061: Backend package layout

## Result and reuse

Reorganized existing backend code without changing its behavior:

- Moved eleven domain/raw-SQL/auth/email/forecast/reminder files into
  `app/modules/`, retaining their dataclasses and single forecast boundary.
- Moved the four routers into `app/endpoints/` and extracted their existing
  Pydantic classes/validators into feature files under `app/schemas/`.
  `HealthResponse` also moves to schemas.
- Kept `main.py`, `settings.py`, `database.py` and the version-bearing
  `__init__.py` at the app root. The entrypoint remains `app.main:app`.
- Added docstring-only package initializers, updated imports/monkeypatch paths in
  seventeen test files, and documented the layout and canonical finite command
  `python -m app.modules.reminder_runner` in the backend README.

No ORM, layer, dependency, compatibility shim, eager export or new feature was
added. Preserved pending Task 059 role changes, API/cookie shapes, authorization,
SQL, UTC/Decimal validation, forecasting and runner behavior. Research, source
data/services and the verified `.tmp/task060/pre-cleanup-source.zip` recovery
archive are untouched.

Review-size exception: the approved mechanical refactor relocates 2,363 original
lines across fifteen files (1,506 domain and 857 router lines), extracting 213
schema-file lines. Those counts describe code movement, not new algorithms.
Tests and documentation are excluded from the implementation-line guideline.

## Verification

- PASS: root confirmed source backend/frontend/Mailpit were exited before the
  bind-mounted code moved; the existing database remained running. No source
  service start/restart or source database write was performed.
- PASS: old flat-module imports are absent from current app/tests; package root
  contains only main/settings/database/version files. Scoped whitespace checks
  pass.
- PASS: independent stdlib AST comparison through
  `.tmp/task060/compare_layout.py` matched all eleven domain moves, three
  unchanged root files, 54 router/schema definitions and the main/health
  definitions against the post-059/verified-060 baseline, excluding imports and
  docstrings. No function-body changes were found.
  Root repeated this check after the final blank-line-only formatting; it passed.
- PASS: all 67 backend checks passed in 42.63 seconds, without warnings, using
  isolated fresh DB/Mailpit resources and current code. No source DB/services
  were touched by verification. Subsequent formatting adds blank lines only.
- PASS: canonical OpenAPI is JSON-identical to Task 060, SHA-256
  `32c5aba6aa94d8a9473b9a0b286c5b0fc6c1f913bdbe7b511fd4e579784e04a7`.
  Byte-for-byte comparison and matching dependency-version evidence are retained
  in `.tmp/task060/openapi-comparison-9b7ef9e8ef9e.json`.
- PASS: isolated verification cleanup completed at `2026-10-18T18:20:31Z` with
  status `verified-cleaned`. Three task containers, one synthetic database volume
  and one internal network were removed after exact ID/label/mount checks;
  matching task labels were absent afterward. Source data/services and retained
  recovery evidence were untouched.

The finite reminder CLI was not executed, including with `--help`. No source
HTTP login, real email, model integration, commit or push was performed.
