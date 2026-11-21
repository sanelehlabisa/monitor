# Market-research pipeline

Local workspace for a planned Python tool finding public business contacts at
student accommodation providers, property managers and landlords. Workspace
setup, resumable collection and in-memory HTML/plain-text/PDF extraction are
implemented. The first milestone will produce one contacts CSV with short,
factual context. Contact refinement, LM Studio and outreach remain later tasks.

## Workspace and privacy

Use this folder for the whole experiment. One typed `pipeline.py` provides the
entrypoint. `requirements.txt` pins the research-only `pypdf==7.1.1` reader;
HTML/plain text and setup/check modes use the standard library. Use the local `.venv/`.
Split helpers only when useful. No application imports, production dependencies,
database, queue, browser automation, vector store or agent framework.

Workspace layout; the contacts CSV and environment are later additions:

```text
market-research/
  README.md
  .gitignore
  pipeline.py
  requirements.txt
  links.txt
  .venv/
  data/
    contacts.csv
    crawl_state.json
    crawl.lock
    evidence/
  drafts/
  logs/
```

`data/contacts.csv` is the sole contact register. Crawl state stores URL progress
and resource/extraction status, not a second contact database. Keep useful extracted
text, source evidence and summaries privately. The crawler extracts directly
from bounded response bytes and saves extracted JSON, without new original
HTML/PDF/binary copies. Existing captures from earlier tasks stay intact.
Inputs, CSVs, existing captures, excerpts, prompts/results, drafts, logs,
temporary files and credentials stay here and out of Git. Logs avoid contact
details and secrets. Retention/cleanup is manual and documented; never delete
the working contact register automatically.

The local `.gitignore` excludes everything except explicitly reviewed source,
requirements and instructions. Verify exclusions before the first data run and
whenever adding output paths. Do not force-add private files or paste records
into work reports. Ignore rules do not remove previously tracked files or provide
encryption. Application Docker builds do not include this sibling directory.

## Setup

Create the isolated research environment from the repository root:

```powershell
cd software/research/market-research
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe pipeline.py --init
.venv/Scripts/python.exe pipeline.py --check
```

On Linux/macOS use `.venv/bin/python`. Setup/check modes also work without the
PDF dependency. Paths resolve relative to the script regardless of the calling
folder. The owner's existing `links.txt` is the
default input; it has 16 entries passing syntax checks. Initialization creates
missing private folders and only creates a comment-only seed template if absent.
It never overwrites existing files. Checks report counts, not URLs.

`--check` checks directories, temporary write access and seed syntax without
network access. It returns 0 on success, 1 for missing/invalid workspace inputs;
invalid command options return 2. This mode makes no crawl, DNS, robots or model
request. It does not create the final CSV.

Use `--help` for options. `--seeds` and `--data-dir` must resolve inside this
experiment, including through existing links/junctions. An alternative private
seed file can be selected with `--seeds data/seed_urls.txt`. Crawl defaults
are depth 2, 50 pages per seed, 200 requests per run, 15-second request timeout
and a 1-second delay, plus 5 MiB per resource. PDF work is limited to 100 pages,
1,000,000 text characters, bounded decoded streams and a 15-second between-page
budget. Individual parser calls are not pre-empted. `--max-pages` and
`--max-text-chars` adjust reader limits. Robots requests, redirects and failed
request attempts consume the total request budget.

## Crawl and resume

From this research folder with its virtual environment:

```sh
# First run only; refuses to replace an existing checkpoint.
.venv/Scripts/python.exe pipeline.py --crawl --max-requests 5

# Continue saved work with a fresh per-run budget.
.venv/Scripts/python.exe pipeline.py --resume --max-requests 5
```

The local Task 100 smoke checkpoint already exists, so use `--resume` here.
The seed file must match that checkpoint. Use another private `--data-dir` for
a different batch instead of deleting existing evidence/state.
Already-fetched legacy nodes are not automatically reprocessed when readers
change. New responses use the new extraction path; use a separate private batch
when an explicitly authorized re-fetch is needed.

