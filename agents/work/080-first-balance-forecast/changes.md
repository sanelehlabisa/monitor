# Task 080 results

Completed 24 October 2026. The user requested immediate first-balance estimates
and confirmed existing dashboard only, without charts. No commit or push.

## Change and reuse

- run_forecast_model now uses one DEFAULT_DAILY_USAGE_KWH constant (10 kWh/day)
  when exactly one actual balance exists at or before calculation time. This is
  an assumption, not the research simulator's trained/synthetic prior.
- Existing elapsed datetime, intervening purchases, balance clamp, remaining days,
  run-out and calendar-month recommendation math is reused. Two or more valid
  balances replace the fallback with that meter's observed time-weighted rate.
- No balance remains unavailable; future/contradictory history is not masked by
  fallback. Observed zero use retains its existing no-finite-run-out behavior.
- API shape stays unchanged: available with intervals_used=0 identifies a starting
  estimate. UI and monthly email explicitly label it. Legacy low-balance warnings
  still require measured history; no scheduler or production-mail activation.
- Existing create/edit/delete handlers already reload the dashboard, so their
  stale-response/error guards are reused unchanged. No charts or new dependencies.
- Updated current product guidance, README files and context to supersede the old
  first-balance restriction. Historical work and research remain untouched.

## Verification

- 38 focused backend checks passed in 3.61 seconds: forecast/calendar boundaries,
  actual synthetic ledger API POST/PATCH/DELETE transitions, independent meters,
  default and measured email copy/policy, plus existing reminder-runner behavior.
- The API flow covered empty -> first balance -> purchase -> measured rate ->
  inconsistent/corrected reading -> deletion back to default -> edit -> empty.
  Future readings, fractional time, purchase boundaries, zero/depletion, all
  calendar-month lengths and observed zero use are covered.
- Frontend TypeScript/Vite build passed. All 44 frontend checks passed, including
  clear default labeling and transition to measured use. The existing >500 kB
  bundle advisory remains; no unrelated bundling changes.
- Independent implementation review and whitespace checks passed. This is isolated
  API/UI verification, not a new live-user browser or household accuracy claim.

## Preservation and handoff

The verification used the running backend's existing dependency image with
read-only current app/tests mounts and a private, task-owned PostgreSQL container
using temporary memory-backed data. No actual .env or source DB was used. The two
backend-check containers, their network, frontend-check container and temporary
frontend image were removed; no Task 080 containers/networks remain.
Source container identities/images/start times/status/restart counts matched
before and after. Evidence: .tmp/task080/pytest.log and result.json.

The running app still uses its previous build. From software/, apply both changes:

```sh
docker compose -f prod.docker-compose.yaml up -d --build --no-deps backend frontend
```

Reload the browser afterward. No live data, env, credentials or earlier uncommitted
work was changed; source services were not restarted or recreated.
