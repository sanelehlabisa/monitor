# Task 103: Contact collection complete

## Result

Implemented the approved collection-only milestone in the existing typed
`software/research/market-research/pipeline.py`. Tickets 71.3.1 and 71.4-71.7 now
cover independent email/phone rows, source context, optional local enrichment,
cleanup and restartable CSV output. No sending or application integration.

- HTML visible text, mailto/tel links, PDF text/URI annotations and plain text
  supply normalized contact methods with source/page/nearby evidence. Explicit
  hidden HTML is excluded; no scripts, OCR or access bypass execute.
- Added isolated `phonenumbers==9.0.44`; reused `pypdf==7.1.1`. Credible ZA numbers
  prefer E.164, explicit international prefixes remain respected and labelled
  uncertain local forms keep original/uncertainty notes. Dates, IDs and prices
  are filtered. Email syntax/case validation does not probe mailboxes.
- One private `data/contacts.csv` uses the exact approved 15 columns and stable
  IDs. Deduplication is by (contact_type, contact_value), without person matching.
  Blank context can be filled; manual fields, statuses, contact history and notes
  survive. Conflicting named facts and additional sources are retained in notes.
- Reused atomic replacement and writer locks. Added an experiment-level contact
  lock, external-edit checks and malformed-input preservation. Contacts save
  before a resource is marked complete. Different checkpoint directories still
  update the same canonical CSV; stored extracted evidence is replayable.
- Added a shared hostname/www page-attempt budget, explicit challenge/terms
  checks and private `data/blocked_urls.csv`. Robots, rate/backoff, TLS/public-IP
  guards, bounded traversal and manual deferrals remain enforced. Actual access
  blocks are distinguished from temporary limits and transport/redirect errors.
- Optional loopback-only LM Studio uses bounded JSON-schema requests, nearby
  prose grounding, private success caching and deterministic fallback. Unknowns
  stay empty. Neither domains nor publisher titles establish contact identity.
  Model output cannot invoke tools. No downloads, cloud calls or server restart.

## Verification

58 direct checks passed using stdin scripts and temporary fictional workspaces;
no test files were added. Checks covered HTML/PDF/tel/mailto, formats/uncertain
phones, numeric false positives, free-mail/publisher attribution, local model
success/cache/outage/invalid JSON/hallucinations, shared domain limits, resume,
CSV identity/defaults/manual preservation, malformed/external edits, atomic-write
failure, challenge/robots/manual restrictions and rate deferrals. New descriptive
formula cells are neutralized; normalized identities are preserved.
Final CSV/protected-file integrity, 24 relative documentation links, offline
`--check`, isolated `pip check` and `git diff --check` also passed.

One authorized live run used the existing 16 seeds/checkpoint with ceilings of
30 requests, depth 2 and ten page attempts per seed/domain. It stopped after
20 requests at domain/scope limits; all 11 manual-review URLs stayed deferred.
Results printed by the CLI:

```text
Pages visited: 20
PDFs processed: 0
Emails found: 50
Phone numbers found: 69
Unique contacts added: 109
Duplicates skipped: 66
Blocked URLs: 1
Errors: 0
```

Contact finds include eight reused extracted records, including PDF evidence;
69 phone finds deduplicated to 59 unique phone rows alongside 50 unique emails.
The checkpoint now has 515 nodes: 24 fetched, one redirect, 479 pending, one
blocked and ten existing failures. This is bounded collection, not full coverage.
No deferred seed was retried and no raw original was added. Existing inputs and
five old binary captures passed hash-preservation checks. All generated paths
are ignored by Git, and normal exit released both writer locks.

The local LM endpoint was unavailable: the live run made one discovery request,
zero inference requests and used source fallback. Small-model identity and real
inference remain unverified. Mock API checks verify the integration paths, not
real model quality. A focused context review removed a temporary publisher-based
heuristic; generated assumptions were corrected without changing identities or
contact/status fields. Unknown identity fields remain blank; source excerpts,
titles, URLs and page notes remain available for review.

A request-free replay of all 27 extracted evidence records preserved 109 rows and
all IDs. Private verification/audit files are in the experiment's `data/`, including
`task103-verification.json`, `task103-before.json` and `task103-context-review.json`.
Three actual generated rows were selected for the owner's requested preview;
contact records are deliberately absent from this tracked report.

## Reuse and boundaries

Reused PageText, in-memory content readers, evidence JSON, crawl graph/checkpoint,
Fetcher policies/limits and atomic/lock helpers. Updated root/research READMEs and
active context. Historical files and unique sources were preserved. No files were
retired; only owned temporary verification folders were cleaned after checking
their resolved paths stayed inside this research workspace.

No email/SMS sending, outreach drafts, SMTP checks, live app/database changes,
service restarts, Docker changes, commit or push. The next step is owner CSV
review. Any outreach requires a separate approved prompt.

