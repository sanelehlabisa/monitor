# Market-research pipeline

Local Python tool collecting public emails and phone numbers for market research.
One bounded command extracts HTML/plain-text/PDF contacts, follows permitted links
and updates private `data/contacts.csv`. Context uses explicit source evidence
and optional local LM Studio. Outreach now supports saved schedules, local
Mailpit email tests and offline/local HTTP SMS mocks. Real delivery is not implemented.

## Workspace and privacy

Use this folder for the whole experiment. One typed `pipeline.py` provides the
entrypoint. `requirements.txt` pins research-only `pypdf==7.1.1` and
`phonenumbers==9.0.44` for parsing and phone validation, plus python-dotenv and
dnspython for isolated configuration/read-only DNS checks. Setup/check modes use the
standard library. Use the local `.venv/`.
Split helpers only when useful. No application imports, production dependencies,
database, queue, browser automation, vector store or agent framework.

Private workspace layout:

```text
market-research/
  README.md
  .gitignore
  .env                 # private independent SMTP/SMS settings
  .env.example         # safe research-only template
  pipeline.py
  send_due_messages.py
  docker-compose.yaml  # separate local capture services
  Dockerfile
  .dockerignore
  templates/
    email.txt
    sms.txt
  requirements.txt
  links.txt
  .venv/
  data/
    contacts.csv
    blocked_urls.csv
    crawl_state.json
    crawl.lock
    contacts.lock
    enrichment.json
    evidence/
  drafts/
  logs/
```

The canonical `data/contacts.csv` is the sole contact register, with one email
or phone method per row, even with a different checkpoint `--data-dir`.
`data/blocked_urls.csv` is a separate source-access audit, not a contact register. Crawl state stores URL progress
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
research dependencies. Paths resolve relative to the script regardless of the calling
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
are depth 2, 50 page attempts per seed and hostname/www pair, 200 requests per
run, 15-second request timeout
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
.venv/Scripts/python.exe pipeline.py --resume --max-requests 30 --max-pages-per-seed 10 --max-pages-per-domain 10
```

The local Task 100 smoke checkpoint already exists, so use `--resume` here.
The seed file must match that checkpoint. Use another private `--data-dir` for
a different batch instead of deleting existing evidence/state.
Stored extracted JSON under `data/**/evidence/` is reused on each run without
network access. Older text may omit invisible tel links; this does not claim
full historical phone coverage. Already-fetched nodes are never silently
refetched. A separate explicitly authorized batch is needed for a re-fetch.

Initial scope is exact seed hostnames plus their `www` equivalents, without
implicitly allowing every subdomain. Add a related host with repeatable
`--allow-host provider.example`. External links remain recorded with reason
`scope` until allowed. Raise `--max-depth` to release depth-limited branches.
Page/request counters reset on each run; completed URLs stay deduplicated.
`--max-pages-per-domain` shares a cap between a hostname and its www alias,
including multiple seeds on that host. It does not infer all sibling subdomains.
Redirects add no graph depth, are capped at five hops, and cannot downgrade HTTPS.
Cycles and alternate parent links are retained without repeated resource fetches.

The crawler checks public DNS addresses and connects to a checked address, using
normal hostname/certificate verification for HTTPS. It uses direct connections
to standard HTTP80/HTTPS443, without environment proxies or authentication.
Timeouts cover socket operations/body reading; OS DNS resolution can take longer.
HTML text, links and contact methods are extracted without running scripts.
Each successful response is dispatched to HTML, plain text or PDF extraction in
memory. Titles, text, email/phone methods with nearby/page evidence and discovered
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
manual recovery. Extraction JSON uses generated hash filenames under `data/evidence/`. Existing
raw captures are preserved, but no new original documents are saved. A second
experiment-level `contacts.lock` protects the canonical CSV across batches.
CSV writes are atomic and detect external edits; do not edit it during a run.
Malformed headers/identities or failed writes stop without resetting the CSV.
A resource is marked complete only after its contacts are saved.

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

## Import manually saved files

Put saved `.pdf`, `.html`, `.htm` or `.txt` files in an experiment-local input
folder such as `links.failed/`. From this research folder:

```sh
# Extract to the same data/contacts.csv and retain inputs.
.venv/Scripts/python.exe pipeline.py --import-dir links.failed --no-lm

