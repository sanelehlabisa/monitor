# Market-research pipeline

Local workspace for a planned Python tool finding public business contacts at
student accommodation providers, property managers and landlords. Workspace
setup and resumable resource collection are implemented. The first milestone
will produce one contacts CSV with short, factual context. Document readers,
enrichment and outreach remain separate tasks.

## Workspace and privacy

Use this folder for the whole experiment. One typed `pipeline.py` provides the
entrypoint. `requirements.txt` currently has no packages; use a local `.venv/`
when dependencies are added.
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
and resource/extraction status, not a second contact database. Keep fetched
documents, extracted text and source-linked summaries in private evidence for
review and reprocessing. Inputs, CSVs, downloads, excerpts, prompts/results, drafts, logs,
temporary files and credentials stay here and out of Git. Logs avoid contact
details and secrets. Retention/cleanup is manual and documented; never delete
the working contact register automatically.

The local `.gitignore` excludes everything except explicitly reviewed source,
requirements and instructions. Verify exclusions before the first data run and
whenever adding output paths. Do not force-add private files or paste records
into work reports. Ignore rules do not remove previously tracked files or provide
encryption. Application Docker builds do not include this sibling directory.

## Run offline setup

From the repository root, using Python and its standard library:

```sh
python software/research/market-research/pipeline.py --init
python software/research/market-research/pipeline.py --check
```

From this folder, use `python pipeline.py --init` or `--check`. Paths resolve
relative to the script in either case. The owner's existing `links.txt` is the
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
and a 1-second delay, plus 5 MiB per resource. Robots requests, redirects and
failed request attempts consume the total request budget.

## Crawl and resume

From the repository root:

```sh
# First run only; refuses to replace an existing checkpoint.
python software/research/market-research/pipeline.py --crawl --max-requests 5

# Continue saved work with a fresh per-run budget.
python software/research/market-research/pipeline.py --resume --max-requests 5
```

The local Task 100 smoke checkpoint already exists, so use `--resume` here.
The seed file must match that checkpoint. Use another private `--data-dir` for
a different batch instead of deleting existing evidence/state.

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
Bounded non-HTML downloads are retained for the later document-reader ticket.

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

### Access findings and limits

Only four of the 16 seed URLs were attempted: one fetched and three failed at
robots checking. The other 12 seeds are pending solely because of the request
budget. Most seeds remain untested; these results cannot establish that most
sites are inaccessible. The recorded errors do not yet establish their root cause.
`robots_unavailable` can conceal different network/HTTP failures, while the two
`robots_redirect_loop` outcomes need their actual response chains checked.

Exact seed outcomes are recorded privately in `data/task100-access-review.json`;
the source checkpoint/evidence remain intact. Follow-up 71.2.1 comes before
document readers or a broad collection run. No additional requests were made
while recording this review.

## First milestone — Tickets 71.1–71.7

After individually approved slices, the user can enter several seeds, run one
Python command and obtain unique contacts with traceable context. Stop for review
before survey work or outreach. Tickets 71.1 and 71.2 are complete; the rest remain open.
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

Detect the resource type at every node. Save allowed fetched files and extract
text/links using a suitable reader. Start with HTML/PDF; extend the document
ticket to the text/office formats actually encountered. Record unsupported,
encrypted, scanned, oversize or failed resources for review rather than calling
them read. Do not execute downloaded files or promise arbitrary-format reading.
Agree any needed OCR or additional parser before implementing it.

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

### 71.2.1 — Crawl access diagnostics (next)

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

### 71.3 — PDF and document reading

Depends on 71.2.

- Handle direct PDFs and discovered PDFs using a small text extractor such as
  PyMuPDF. Confirm actual response type rather than relying on `.pdf` endings.
- Capture text, emails, URLs, title when available and nearby contact context.
  Feed relevant links through the same crawler budgets; add size/page limits.
- Check a text PDF and malformed/scanned documents. Report unavailable text;
  OCR needs separate agreement. Retain allowed downloads and extracted text in
  private evidence so readers/enrichment can rerun without fetching again.
- Inventory actual file types in the seed crawl, then add small readers for
  relevant text/office documents in reviewed substeps. Every discovered resource
  has a readable/pending/unsupported/failed status; unsupported does not mean read.

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
