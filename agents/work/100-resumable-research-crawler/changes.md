# Task 100 results

Published the completed research plan/workspace as
1b233b4aad7a5f4f363cc315a58ed5ed370736b1 on Monitor master, as requested.
The remote master SHA matched local HEAD. Only the 12 reviewed source/planning
files were committed; links.txt and generated/private directories remain excluded.
The offline workspace check and staged whitespace check passed before publication.

Prepared the next prompt from agents/prompt.md for Ticket 71.2, reusing the one
script and private seed file. The proposed initial scope is seed hosts plus www
equivalents, with explicit expansion and retained external/deferred branches.
The user subsequently approved Task 100. Implemented Ticket 71.2 below; this
implementation remains local and uncommitted.

## Implementation and reuse

- Extended the existing typed, standard-library pipeline.py with --crawl and
  --resume. Preserved offline setup/check modes and the owner's seed file.
  No third-party package, framework, database or persistent test file was added.
- Added seed-host/www scope with explicit --allow-host expansion, normalized
  HTTP(S) URLs and graph edges retaining alternate parents. Cycles and completed
  nodes are deduplicated. Pages without contacts are still traversed.
- Per-run page/request budgets reset on resume; depth/scope/rate-limited branches
  remain pending. Redirects count against requests, add no graph depth, have a
  finite chain limit and cannot downgrade HTTPS. Failed nodes have two attempts
  across runs; errors remain visible instead of repeated indefinite retries.
- Public-address validation covers all resolved addresses before connecting to
  one pinned address, preserving HTTPS hostname/certificate checks. No automatic
  redirect/proxy/authentication handling can bypass target validation. Only
  standard web ports are supported. Body size, socket waits and resource attempts
  are bounded; system DNS resolver timing remains OS-controlled.
- Robots parsing handles matching-group merging, wildcard/end rules and longest
  paths. Policies are cached for up to 24 hours. Host delays and Retry-After
  backoffs persist across runs; long waits defer work instead of long sleeps.
- Private JSON checkpoints use temporary replacement and an exclusive writer
  lock. Ctrl+C saves pending work and removes the lock. Hard-crash stale locks
  require manual review; malformed state and differing evidence are preserved.
- HTML visible text, links, mailto/public email candidates and bounded raw files
  are saved under generated evidence names. Non-HTML resources are marked
  pending_reader, not reported as read. No final CSV, model call or outreach yet.
- Updated root/software/research READMEs and context with actual usage and limits.
  No existing source or user file was moved, retired or deleted.

## Verification

- The final expanded suite passed 33 direct CLI/policy/transport checks using
  temporary fictional responses. Coverage includes cycle/shared-link traversal,
  empty-contact pages, private mailto evidence, budgets and scope/depth expansion,
  cached robots, retry caps, redirects, Ctrl+C/resume, malformed checkpoints,
  changed seeds, writer locks, saved rate waits and Retry-After.
- Synthetic socket checks verified checked-IP connection, hostname propagation
  into TLS and oversized-response rejection. Private, link-local, loopback and
  multicast address cases were rejected without live network requests.
- Temporary fixtures stayed inside a verified ignored research data directory
  and were cleaned. The initial 16-scenario pass also passed. A verification-helper
  JSON read of an intentionally malformed checkpoint was corrected before the
  expanded rerun; the application correctly preserved/rejected that checkpoint.
- Ran the one approved real smoke with --max-requests 5 --request-timeout 10.
  It stopped at five attempts, fetched one HTML page and saved 76 resource nodes:
  72 pending (70 request budget, two external scope) and three failed (one
  robots_unavailable, two robots_redirect_loop). These are recorded remote-access
  outcomes, not evidence that all seeds or the full corpus are readable.
- Seed SHA-256 remained unchanged, the final contacts CSV is absent and the
  writer lock was removed. Only aggregate outcomes were printed. State and the
  two evidence files remain private under data/ and excluded from Git.
- Source syntax, offline --check, local documentation links and whitespace pass.
  No application build is appropriate for this isolated script-only change.

Consulted the official [Python HTTP client documentation](https://docs.python.org/3/library/http.client.html),
[TLS documentation](https://docs.python.org/3/library/ssl.html) and
[RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html) for transport and robots
semantics. Inspected the installed robotparser before using a small explicit
matcher for wildcard/longest-rule handling.

No more than the approved smoke batch was run. No production service, application
data, DNS, emails, model, dependency installation, commit or push was changed.
Next research slice is 71.3 document readers; next work prompt is 101.

## Subsequent access review and publication request

The user requested commit/push to master, preparation of the next work and notes
on scraping problems. Read the existing checkpoint only; no further requests.
Four of 16 seed URLs were attempted across four hosts: one fetched and three
failed at robots checking. Twelve seeds are budget-pending, so a majority-of-all-
seeds failure claim is unsupported. Generic robots_unavailable and the two
robots_redirect_loop outcomes do not establish the actual HTTP/network/parser cause.

Saved exact seed results in ignored data/task100-access-review.json and added
71.2.1 access diagnostics before document readers. Public documents retain only
aggregate outcomes. The user authorized publication of the reviewed implementation
and these notes; private seed/state/evidence/review files remain excluded.