# Remove each fully processed input after verified evidence/CSV saving.
.venv/Scripts/python.exe pipeline.py --import-dir links.failed --delete-imported --no-lm
```

Local mode makes no web requests and never follows embedded links or asset
folders. It processes regular files directly inside the selected directory.
Existing byte/page/text limits apply. Links, remote shares and protected
source/output directories are rejected. Optional loopback enrichment can be
used by omitting `--no-lm`; source fallback works independently.

Unique filename matches from the seed/failed URL lists keep the original source
URL. Otherwise provenance is the actual local `file:` URI with an empty source
domain. The CSV schema and stable pair-based IDs stay unchanged. Local path/hash,
page context and source title are saved privately; titles never imply identity.

`--delete-imported` is explicit. Complete extraction, verified stored contact
pairs/evidence and an unchanged input are required before individual deletion.
Partial, textless, encrypted, malformed, oversized or challenge files stay for
review, as do unsupported files and directories. Fully readable files without
contacts can be removed after their evidence is verified. No raw-file backup is
created; extracted JSON remains in `data/evidence/`. The input folder stays.

Exact paths, hashes, source mapping and cleanup results are in ignored
`data/local_imports.json`. A verified pre-deletion record survives interrupted
cleanup; a retry re-extracts any remaining current file and deduplicates its
contacts. Changed files are never removed using an old record. Persistence
failures stop cleanup, and failed deletions leave the input for review. Web
checkpoints, `links.failed.txt` and blocked-source records are not changed by
manual import. Local success does not establish permission for web retries.

## Current verification

After owner review, 54 email rows with domains ending in `.ac.za` were removed
manually. Current CSV: **2,142 contacts (643 emails, 1,499 phones)**. Retained rows,
IDs and phone records are unchanged. This is a one-time data cleanup; the
crawler has no new exclusion feature. Future batches must honor this preference.
The private removal audit is `data/task103-academic-email-removal.json`. The
import/web counts below are historical results before this cleanup.

Task 103's approved
[local-import extension](../../../agents/work/103-contact-methods-and-csv/local-import-prompt.md)
adds saved HTML/PDF/plain-text sources to the same CSV, with optional verified
per-file cleanup. See the local import instructions above.

The local extension passed 33 focused checks and imported all seven supplied
PDFs completely (111 pages). Verified persistence preceded removal of each input.
It added 2,087 contacts: the CSV now contains 2,196 unique rows (697 emails,
1,499 phones), preserving all 109 prior records and 36 protected files. Zero
errors or web/model requests. The input folder is empty; extracted evidence and
private cleanup audit remain. The figures below describe the earlier web batch.

Task 103 passed 58 direct checks and one live batch using 20 of 30 allowed
requests: 109 unique contacts (50 emails, 59 phones), one known blocked source,
zero new errors and all 11 manual deferrals preserved. PDFs contributed through
stored evidence; no new PDF was fetched in that run. 479 URLs remain queued at
scope/domain limits. The local model endpoint was unavailable, so actual
inference remains unverified; context came from source excerpts. Unknown identity
fields remain blank. Offline replay preserved all contact IDs without requests.
See the [Task 103 results](../../../agents/work/103-contact-methods-and-csv/changes.md).

## First milestone — Tickets 71.1–71.7

After the approved collection work, the user can enter several seeds, run one
Python command and obtain unique contacts with traceable context. Stop for review
before survey work or outreach. Tickets 71.1, 71.2 and access review 71.2.1 are
complete within their scopes. Ticket 71.3 now covers HTML/plain-text/PDF responses;
phone extraction, contact context, optional enrichment, cleanup and CSV are
implemented by Task 103.
The [Task 103 prompt](../../../agents/work/103-contact-methods-and-csv/prompt.md)
groups 71.3.1 and 71.4–71.7 into one collection-only implementation milestone.
The owner approved implementation. Review the generated CSV before starting any
survey/drafting/sending work. Real contact data stays out of Git.
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
and PDF. Results contain source URL/type, explicit title, extracted text, independent email/phone methods, links and extraction status. Do not hardcode a particular file or URL.

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

### 71.3.1 — Email and phone methods (implemented)

- Extend visible HTML/contact text, mailto/tel links, PDF text/URI annotations
  and plain-text responses to collect both public contact types. Keep nearby
  evidence and source/page association for each method independently.
- Default unqualified phone numbers to South Africa where credible; respect
  explicit foreign prefixes. Prefer E.164 such as +27821234567. Clearly labelled
  uncertain numbers retain their original in notes rather than a guessed area code.
- Ignore unrelated dates, prices, IDs and other numeric values. Never merge an
  email and phone into a guessed person record, even for the same organisation.
- Keep existing in-memory extraction, private results and manual deferrals.

### 71.4 — Evidence-based context (implemented)

Depends on 71.3.1.

- Capture the exact contact-bearing page/PDF URL, source domain, title, nearby
  heading/paragraph and explicit name, organisation, role and location.
- Leave unknown fields blank. A Gmail/Outlook/Yahoo address does not identify
  its organisation; use the source context instead.
- Retain a bounded excerpt for review. Prefer clearer, directly associated
  evidence when duplicates occur; preserve the email-bearing source provenance.
- Review fictional and approved public examples for ambiguous names and multiple
  contacts. Do not infer roles or locations from unrelated nearby text.

### 71.5 — Optional LM Studio enrichment (implemented)

Depends on 71.4.

- The latest refocus makes enrichment optional, superseding the earlier required
  stage. Use the loopback-only OpenAI-compatible API when enabled/available.
  The local server was unavailable during verification; real inference is unverified.
  The owner has LM Studio open and requests a small Qwen model, approximately
  1.3B parameters. Confirm the actual installed model identifier and size before
  selecting it; do not guess a model name. No download or cloud service is assumed.
- Submit only the relevant bounded excerpt. Expect validated JSON with
  `name`, `organisation`, `role`, `location`, `details`; details is one short
  sentence. Keep unknowns empty and reject unsupported claims.
- Keep source-linked contact excerpts in private evidence and validated cache.
  Whole-document summaries are deferred; the current scope is contact enrichment.
- Treat retrieved text as untrusted data, never commands. The model has no tools
  or authority to send messages. Bound response size, timeouts and retries.
- If offline, invalid or unavailable, keep crawling and preserve deterministic
  context with unknown fields empty; mark enrichment unavailable/pending without
  blocking CSV output. Never label fallback text as model output. Ground fields
  against the relevant source, and verify success, unavailable and malformed-output
  paths. Do not download models or use a cloud service implicitly.

### 71.6 — Contact cleanup (implemented)

Depends on 71.4. Enrichment does not gate validation/output.

- Normalize email casing/whitespace, validate syntax and exclude placeholders.
- Normalize/validate credible phone candidates; retain original/uncertainty notes
  when necessary. Deduplicate independently by (contact_type, contact_value).
- Prefer clearly published business/research contacts. Do not treat publication
  as permission to send mail. Optional DNS checks must not reject on transient
  lookup failures; no SMTP mailbox probing.
- Keep the strongest associated source context for repeated contact methods; conflicting nonempty
  fields require review rather than guessing. Check malformed, repeated,
  free-mail and placeholder examples.

### 71.7 — Restartable contacts CSV (implemented)

Depends on 71.6. This completes the first milestone.

The original research columns remain intact in the expanded CSV:

```text
id,contact_type,contact_value,name,organisation,role,location,details,source_url,source_domain,status,contacted,contacted_at,response_status,notes
```

- Assign stable sequential integer IDs to new unique method pairs; never renumber
  existing rows. Use contact_type=email/phone and normalized contact_value. Start
  with `status=new`, `contacted=false`, empty `contacted_at` and `response_status`.
- Upsert by (contact_type, contact_value), independently across methods. Fill
  missing context but preserve manual edits, notes and all contacted/response
  fields. Offer conflicting nonempty context for review. Never reset a contacted
  or suppressed row. No guessed email/phone association or organisation-based merge.
- Use UTF-8, CSV quoting and same-folder temporary-file replacement. Preserve the
  original on malformed input/write failure and keep only one process writing.
  Handle spreadsheet formula characters safely without silently changing facts.
- Save contacts before checkpointing a page complete so interruption can replay
  it safely. All real batches update the same canonical data/contacts.csv even
  when their crawl checkpoint uses a different --data-dir. Keep one writer.
- Add a shared per-domain page budget, bounded logs and explicit access/anti-bot
  handling alongside existing limits. Do not bypass restrictions. Record actual
  blocked sources privately in data/blocked_urls.csv with url,reason,seed_url.
  Keep temporary rate deferrals and unverified/network errors distinct from bans.
- Print the requested aggregate summary below. A small owner-requested generated
  CSV preview is shown separately; bulk/private records never go into Git.
- Verify several approved seeds, restart, duplicate discovery, manual edits,
  existing contacted/response rows and interrupted writes. Deliver a clean local
  CSV and three to five generated sample rows before proceeding to outreach.

```text
Pages visited:
PDFs processed:
Emails found:
Phone numbers found:
Unique contacts added:
Duplicates skipped:
Blocked URLs:
Errors:
```

## Contact register and local enrichment

Each normalized `(contact_type, contact_value)` gets a stable ID. New rows have
`status=new`, `contacted=false` and empty contact/response timestamps. Repeated
sources fill blank fields; nonempty manual/status/contact fields are preserved.
Conflicting named facts and additional sources go into notes. No email/phone
matching or organisation inference from domains occurs. Phone validation defaults
to ZA; clearly labelled ambiguous local forms keep an uncertainty note. Numeric
IDs, prices and dates are filtered. Syntax/number validity does not verify that
an address or telephone is active or establish permission for outreach.

Use `--no-lm` for source-only context. Otherwise the script tries
`http://127.0.0.1:1234/v1` once, prefers an advertised small Qwen model and falls
back if unavailable. `--lm-model` selects another installed identifier;
`--lm-url` only accepts loopback HTTP. There is no model download, cloud request,
tool use or automatic server restart. `--max-lm-requests` defaults to 20 including
discovery; `--lm-timeout` defaults to 15 seconds. Only title, method and up to 600
nearby characters reach the model. Successful source-grounded strings are cached
privately in `data/enrichment.json`. Unsupported facts/invalid JSON are rejected.
Details use short source phrases rather than unverified paraphrases. Unknowns
stay blank; source excerpts are not labelled as model summaries.