Initial scope is exact seed hostnames plus their `www` equivalents, without
implicitly allowing every subdomain. Add a related host with repeatable
`--allow-host provider.example`. External links remain recorded with reason
`scope` until allowed. Raise `--max-depth` to release depth-limited branches.
Page/request counters reset on each run; completed URLs stay deduplicated.
Redirects add no graph depth, are capped at five hops, and cannot downgrade HTTPS.
Cycles and alternate parent links are retained without repeated resource fetches.

The crawler checks public DNS addresses and connects to a checked address, using
normal hostname/certificate verification for HTTPS. It uses direct connections
to standard HTTP80/HTTPS443, without environment proxies or authentication.
Timeouts cover socket operations/body reading; OS DNS resolution can take longer.
HTML text, links and email candidates are extracted without running scripts.
Each successful response is dispatched to HTML, plain text or PDF extraction in
memory. Titles, text, email candidates with nearby/page evidence and discovered
URLs share one result shape. PDF annotations and text URLs feed the same graph.
Readers do not fetch their own source again or require a saved input file.

Extraction JSON uses content-derived names under `data/evidence/`; different
limits/results preserve earlier outputs. Original response bytes are not saved.
Unsupported, encrypted, textless, malformed, partial and missing-reader outcomes
are explicit and not automatically refetched. A future reprocess may require a
new authorized request. PDF imports are lazy; missing `pypdf` does not prevent
other readers from running. No OCR or document scripts are executed.

Robots rules include wildcard/end matches, longest-path selection and merged
matching user-agent groups. Successful policies are cached privately for up to
24 hours. Per-host waits and Retry-After backoffs survive resume. Waits over
30 seconds leave work deferred instead of blocking the process for a long sleep.
Each resource gets at most two failed attempts across runs. Restrictions, errors,
unsupported encodings and oversized files remain recorded; they are not bypassed.

State uses temporary-file replacement and an exclusive `crawl.lock`. Normal exit
and Ctrl+C release the lock. After a hard crash, first confirm no writer remains
before manually removing that exact stale lock. Invalid state is preserved for
manual recovery. Raw files and extraction JSON use generated hash filenames under
`data/evidence/`; no final contacts CSV is created yet.

Task 100's five-attempt public smoke fetched one HTML page and saved 76 resources:
72 pending and three failures (one unavailable robots response and two robots
redirect-loop outcomes). This verifies a bounded run, not coverage of every seed.
Private source URLs, emails and page contents stay out of Git and terminal reports.

Each processed node keeps its two latest bounded diagnostic records. They contain
request stage, HTTP status, redirect Location, network error class and outcome.
TLS verification errors retain the verification code/message privately. No cookies,
response bodies or source URLs are printed in the console summary.

### Access findings and limits

Task 100 reached four of 16 seed URLs, so its initial three error labels did not
establish whether most seeds had access problems. That baseline remains private
in `data/task100-access-review.json`.

Task 101 reviewed all 16 seeds in one seed-only batch of 16 request attempts
(maximum 32). Five seeds were downloaded: four HTML resources and one PDF awaiting
a reader. Nine seeds failed because their robots URL redirected to itself, one
failed TLS certificate verification, and one target returned HTTP 403. These are
observed outcomes for seed URLs, not proof of permanent site inaccessibility.
The 348-node graph still has 332 pending links; depth-zero review did not crawl them.

Two crawler defects were demonstrated with synthetic responses/wire captures.
Missing redirect Location is now distinguished from self/cyclic redirects.
The HTTPS Host header now matches the normalized URL authority, avoiding an
unnecessary :443 added by the underlying HTTP connection class. This second fix
was made after the live batch; its effect on the nine self-redirects is unverified.
A separate bounded recheck is needed before attributing these redirects to the sites
or starting a broad collection run. TLS/restriction checks remain enforced.

Exact old/current outcomes and request diagnostics are in ignored
`data/task101-access-review.json`, with the fix timing recorded. The original
checkpoint snapshot is `data/task101-state-before.json`. Seeds, the Task 100
review and pre-existing evidence were preserved byte-for-byte. Existing retry
counters were not reset and no second live batch was run.