Implementation references: [phone library](https://github.com/daviddrysdale/python-phonenumbers)
and [LM Studio structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output).

## Local-import extension preparation

The owner requests importing manually downloaded files and removing successful
inputs afterward, continuing Task 103. Inspected the private links.failed/ folder:
seven regular PDFs, 111 pages total, no encryption, all under existing byte limits.
Six uniquely match seed/failed URL basenames; the unmatched input needs honest
local-file provenance rather than an invented source. No contacts were printed
or imported during this inspection.

Prepared local-import-prompt.md from agents/prompt.md and linked it from the
research README/current context. It reuses the existing readers/register and
defines verified evidence/CSV persistence before individual input deletion, with
failed/partial files retained. Exact cleanup paths/results will stay in a private
import report referenced here. Approval is pending under AGENTS.md; this extension
has made no code/dependency, contact CSV, source-file, crawl-state or Git changes.

## Approved local import: implementation and results

The owner approved local-import-prompt.md and reiterated execution. Added
--import-dir and explicit --delete-imported to the existing pipeline, without
new dependencies or scripts. Factored reusable extraction persistence out of the
web wrapper; its metadata/link contract remains verified. Local HTML/PDF/plain
text uses existing contact validation/enrichment and the same locked canonical
CSV. URL matching uses only a unique seed/failed filename match; otherwise local
URI provenance is validated within the experiment and source_domain stays empty.
Local path/hash and source title/page context remain in private evidence/notes.
The public crawler's HTTP URL/network rules are unchanged.

Cleanup checks a real, experiment-local, regular input directly inside the chosen
directory. Links/reparse points, protected paths and unrelated directories are
excluded. Existing byte/page/text limits apply. Complete extraction, saved and
verified evidence, persisted method pairs and unchanged input bytes/stat identity
are required before individual unlink. Partial, unreadable, encrypted, textless,
challenge, oversized and changed sources stay for review. Fully readable
zero-contact inputs can be removed with verified evidence. No recursive removal,
raw archive or automatic linked-resource fetching.

The ignored data/local_imports.json keeps exact input paths, SHA-256 hashes,
source mappings, evidence paths, persistence proof and per-file cleanup results.
It saves a verified ready-to-delete record before unlink; interruptions/retries
keep deduplicated IDs and extracted evidence. No stale record authorizes deletion
of changed current contents. Failed persistence stops cleanup, while a failed
unlink retains the input and is recorded.

### Checks

33 focused direct checks passed using fictional stdin-driven temporary fixtures,
without persistent test files. Covered HTML/PDF/text methods, original/local and
ambiguous provenance, stable IDs, repeated imports, manual/contact/response field
preservation, complete zero-contact cleanup, local evidence replay after deletion,
public web-wrapper compatibility, precise textless retention, byte/page limits,
encrypted/malformed/challenge inputs, changed-file/deletion/write/verification
failures, malformed audit preservation, protected seeds/directories and no network
or model calls. Temporary directories were resolved inside the experiment before
owned cleanup. Early fixture attempts encountered Windows path/file I/O limits;
shorter fixture paths and the final full rerun passed. These failures retained
inputs; no path/security or persistence checks were relaxed.

### Actual private batch

One approved source-only import processed the seven supplied PDFs (111 pages).
All extracted completely and were removed only after verification:

```text
Local files imported: 7
Removed: 7
Retained: 0
Emails found: 651
Phone numbers found: 1484
Unique contacts added: 2087
Duplicates skipped: 658
Errors: 0
```

Canonical data/contacts.csv now has 2,196 unique pairs/IDs: 697 emails and 1,499
phones. All 109 original IDs, named/details/source/status/contacted/response
fields and existing notes were preserved; additions have the approved defaults.
All discovered method pairs are verified in the saved CSV. The seven source
hashes match the pre-import inventory; their complete evidence JSON remains.
Exact removed paths are retained privately in data/local_imports.json, as scoped
by the approved prompt; no private source inventory is copied into tracked docs.
The links.failed/ input directory remains, empty. No replacement raw copies.

All 36 protected source/evidence/state files passed hash-preservation checks,
including links.txt, links.failed.txt, the crawl checkpoint and blocked audit.
No web retries or model requests occurred. The 479 queued web URLs remain outside
this local import. No app/service, outreach, commit or push operations.

Private before/after verification is in data/task103-local-before.json and
data/task103-local-verification.json. Updated active context and research READMEs.
Final syntax/CSV/cleanup checks, all 25 relative documentation links, offline
--check, Git ignore coverage and git diff --check passed. Both writer locks are
released; the seven input files are absent and their verified evidence remains.

## Completion review

On the owner's continuation request, inspected the existing CSV/import report and
recorded checks: 2,196 contacts, seven verified removals, no remaining local inputs,
58 collection checks and 33 extension checks. Marked both approved prompts complete.
Corrected the research README's local-import section reference. A read-only direct
GET /v1/models was denied by the sandbox (Windows 10013); the authorized check
outside it received connection refused (10061). The configured LM API remains
unavailable; no inference, model loading or server changes occurred. No extra
crawl or CSV rewrite was needed, and outreach remains outside this completed scope.

## Owner-requested academic-email cleanup

The owner explicitly requested a simple direct CSV edit before moving on.
Removed 54 email rows whose normalized domain is ac.za or ends with .ac.za.
No phone rows were inferred to belong to universities or removed based on their
publishing site. Remaining CSV: 2,142 unique contacts (643 emails, 1,499 phones).
All retained rows, IDs, field values and order match the pre-filter rows exactly.
Used the existing contact lock, exact-header loader and guarded atomic writer;
verified the result has no matching email rows and all phone records are intact.

Private recovery/audit data is in data/task103-academic-email-removal.json,
including removed rows and before/after hashes. Updated current context and
research README. No new feature, crawler rerun, outreach, commit or push; the
source evidence remains. Future collection must honor the owner's exclusion
preference; no ingestion-code filter was added during this manual-only request.