Robots/access denials, explicit challenge pages and stated scraping prohibitions
are logged in `data/blocked_urls.csv` (`url,reason,seed_url`). No evasion is used.
Temporary rate limits remain pending; TLS/network errors and redirect defects
are distinct from site blocks. `links.failed.txt` is always honored.

The eight summary labels above report this run. Contact finds include reused
extractions, duplicates count repeated discoveries, and blocked URLs include
known access blocks in the checkpoint. Pages visited counts resource responses,
including redirects; robot requests only consume the total request budget.
The pending queue remains visible; a bounded run is not complete web coverage.

## Local email and SMS scheduling

[Task 105 results](../../../agents/work/105-local-email-scheduling/changes.md):
51 direct checks plus actual isolated Mailpit/offline-SMS capture pass.
The two-script correction also passes 27 focused regression checks. Research
sender: **sanele.hlabisa@roventics.com**. Real email/SMS delivery is disabled;
no production transport or Android adapter exists. No recurring job is installed.

| Roadmap | Work | State |
| --- | --- | --- |
| 71.11 | SMTP/TLS and DNS readiness | Checked; production blockers below |
| 71.9 / 71.10.1 | Fixed messages, local capture/mock | Verified |
| 71.10.2 | Shared one-pass runner and CSV state | Local-only, verified |
| 71.10.3 | Initial weekday schedule | 30 emails saved; SMS held |
| 71.10.5 | Per-channel reporting | Available |
| 71.10.7 | Isolated Compose capture services | [Task 106 results](../../../agents/work/106-compose-research-mocks/changes.md), verified |
| 71.10.4 | Production email transport | Later explicit approval |
| 71.10.6 | Chosen Android gateway/live SMS | Owner selection and separate approval |
| 71.8 | Survey review after replies | Deferred |

