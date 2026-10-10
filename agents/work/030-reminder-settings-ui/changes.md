# Task 030: Reminder settings UI

## Result

Each selected meter now provides compact Material UI controls for optional
monthly and predicted-low-balance email reminders.

## Change and reuse

- Added typed reminder GET/PATCH client functions using the existing relative,
  cookie-authenticated API helper.
- Added independent switches, constrained monthly-day and lead-day inputs,
  browser IANA timezone capture and one explicit save action.
- Reused the selected-meter owner/admin workspace and its request feedback
  patterns; the browser performs no scheduling or forecasting.
- Explained that monthly email may request a fresh reading and that low-balance
  email requires a valid forecast. The UI promises no purchase or guaranteed
  estimate.
- Added API and static component coverage for defaults, enabled values,
  timezone text, loading, saved and request-error states.

## Verification

- Frontend tests: `20 passed`.
- Frontend production build: passed.
- Owner defaults/save and administrator read/save through the frontend proxy:
  passed in the Task 029-030 batch check.
- Complete backend suite: `60 passed`.
- `docker compose -f dev.docker-compose.yaml config --quiet`: passed.
- `git diff --check`: passed (line-ending conversion warnings only).