The owner has deferred access fixes for now. Private `links.failed.txt` contains
the 11 failed/restricted seed URLs, with comments distinguishing nine robots
self-redirects, one TLS failure and one HTTP403. The list records pre-Host-fix
observations, not confirmed robots.txt bans. It is ignored by Git and can be used
for later manual review. The crawler now loads it automatically, skips its URLs
before scheduling and enforces it again before requests/redirects. Original
failure/retry history is preserved; pending matches show `manual_review`.
Remove an entry only when its retry is explicitly intended; no counter is reset.

Task 102's isolated live check used five request attempts and extracted one PDF
and two HTML pages completely, with 287 discovered nodes and 284 still pending.
It created no raw-document copies and retried no manual-review URL. Results are
private in `data/task102-live/` and `data/task102-verification.json`; original
seeds, checkpoint, reports and existing captures passed hash-preservation checks.

## First milestone — Tickets 71.1–71.7

After individually approved slices, the user can enter several seeds, run one
Python command and obtain unique contacts with traceable context. Stop for review
before survey work or outreach. Tickets 71.1, 71.2 and access review 71.2.1 are
complete within their scopes. Ticket 71.3 now covers HTML/plain-text/PDF responses;
contact context, enrichment, cleanup and CSV remain open.
Task 099's approved
[workspace prompt](../../../agents/work/099-market-research-workspace/prompt.md)
covers setup only. The owner's seed file is already present for 71.2.
The approved [crawler prompt](../../../agents/work/100-resumable-research-crawler/prompt.md)
covers 71.2; [results](../../../agents/work/100-resumable-research-crawler/changes.md)
record isolated checks and the bounded public run.

## Traversal and reading

Every seed is a root. Sites form a graph with cycles and shared targets, so visit
each unique resource while following every discovered in-scope link, even when
the parent has no contact email. Retain parent/source links and the pending queue.
Run limits pause work without discarding unexplored branches; resume continues
until the queue is empty or the user stops it. Report counts of pending, blocked,
failed and unreadable nodes. Never claim a complete crawl while work remains.

The initial scope is the seed organisations and explicitly related public sites,
as in the brief. Confirm external boundaries with the seed file before crawling.
All reachable paths means all paths within that scope and site restrictions,
not unrestricted expansion to the whole web.

The implemented flow is fetch URL → detect response type → extract information in
memory → save useful results and continue through discovered links. The response
still transfers over the network; an original file saved to disk is not required.
Use small format handlers with a shared result shape, initially HTML, plain text
and PDF. Results contain source URL/type, explicit title, extracted text, email candidates,
links and extraction status. Do not hardcode a particular file or URL.

Record unsupported, encrypted, textless, oversized, partial or failed extraction
explicitly. Add readers for other encountered formats as small later changes;
do not claim arbitrary files are readable. New raw originals are not saved
by default, so later reprocessing may need another authorized fetch. Existing
captures are preserved. Embedded scripts and OCR remain out of scope.

### 71.1 — Local workspace (complete)

- Create the entrypoint, isolated dependencies and private directories above.
  Resolve paths relative to this folder regardless of the calling directory.
  Keep configured output paths inside this experiment too.
- Document one run command and configurable depth (initially 2), page budget per
  seed, request timeout and delay. Use ordinary Python libraries where practical.
- Check ignored paths using fictional inputs, without any network request.

### 71.2 — Resumable link traversal (complete)

Depends on 71.1.

- Use the owner's existing private links.txt before the first real run. Read
  nonblank, non-comment seed lines. Fetch public HTTP(S) resources, extract HTML
  visible text, public emails/`mailto:` values and links for the traversal queue.
- Deduplicate URLs/emails. Prefer same-organisation pages; follow relevant
  external providers only within explicitly allowed domains and the same depth
  and page budgets. Count redirects/retries toward finite request limits too.
- Respect robots/site restrictions, delays, timeouts and response-size limits.
  No login/paywall bypass, JavaScript execution or private/local network targets,
  including redirects. Skip unsupported content with a concise reason.
