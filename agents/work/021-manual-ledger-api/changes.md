# Task 021: Manual ledger API

## Result

Authenticated clients can create, list, retrieve, correct and delete factual
balance and purchased-top-up entries below an accessible meter.

## API and access

- Added nested `/api/meters/{meter_id}/balances` and `top-ups` collection routes
  plus entry-specific get/PATCH/DELETE routes.
- Reused one public owner-scope helper so regular users remain restricted to
  their meters and configured administrators receive unrestricted meter scope.
- Required timezone-aware, non-future occurrence times and strict Decimal
  precision/ranges at request validation.
- Returns 409 for duplicate actual-balance times, 422 for invalid input, and one
  generic 404 for missing, foreign or meter-mismatched resources.
- Responses preserve Decimal kWh as exact JSON strings and clearly separate
  balance and top-up fields.

## Reuse

- Reused cookie-session authentication, admin configuration, meter lookup,
  Tasks 019-020 repositories and established FastAPI response/error patterns.

## Verification

- Focused live-PostgreSQL ledger API test: 1 passed.
- Full backend suite: 44 passed.
- Integration coverage includes both CRUD resources, duplicate balance times,
  repeated top-up times, invalid/future/naive values, entry/meter mismatch,
  regular-user isolation and admin correction/deletion.
- Live frontend-proxy flow created balance/top-up entries as a regular user,
  rejected a future balance with 422, and let the configured admin list the
  meter, correct the balance and delete the top-up/meter with 204 responses.
- The synthetic Task 021 identity and cascading records were removed; both live
  sessions were logged out.
- `git diff --check` passed with only line-ending notices.
