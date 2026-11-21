# Task 101: Crawl access diagnostics

## Outcome
Implement follow-up 71.2.1: explain seed-access failures using private diagnostics
and a bounded seed-only review before document-reader work.
Status: explicitly approved by the user for implementation and the bounded live review.

## Questions and answers
- Task 100 is published. Its five-attempt smoke reached four of 16 seed URLs:
  one fetched, three failed at robots checking, and 12 remain budget-pending.
- One robots_unavailable and two robots_redirect_loop labels are observations;
  neither establishes a server, network or crawler root cause. Most seeds are
  still untested. Do not represent 72 discovered pending URLs as 72 failures.
- Exact existing seed outcomes are in ignored data/task100-access-review.json.
  The owner asked that access problems be noted and the next task prepared.
- Preserve the agreed public-host scope and normal robots/TLS protections.
  No unresolved questions for this proposed bounded diagnostic scope.

## Scope and reuse
- Reuse the same typed pipeline.py, private links.txt, checkpoint, raw evidence,
  existing request budgets, robots handling, retry limits and single-writer lock.
- Retain bounded private per-attempt diagnostics for robots/resource checks:
  HTTP status, redirect locations/chain, network error class and outcome.
  Separate missing/invalid redirect locations, actual cycles, TLS/DNS/timeouts,
  HTTP unavailability and explicit restrictions. Print aggregate counts only.
- Preserve existing checkpoint/evidence and the Task 100 review; add only the
  small optional state/report fields needed to understand the failures. Do not
  create another contact register, schema, service or framework.
- Fix a crawler defect only if demonstrated by a reproducible response case.
  Do not infer that a generic error means the site blocks scraping. Do not
  bypass robots, certificate validation, login, host scope or private-IP checks.
- After synthetic verification, perform one seed-only --resume review with
  --max-depth 0 --max-pages-per-seed 1 --max-requests 32 --request-timeout 10.
  Count robots and redirects in that cap. Keep two-attempt limits; do not reset
  failed counters or automatically run more batches. Record seeds still untested
  when rate, scope, restrictions or budget prevent access.
- Save exact findings in ignored data/task101-access-review.json, retaining
  original/current outcomes and concrete known/unknown causes. Public docs/context
  get aggregate seed coverage and follow-up actions only.

## Verification
- Direct synthetic checks cover HTTP failures, DNS/TLS/timeouts, missing Location,
  self/cyclic/long redirects, valid redirects, robots restrictions and retries.
  Confirm diagnostic writing does not leak URLs or change scheduler safeguards.
- Use temporary fictional fixtures inside verified private paths. No permanent
  test files or application checks are needed for this isolated script change.
- Verify the one live batch stays within 32 attempts; report tested/succeeded/
  failed/deferred/untested seeds without claiming a complete crawl.
- Check original seed/review hashes, checkpoint/evidence preservation, ignored
  outputs, offline setup/check behavior, syntax and documentation links.

## Exclusions
No broad crawl, extra automatic batches, request-limit bypass, PDF/office reader,
OCR, model call/download, final CSV, survey, outreach, app/service or DNS change.
No commit/push of implementation without separate authorization.