- Save private crawl progress for restart. Interrupted/in-flight pages can be
  retried within limits; failures do not terminate unrelated seeds. Store graph
  edges, fetched-file metadata and extraction status locally. Do not discard
  discovered links at a depth/page cutoff; retain them as pending or explicitly
  blocked until the relevant limit changes. Deduplicate nodes without losing
  discovery paths. Check cycles, shared targets, paused branches, resume,
  restrictions and a successful local/manual run.

### 71.2.1 — Crawl access diagnostics (complete)

The approved [Task 101 prompt](../../../agents/work/101-crawl-access-diagnostics/prompt.md)
and [results](../../../agents/work/101-crawl-access-diagnostics/changes.md) record
the diagnostic changes, live outcomes and post-review header fix. Remote behavior
after that fix remains unverified; no additional batch is authorized by this result.

- Inspect the three recorded failures with private HTTP status/redirect-chain
  and network-error details. Distinguish site restrictions, unavailable robots,
  transport errors and crawler defects; do not infer the cause from a generic label.
- Preserve current state, evidence and the private seed review. Keep diagnosis
  details private and report aggregate seed coverage separately from discovered links.
- Use synthetic responses first. After prompt approval, run one bounded seed-only
  review of at most 32 request attempts, including robots/redirects. Stop and report
  untested seeds if the budget ends. No restriction bypass or unlimited retries.
- Fix only demonstrated crawler defects, then document accessible/failed/untested
  seeds and remaining limits before document-reading work or a broad crawl.

### 71.3 — Extract content during crawling (complete)

Depends on 71.2.

The [Task 102 prompt](../../../agents/work/102-offline-document-reading/prompt.md)
was revised and approved. Extraction happens as each crawl response arrives,
without requiring a saved document or an offline workflow. See the
[Task 102 results](../../../agents/work/102-offline-document-reading/changes.md)
for checks and scope limits.

- Reuse HTML parsing and dispatch bounded response bytes to a small suitable
  reader based on type/signature. Add plain-text/PDF support first, using isolated
  dependencies where needed; additional encountered formats get small later readers.
- Extract text, email candidates, links, explicit title and page/nearby context
  into the same result shape. Queue links through existing crawl budgets.
- Save useful extracted results/provenance privately, without new original
  HTML/PDF/binary copies by default. Preserve existing captures and checkpoint data.
- Honor links.failed.txt without resetting old outcomes; verification was one
  five-attempt batch using successful seeds only, within the approved scope.
- Check response limits, unsupported/malformed/textless/encrypted resources,
  missing readers and partial extraction. No repeated fetch loop, OCR or guessed facts.

### 71.4 — Evidence-based context

Depends on 71.3.

- Capture the exact email-bearing page/PDF URL, source domain, title, nearby
  heading/paragraph and explicit name, organisation, role and location.
- Leave unknown fields blank. A Gmail/Outlook/Yahoo address does not identify
  its organisation; use the source context instead.
- Retain a bounded excerpt for review. Prefer clearer, directly associated
  evidence when duplicates occur; preserve the email-bearing source provenance.
- Review fictional and approved public examples for ambiguous names and multiple
  contacts. Do not infer roles or locations from unrelated nearby text.

### 71.5 — Required LM Studio enrichment

Depends on 71.4.

- LM Studio is already installed; inspect the available local model/hardware.
  This stage is required, not an optional ticket. Use its local
  OpenAI-compatible API with an explicitly selected lightweight instruction model.
  The owner has LM Studio open and requests a small Qwen model, approximately
  1.3B parameters. Confirm the actual installed model identifier and size before
  selecting it; do not guess a model name. No download or cloud service is assumed.
- Submit only the relevant bounded excerpt. Expect validated JSON with
  `name`, `organisation`, `role`, `location`, `details`; details is one short
  sentence. Keep unknowns empty and reject unsupported claims.
- Also produce short source-linked summaries of readable collected documents
  for the owner's review. Chunk long text only as needed, retaining evidence and
  distinguishing missing facts. These private summaries are not another contact CSV.
- Treat retrieved text as untrusted data, never commands. The model has no tools
  or authority to send messages. Bound response size, timeouts and retries.