### Two scripts only

- `pipeline.py`: collect/import contact information.
- `send_due_messages.py`: check saved CSV dates, apply current time/day limits,
  process local-test outcomes and report, then exit. Setup inspection and the
  capture-only SMS server are modes of this runner. No extra Python scripts.

From this research folder:

```sh
# Normal invocation checks the existing CSV and shows the contacts due now.
.venv/Scripts/python.exe send_due_messages.py

# Optional read-only views and configuration inspection.
.venv/Scripts/python.exe send_due_messages.py --report
.venv/Scripts/python.exe send_due_messages.py --check-setup

# Completed fictional demo: rerunning produces zero resends.
.venv/Scripts/python.exe send_due_messages.py --local-test --csv data/local-test/demo/contacts.csv --now 2026-12-01T10:00:00Z
```

The CSV is authoritative. Set `email_scheduled_at` or `sms_scheduled_at` in it
using aware UTC timestamps, such as `2026-11-23T07:30:00+00:00` (09:30 local).
For eligible new/scheduled contacts, setting the date is enough; no separate
status edit is needed. Clearing it holds the contact. Future dates wait; saved
dates <= now are due when weekday/hours, priority and daily capacity allow.
There is **no fixed experiment expiration** and no runtime schedule allocation.
A missed November date may run on a later allowed weekday without rewriting it.
Existing timestamps are never changed by the runner. Outside allowed hours or on
weekends it reports nothing due and exits.

