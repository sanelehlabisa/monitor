# Task 100: Resumable research crawler

## Outcome
Implement Ticket 71.2 in the existing research script. Starting from the owner's
private links.txt, discover and retain reachable resources with resumable progress.
Status: explicitly approved by the user for the scope below.

## Questions and answers
- Task 099 is complete and published on master. The owner's existing file has
  16 syntax-valid seed entries; preserve it and never print its contents.
- Traverse a graph, preserving discovery paths and avoiding repeated fetches or
  cycles. Explore pages without emails too; they may lead to useful documents.
- Proposed initial scope for this task: seed hostnames and their www equivalents.
  Extra hosts can be explicitly allowed. Retain other external links for review,
  rather than silently dropping them or recursively following the entire web.
  Approval of this prompt confirms that starting boundary.
- Each run respects finite limits. Save unfinished branches for another run;
  depth-limited nodes remain deferred until the depth setting is raised.
- LM Studio/Qwen enrichment is required later in 71.5. This task collects its
  source material, without inference or a model download.
- No other unresolved questions for the proposed scope.

## Scope and reuse
- Extend the single typed, standard-library pipeline.py with --crawl and --resume,
  reusing --init/--check, path protection, seed input and existing limit options.
- Use a simple local queue and one private JSON checkpoint containing URL/node
  status and discovery links. Normalize URLs, remove fragments and deduplicate
  without dropping meaningful query parameters or alternate parent paths.
- Fetch public HTTP(S) resources with normal TLS validation, a clear user agent,
  robots/site restrictions and per-host delay. Bound request/redirect attempts,
  response size and timeouts; redirects and robots requests count toward budgets.
  Reject credentials, local/private targets and unsafe redirects. No browser,
  login bypass, script execution or intrusive probing.
- Parse HTML visible text, links, mailto values and public email candidates.
  Save bounded raw resources and extracted material under private evidence using
  generated filenames, not untrusted remote paths. Non-HTML resources are retained
  with content type and pending/unsupported status for 71.3; never claim them read.
  Emails here are raw evidence, not a second contact register or final CSV.
- Save progress after each resource using temporary-file replacement. Resume
  interruption without throwing away fetched evidence. Preserve malformed state
  and report recovery rather than resetting it. Use one writer at a time.
- Per-run request/page budgets reset on resume while completed nodes remain
  deduplicated. Keep out-of-scope/depth-limited branches and the reasons they wait.
  Report counts for fetched, pending, blocked, unreadable and failed resources;
  an exhausted budget does not mean the crawl is complete. Do not loop through
  repeated batches automatically or retry indefinitely.
- Keep all data/logs inside this experiment and ignored by Git. Print aggregate
  results only. Update research instructions and active context.

## Verification
- Use temporary fictional graph responses for cycles, shared targets, pages
  without emails, mailto extraction, redirects, blocked targets, resource types,
  size limits, errors, interrupted state and budget/depth/scope resume behavior.
- Exercise direct checks without adding persistent test files. Keep fixtures
  inside verified private directories and preserve existing --init/--check.
- After approval, use the real seed file for one small public smoke run capped
  at five total requests, including robots/redirects. Report counts and pending
  work only. Do not expand into a full collection run during verification.
- Verify seed-file hashes, private-output exclusions, script syntax, links and
  whitespace. No production services or data are involved.

## Exclusions
No PDF/office text reader, OCR, contextual enrichment/model call, final contacts
CSV, survey edit, outreach, DNS change, app integration or service restart.
No commit/push of Task 100 implementation without separate authorization.
