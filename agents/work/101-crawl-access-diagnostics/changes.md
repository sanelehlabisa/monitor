# Task 101 results

At the user's request, published Task 100 plus aggregate access findings to
Monitor master as 38c24092d92ab74f3f6b10a1a7c01baece5d7e51.
Local HEAD and remote master matched after push. The nine reviewed source/docs
were committed; private seed, state, evidence and per-seed review were excluded.
Syntax, offline check, whitespace and all 38 local links passed before publication.

Reviewed the saved checkpoint without further web requests. Four of 16 seeds
were attempted across four hosts: one fetched, three failed during robots checks.
The 12 remaining seeds are budget-pending. Added follow-up 71.2.1 to diagnose
access before 71.3 document readers; a majority-of-all-seeds problem is unproven.

Prepared this prompt from agents/prompt.md. Proposed implementation adds bounded
private diagnostics and one seed-only batch of at most 32 request attempts while
preserving existing safeguards and artifacts. The user approved Task 101;
implementation and the single review are complete within that scope, as below.
The changes remain local and uncommitted.

## Implementation and demonstrated defects

- Reused the same typed, standard-library pipeline.py, state and writer lock.
  Added two bounded private diagnostic records per node, containing stage,
  request URL, HTTP status, redirect Location, error class and outcome. TLS
  verification code/message and Retry-After are private; console output stays
  aggregate-only. No dependency, service, database or test file was added.
- Separated robots HTTP errors, DNS failures, TLS verification/protocol errors,
  timeouts, missing/invalid redirect Location, self redirects and actual cycles.
  A synthetic response proved missing Location previously normalized to the same
  URL and was incorrectly labelled a loop. Both redirect paths now validate it.
- Kept budget, robots, rate, host scope, IP pinning, normal TLS validation,
  existing retry caps and single-writer behavior. Rate/scope deferral propagates
  without turning a scheduling pause into an access failure.
- After the live review, a synthetic wire capture proved HTTPConnection's
  default-port handling added :443 to HTTPS Host although the normalized URI
  authority omitted it. Set Host explicitly to the normalized authority. HTTP
  and HTTPS wire checks pass with the pinned address and TLS hostname preserved.
  This correction follows the [HTTP Host requirement](https://www.rfc-editor.org/rfc/rfc9112.html#section-3.2).
- This header defect may contribute to self-redirects, but the reviewed sites'
  response to the fix is unverified. No second batch was run, even though the
  first ended below its maximum. Existing failed counters were not reset.

## Verification and private evidence

- Passed 25 direct synthetic diagnostic/CLI scenarios for redirects (missing,
  invalid, self, cycle, long and valid), DNS/TLS/timeouts, HTTP restrictions,
  Retry-After/rate deferral, cache/retry limits, seed-only depth limits,
  malformed diagnostic state, offline modes and non-leaking console output.
- Two additional synthetic HTTP/HTTPS wire checks confirm the Host correction,
  a single matching header, checked-IP connection and original TLS hostname.
  These checks made no live requests and added no persistent test files.
- The one approved --resume review used depth 0, one page per seed, a maximum of
  32 requests and a 10-second timeout. It ended after 16 request attempts with
  all 16 seeds reviewed: five downloaded (four HTML, one PDF), nine robots
  self-redirect failures, one TLS verification failure and one target HTTP403.
  The full discovered graph is 348 nodes, with 332 still pending. No broad crawl.
- These are seed-URL outcomes, not unique-site counts or permanent-inaccessibility
  findings. Some failed seeds reuse a cached robots outcome. The seed report
  retains the actual per-attempt request count and chain; failures are not all
  separate outgoing requests. Existing success from Task 100 was not re-fetched.
- Saved original checkpoint bytes at ignored data/task101-state-before.json and
  original/current outcomes at data/task101-access-review.json. The report records
  that live results preceded the Host fix and that its remote effect is unknown.
  Hash comparisons passed for links.txt, task100-access-review.json and all
  pre-existing evidence files. No old file was moved, deleted or reset.
- Lock cleanup passed; the final contacts CSV remains absent. Private state,
  evidence and reports are excluded from Git. Source syntax, offline check,
  whitespace and documentation links pass.

Consulted the [Python TLS error documentation](https://docs.python.org/3.14/library/ssl.html#ssl.SSLCertVerificationError)
and [HTTP redirect semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-location)
alongside the wire evidence. No TLS verification was disabled.

Root/software research READMEs and current context now record the observed access
limits, corrected client behavior and pending live confirmation. A separately
approved bounded recheck is needed before a broad crawl; no extra batch is covered
by these results. The saved PDF is available for 71.3 document-reader work.
Next work prompt is 102. No model, outreach, app/service, DNS, commit or push action.

## Subsequent manual deferral and publication authorization

The user requested commit/push and a private failed-links list, deferring access
fixes so document work can continue. Added ignored links.failed.txt with 11 unique
seed URLs and reason comments (nine robots self-redirects, one TLS verification
failure, one HTTP403). It identifies observations before the Host fix rather than
calling every entry a robots.txt ban. Exact URLs remain local, out of Git/output.

Hash checks confirm links.txt, crawl_state.json and the Task 101 access report
were unchanged during this export. No additional requests or retry reset. Active
docs/context record the owner's deferral; the next prompt is offline PDF/document
reading. Publication includes only reviewed source/plans, not private URL lists,
state, evidence or generated research data.