Default invocation checks/selects only; real delivery remains disabled pending
separate approval. --local-test alone can submit fictional data to Mailpit/SMS
mock. It requires example.invalid provenance under data/local-test/, rejects real
CSV/aliases, pins SMTP to 127.0.0.1 and never loads production credentials.
--channel email|sms|all selects channels; --mailpit-port and --sender affect local
capture only. --mock-sms-port 8086 explicitly selects the loopback HTTP mock;
without it SMS still uses offline file capture. --now simulates time for
read-only checks/local fictional tests.
For a fresh simulation use a new fictional fixture; do not reset completed sent
state or copy real contacts into test data.

Mailpit was tested as a checksum-verified standalone v1.31.4 binary because Docker
was unavailable. It bound only 127.0.0.1:8026/1026, allowed fictional recipients,
had no relay/forwarding, version checks or reverse DNS, and was stopped afterward.
Its private executable/capture artifacts are under data/local-test/. There is no
global install and no Android software. A future manually started isolated
Mailpit instance can use the same ports for new fictional tests.

### Run the Compose mocks

The saved `data/local-test/ready/contacts.csv` contains five fictional emails and
five confirmed fictional phone-only groups, all unsent. It is separate from the
completed demos and the real contact register. No Android gateway is needed.
Start Docker Desktop, then run from **this market-research folder**:

```sh
docker compose -f docker-compose.yaml up -d --build --wait
```

This separate `monitor-research-mocks` project starts Mailpit and the SMS API.
It does not start the sender, read either private .env, mount contacts or change
the app Compose files. Host ports bind only to 127.0.0.1; containers share a
separate bridge, with no relay/forwarding configured. Docker 29 suppresses port
publishing on internal-only networks; this bridge does not block outbound traffic.
The services have no real sending adapter or account credentials. Mailpit accepts only
`@example.invalid` recipients. The build allowlist excludes inputs and credentials.
If a port is occupied, stop here and inspect its owner; do not stop another app.

Send the fictional fixture once through both capture services:

