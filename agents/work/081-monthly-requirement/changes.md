# Task 081 results

Completed 25 October 2026 at the user's direct request. No commit or push.

## Change

- Added monthly_requirement_kwh to the existing forecast, API schema and frontend
  type: daily rate times actual planning-month days, rounded to 0.001 kWh.
  It does not subtract balance; unavailable estimates return null, zero use is zero.
- Kept recommended_monthly_top_up_kwh and its current-balance subtraction unchanged.
  No database, reminder or rate-learning changes.
- The existing UI now shows Additional top-up and Monthly requirement alongside
  estimated balance and remaining days. Short notes distinguish extra energy from
  total monthly use. Four desktop columns become two on tablet and one on phones.
- Reused run_forecast_model, calendar duration, EstimateMetric and dashboard reload;
  no new dependency, settings or controls. Updated current context and relevant READMEs.

## Verification

- 39 isolated backend checks passed, including balance/top-up independence, actual
  28/29/30/31-day totals, default/measured/zero/unavailable values and API serialization.
- TypeScript and Vite production asset build passed. All 44 frontend checks passed
  with updated fixtures and assertions for both amounts, labels and responsive grid.
- The initial Docker build could not fetch a Docker Hub token due to a TLS handshake
  timeout. Verification instead used the existing cached development dependency
  image with current source/config/assets mounted read-only and no network. Both
  package.json and package-lock.json hashes matched before build/test. No successful
  fresh image build is claimed. Existing bundle-size advisory remains.
- Syntax/whitespace checks passed. Evidence: .tmp/task081/pytest.log, frontend.log
  and result.json. These are isolated checks, not a new live-browser acceptance run.

## Preservation

All task-owned containers and the isolated network were removed. No source service,
data, actual env or existing image was modified. The intermediate source metadata
check counted the temporary UI container because the cached image inherited
com.docker.compose.project=monitor-dev. After its automatic removal, the final
check confirmed source identities/images/start times/status/restart counts exactly
matched preflight. The ignored UI helper now overrides that project label for any
future reuse. No extra test run was needed; the application code did not change.

The running app still needs the new backend and frontend build. From software/:

```sh
docker compose -f prod.docker-compose.yaml up -d --build --no-deps backend frontend
```

Refresh the browser afterward. All earlier uncommitted work is preserved.
