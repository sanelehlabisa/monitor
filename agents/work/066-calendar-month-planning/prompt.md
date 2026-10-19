# Task 066: Calendar-Month Planning

## Aim

Implement Ticket 69.6 with a strictly-next-1st date and actual-month top-up math.

## Clarifications

- Predict only the usage rate; reuse current balance, with no separate future-balance projection.
- Always target the next UTC 1st; on the 1st, advance to the following month.
- Interpretation for approval: cover that upcoming full calendar month, not just
  the interval from now until its 1st. Use UTC datetime boundaries for its length.
- Example: 15 kWh/day and 300 kWh currently available means 120 kWh extra for a
  28-day February: max(0, 15 * 28 - 300). Do not deplete the balance to February 1.
- Future reminders: automatic to current meter members at 09:00 UTC on month-end;
  DB status and backend-startup catch-up. No user controls; separate tickets below.

## Change

- Reuse run_forecast_model and its existing ledger-derived current balance.
  Keep usage learning, remaining-days/run-out, validation and rounding unchanged.
- Calculate days from next UTC month-start to the following month-start, including
  leap years. Recommendation = max(0, rate * those days - current balance).
- Replace the misleading 30_days recommendation key consistently across model,
  API/schema, frontend and existing email wording. Include target-month UTC start
  (distinct from calculation time) and period days, even when estimates are
  unavailable; withhold unsupported kWh. No duplicate legacy field or DB change.
- Show the next top-up date as a UTC calendar date, separate from Predicted run-out.
  Preserve factual/estimated labels, layout and honest unavailable/zero-use states.
- Refresh read-only estimates at UTC month rollover and on return to an outdated
  open view, using existing request guards; never repeat a ledger write.
- Update current docs/context and changes.md. Aim for 100 implementation lines;
  allow up to 150 for the coordinated contract/UI rollover (tests/docs excluded).

## Reuse

- Existing datetime/Decimal helpers, forecast boundary, API adapter, MUI panel,
  Refresh/version guards and tests. Normal source reload only; preserve services.

## Verify

- Check 28/29/30/31-day months, December rollover, exact UTC boundaries, first-day
  advancement, current-balance subtraction, unavailable/inconsistent/zero use and
  unchanged rate/run-out. Verify dashboard/email amounts agree.
- Run isolated backend checks, frontend build/checks and mocked phone/desktop
  rollover/retry/navigation checks. No live fixtures, login, SMTP or DB writes.

## Out of scope

- Reminder scheduling/fan-out/catch-up implementation or activation (69.7.1/69.7.2),
  future-balance projection, research/model adoption, schema/roles, new dependencies,
  redesign, source service actions, sibling repos, commits or pushes.
