# Task 102: Extract content during crawling

## Outcome
Implement Ticket 71.3 as one continuous crawl-and-extract flow. Every successful
response goes through type detection and a small suitable reader in memory.
Save useful extracted information without first saving the original page/file.
Status: the user explicitly approved the revised implementation and bounded verification.

## Questions and answers
- The owner rejected a required local-download/offline-parsing stage. Fetch
  response bytes once and extract from them directly, whether HTML or a document.
  Network transfer is still needed; a saved original file is not a prerequisite.
- Do not hardcode the current saved PDF or a particular URL/filename. Choose the
  reader from response type/content and support additional formats when needed.
- Persist extracted text/facts, provenance, statuses and progress. New raw .bin,
  HTML or PDF copies are not saved by default. Existing captures remain intact.
- Access fixes stay deferred. Honor private links.failed.txt before requests;
  do not retry its 11 URLs during this task. Existing retry counts stay intact.
- Keep one script and isolated reader dependencies. Required local LM Studio
  enrichment remains in 71.5 with the owner's preferred installed small Qwen.
- No unresolved questions for this revised flow. Approval covers only the scope
  and bounded verification proposed below.

## Scope and reuse
- Reuse typed pipeline.py, --crawl/--resume, the bounded fetcher, graph, checkpoint,
  path protection and writer lock. Replace the proposed standalone offline mode
  with a small extraction function called directly after a successful fetch.
- Detect MIME/content signatures and dispatch to simple readers. Reuse HTML
  parsing, support plain text with the standard library and add PDF-from-bytes
  reading with a small library such as PyMuPDF after compatibility checks.
  Keep its pinned requirement and .venv here; load it only when needed.
  This is a few format handlers in one script, not a parser framework.
- Produce the same compact result shape across formats: source URL/type, explicit
  title when available, text, email candidates, discovered links and extraction
  status. Include page/nearby-text evidence where available; leave unknowns blank.
- Feed normalized links back into the existing queue immediately, sharing the
  same host, depth, page and request limits. Do not refetch a resource just to
  change readers or require a disk file as reader input.
- Save extracted information and provenance privately, not original response
  files by default. Preserve old raw/metadata captures and write results without
  overwriting differing existing outputs. Keep contacts.csv for 71.7.
- Load the manual failed-URL list before scheduling requests and redirects.
  Keep its URLs deferred without replacing their original error history or
  resetting counters. Preserve robots/TLS/private-IP checks and rate limits.
- Bound response size and reader work. Record partial, encrypted, textless,
  malformed, missing-reader or unsupported outcomes instead of inventing content
  or repeatedly fetching. A later reprocess needs another authorized fetch when
  its response bytes were not retained. Do not execute embedded content or OCR.
- Update research instructions/context with current versus planned behavior and
  keep outputs ignored. Do not install parsers for speculative office formats.

## Verification
- Inject bounded HTML, plain-text, PDF and unsupported response bodies into the
  fetch-to-reader path. Check emails/links, PDF pages/title, errors/limits and
  format-independent results. Confirm raw files are not written and readers do
  not request their own URL again. Use direct checks without persistent test files.
- Verify failed-list exclusions, graph links, budget/cycle behavior, resume,
  existing CLI modes, private result paths and preservation of existing artifacts.
- After approval, run one small live check using only previously successful seed
  URLs, capped at five request attempts including robots/redirects. Do not use the
  manual failed URLs or broaden scope. Stop at the cap and report partial results.
- No dependency on an already saved document. Existing private captures may be
  reused as test bytes, but normal operation must work from a fetched response.
  No source text, contact records or URLs in Git/terminal summaries.

## Exclusions
No separate download/archive stage, deletion of old captures, failed-link/access
recheck, broad crawl, restriction/TLS bypass, OCR, general document framework,
model call/download, final contacts CSV, survey, outreach, app/service/DNS change,
commit or push of implementation.