- If offline, invalid or unavailable, keep crawling and preserve deterministic
  context, but mark enrichment pending/failed and resume it later. Never report
  fallback text as model output or consider this ticket complete without a
  successful local-model run. Check factual summaries, invented fields, malformed
  responses, outage recovery and enrichment resume.

### 71.6 — Contact cleanup

Depends on 71.5.

- Normalize email casing/whitespace, validate syntax, exclude obvious placeholders
  and deduplicate by normalized email before persistence.
- Prefer clearly published business/research contacts. Do not treat publication
  as permission to send mail. Optional DNS checks must not reject on transient
  lookup failures; no SMTP mailbox probing.
- Keep the strongest source context for repeated contacts; conflicting nonempty
  fields require review rather than guessing. Check malformed, repeated,
  free-mail and placeholder examples.

### 71.7 — Restartable contacts CSV

Depends on 71.6. This completes the first milestone.

Use exactly one canonical CSV, initially with these columns:

```text
id,email,name,organisation,role,location,details,source_url,source_domain,status,email_sent,sent_at,response_status,notes
```

- Assign stable sequential integer IDs to new unique emails; never renumber
  existing rows. Start with `status=new`, `email_sent=false`, empty `sent_at`
  and `response_status`.
- Upsert by normalized email. Fill missing context but preserve manual edits,
  notes and all sending/response fields. Offer stronger conflicting context for
  review instead of overwriting it. Never reset a sent/suppressed contact.
- Use UTF-8, CSV quoting and same-folder temporary-file replacement. Preserve the
  original on malformed input/write failure and keep only one process writing.
  Handle spreadsheet formula characters safely without silently changing facts.
- Save contacts before checkpointing a page complete so interruption can replay
  it safely. Print counts only for pages, PDFs, emails, new contacts, duplicates
  and errors. Logs/state remain private.
- Verify several approved seeds, restart, duplicate discovery, manual edits,
  existing sent/response rows and interrupted writes. Present aggregate results
  and a local review location, never contact records in Git.

## Later — separate approval required

### 71.8 — Survey review

After 71.7 review, locate the owner's existing survey; ask for its path/link if
unavailable. Keep questions short and neutral. Cover approximate scale, geysers
and high loads, control methods, waste, tenant/prepaid issues, existing solutions,
financial impact and optional follow-up. Review for leading/product-sales wording.
Do not publish or distribute it during this ticket.

### 71.9 — Research email drafts

After 71.8, read the CSV and create private drafts with recipient, subject, body
and personalization evidence. Write as Sanele, an individual researcher/builder.
Use real context, a short problem-discovery request and the reviewed survey only
if supplied. No invented facts or random variations. Manual review only, no sending.

### 71.10 — Controlled sender

Blocked until 71.9 is reviewed, 71.11 is complete and the owner explicitly
authorizes a sending run and its recipients/content.

- Send only the exact approved drafts to approved contacts. Skip sent and
  do-not-contact/opted-out rows. Configure a small per-run/daily cap and bounded
  delays for rate control, never filter evasion. No bulk bursts or indefinite retry.
- Record attempt state in the same CSV before sending. Confirmed success sets
  `email_sent=true`, UTC `sent_at`, `status=sent`; definite failure sets
  `status=send_failed`. Uncertain SMTP/crash outcomes require manual reconciliation
  before retry, because SMTP and CSV updates cannot be atomic.
- Persist each outcome. Verify stop/resume and failure paths with a local mail
  capture before any real outreach. Respect opt-outs and document appropriate
  permission/contact scope before the first real batch.

### 71.11 — Sending-domain readiness

Run after draft review and before 71.10 sending. Confirm the actual sender/domain,
preferably a named address such as `sanele@roventics.com` if available.
Read-only checks cover SPF, DKIM, DMARC, sender alignment and SMTP configuration.
Report configured/missing items without exposing credentials, changing DNS or
sending mail. Check current authoritative guidance during implementation.

The numbering preserves the supplied brief; the later execution order is
71.8 → 71.9 → 71.11 → 71.10.