```sh
.venv/Scripts/python.exe send_due_messages.py --local-test --csv data/local-test/ready/contacts.csv --mock-sms-port 8086 --now 2026-12-01T10:00:00Z
```

The explicit clock is a Tuesday working-time simulation, so you can test on a
weekend too. Expected first run: five Mailpit emails and five SMS API captures;
second run: zero resends. This updates only the fictional CSV. The runner checks
the real clock unless --now is given. Do not reset sent rows for a new test;
use a fresh fictional fixture instead.

- Emails: http://127.0.0.1:8026
- SMS captures: http://127.0.0.1:8086/messages (latest 100; count includes all)
- SMS health: http://127.0.0.1:8086/health

Ignored captures persist below `data/local-test/compose/{mailpit,sms-api}/`.
The SMS JSONL file is a local capture, not delivery to a phone. The earlier native
Mailpit binary and offline captures are retained but are not needed for Compose.

```sh
# Stop only this mock project; saved captures and CSV state remain.
docker compose -f docker-compose.yaml down
```

The SMS API accepts `POST /messages` JSON with `phone`, `message` and
`source_domain: "example.invalid"`. Optional `outcome` supports `success`,
`temporary` (503), `permanent` (422), or `uncertain` (capture then drop response).
It never forwards a message. The client connects directly to 127.0.0.1, ignores
proxy/gateway environment settings and follows no redirects. Unknown acceptance
stays `sending` for manual review, rather than automatically retrying. No CORS
access is enabled; browser-origin submissions are rejected.

Task 106 verified five fictional emails and five HTTP SMS captures, controlled
rejections, an accepted/disconnected request, date/day caps and zero resends
after both runner and capture-service restarts (63 checks). Captures persisted.
The original app containers, Compose/config files and real contact CSV stayed
unchanged. An interrupted fictional fixture is preserved for manual review after
a local CSV write error; the sender stopped safely. A later fresh run passed.
Evidence remains private in `data/task106-verification.json`.

### Current schedule

| Local date | Email reservations | SMS reservations |
| --- | --- | --- |
| Mon 23 Nov 2026 | 5 | 0 |
| Tue 24 Nov 2026 | 5 | 0 |
| Wed 25 Nov 2026 | 5 | 0 |
| Thu 26 Nov 2026 | 5 | 0 |
| Fri 27 Nov 2026 | 5 | 0 |
| Mon 30 Nov 2026 | 5 | 0 |

Each date's local slots: **09:30, 11:00, 12:30, 14:00, 15:30** (Johannesburg,
UTC+02 for this experiment); UTC slots: 07:30, 09:00, 10:30, 12:00, 13:30.
The closing 15:30 minute is included. Five/channel/day is the target; six is the
hard attempted-contact cap. Weekends and outside hours produce no submissions.
The table is the saved initial batch, not a code-level expiration. Catch-up uses
the CSV dates and current limits; there is no schedule-generation step at runtime.

Canonical data/contacts.csv has 2,142 rows: 643 emails and 1,499 phones. Thirty
emails are scheduled, 613 remain new/unscheduled. All real attempt/sent fields
are zero/empty and legacy contacted flags are unchanged. SMS is unallocated
because no phone-only identity has been confirmed. Full reservation IDs/times
are in private data/schedule-proposal.json; before-state audit is private too.

### Contact priority and CSV state

The expanded CSV has 30 columns: original 15 preserved, contact_group, email and
phone mirrors, then each channel's status, scheduled_at, sent_at, attempts,
last_error and last_attempt_at. Existing response_status and notes stay intact.
Known old headers migrate; malformed/unknown schemas are preserved. Collector
upserts retain all delivery fields. No person records are merged or inferred.

Use the same manually confirmed contact_group on rows for the same person. A
phone-only group must be complete and explicitly confirm there is no email.
Leave unknowns blank. An email anywhere in a group always wins, even if failed
or not due. Do not put a second method into the same row. Unconfirmed phones,
fixed-line/uncertain SMS candidates, .ac.za email addresses, sent/contacted/
replied/suppressed groups remain ineligible. No automatic channel fallback or
follow-up after unanswered/failed email. Positive replies are handled manually.

Current phone metadata is 1,391 mobile, 107 fixed-line and one VoIP, without
proving ownership or SMS capability. All phone records remain. Publication on
a university page does not identify its private accommodation contacts as
university staff; never group by publishing domain or adjacent excerpts.

The runner holds one shared contacts.lock, counts today's per-channel successes
and reserved attempts, saves before/after each submission, and exits. At most
one automatic attempt/contact/channel/day and three total safe attempts. It
rechecks the working window before each attempt; there is no waiting daemon.
States: new/scheduled/sending/sent/failed/skipped. Interrupted sending/uncertain
acceptance is held for manual review, never retried automatically. A known
success remains sent after an SMTP QUIT failure. Persistence errors stop further
submissions. A stale/conflicting lock requires confirming the prior writer is
gone before manually removing that exact lock; never reset delivery state blindly.

### Editable templates and SMS boundary

Edit the two UTF-8 plain-text sources:

- [templates/email.txt](templates/email.txt): first line is `Subject: ...`, then
  a blank line and the email body.
- [templates/sms.txt](templates/sms.txt): the complete SMS body, with no links.

The original wording is retained. The runner reads the files once per delivery
run; your edits apply next invocation without Python changes. All recipients
use that same literal text. No interpolation, per-contact variants, LLM copy or
HTML execution. Sent/held states remain protected even after you edit a template.
Blank/malformed/missing/oversized templates stop before an attempt is marked.
The template files are reviewed source; private captures and CSVs remain ignored.

The typed send_sms(phone_number, message) boundary uses an offline mock by
default, or the explicit loopback HTTP mock in local-test mode. Neither can
deliver to a phone. Future environment key names are documented in this folder's
.env.example. Configure them only in this folder's private .env when a gateway
is chosen; no live adapter exists and setting a URL cannot activate delivery.
Keep two Python source scripts only.

### Reporting and readiness

Each run reports emails/SMS sent today and this run, failures, remaining eligible
contacts, unconfirmed phones and manual-review states. Read-only reports show
stored failed-state counts; delivery runs show failures from that run. Counters
represent logical messages, not proof of final inbox/handset delivery or carrier
segments. Mock results are labelled and only mutate fictional CSVs.

The local demonstration captured **five emails and five mock SMS**, with one
controlled failure per channel. A fresh-process restart sent zero again; weekend
execution made no submissions. Exact message text was verified after normalizing
MIME wire newlines. Captures/results are private in data/local-test/demo/ and
data/task105-verification.json.

### Independent research configuration

Use **software/research/market-research/.env** for this tool's own SMTP and future
SMS settings. The runner never loads or falls back to software/.env or process
SMTP credentials. The app's existing .env was left byte-for-byte unchanged.
This folder's [.env.example](.env.example) is the safe source template; never
copy it over the app's configuration or overwrite an existing research .env.

The private research file already exists with the confirmed sender and starting
server/port/TLS values. **Fill SMTP_USER and SMTP_PASSWORD for your research
account**; no app username/password was copied. RESEARCH_DKIM_SELECTOR can remain
blank until confirmed. Future SMS_GATEWAY_URL/USERNAME/PASSWORD/API_KEY are blank
until you choose/configure a gateway; these values cannot enable real delivery.
No additional Python script is introduced. Local Mailpit/SMS mocks do not read
or require these account credentials and remain ready to use.

Readiness checks inspect this research file only, report missing/incomplete own
credentials and still perform bounded no-auth TLS/public-DNS inspection when the
nonsecret endpoint settings exist. Earlier checks found TLS verified and SPF
published, but **DMARC absent, DKIM selector/signing and sender permission
unverified**. See the current private data/email-readiness.json; older shared-env
inspection is preserved separately as historical evidence. No authentication or
real message was attempted. Inspection exit success is not production approval.

Resolve/review these blockers, choose any SMS gateway separately, and obtain
explicit production authorization before implementing/enabling real transports.
The survey is not a prerequisite; Task 104 remains deferred.
