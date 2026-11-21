# Task 102 results

The user approved the revised fetch-and-extract flow. It is implemented and
verified below; this work remains uncommitted.

## Planning history

Published Task 101 and manual-deferral notes to Monitor master as
6ea68bbab5c6cda76f9ec21878fc689b659f5bb9 at the user's request.
Local HEAD and remote master matched. The seven reviewed source/planning files
were committed; private input, state, evidence and review files were excluded.
Source syntax, offline --check, whitespace and all 40 local links passed before
publication. The prior Task 101 diagnostic/wire checks are recorded in its results.

Created ignored software/research/market-research/links.failed.txt with 11 unique
seed URLs and observed reasons: nine robots self-redirects, one TLS verification
failure, one HTTP403. These observations preceded the HTTPS Host fix; the list
does not call every failure a robots.txt ban. Existing seeds, checkpoint and
Task 101 report hashes were unchanged; no request or counter reset was made.

Prepared this prompt from agents/prompt.md for offline PDF extraction using the
saved evidence. It defers failed URLs as requested and awaits approval under
AGENTS.md. No reader code/dependency installation or additional crawl was run.
This preparation remains local.

## Revision before approval

The owner rejected the required saved-file/offline-reader workflow. Revised Task
102 in place to fetch once, detect type and extract directly from bounded response
bytes in memory during crawling. Preserve the task ID and existing linked paths;
the directory name reflects the superseded proposal, not the new scope.

The revised prompt reuses one script and the existing HTML reader, with small
text/PDF handlers and a shared result shape. It proposes saving extracted text,
facts, provenance and progress without raw page/document copies by default. Existing
captures remain preserved. Unsupported formats are explicit, with new readers
added only when needed. Reprocessing discarded response bytes requires a later
authorized fetch, rather than silently depending on a local file or retry loop.

Manual links.failed.txt remains private and deferred. The new prompt includes
honoring that list and a five-attempt live verification using only previously
successful seeds; that proposed verification is not yet approved. LM Studio and
the final contacts CSV remain their planned later slices.

Updated Ticket 71.3, research indexes and current context to match. Runtime code,
dependencies, private sources/state and the Git index were not changed. No
network requests, implementation, commit or push occurred during this revision.

Verification: all 41 local documentation links resolve, active guidance no longer
requires offline saved-file extraction, whitespace checks pass, runtime source
is unchanged and the private failed-links list remains ignored. No runtime test
is needed for this planning-only revision.

## Implementation

- Added a shared extract_content function in the existing typed pipeline.py.
  Successful HTTP responses go directly through HTML, plain-text or PDF readers
  in memory. Readers do not fetch their source or require a saved input file.
- Reused the HTML parser and added explicit titles, visible/mailto email evidence,
  text URLs and nearby context. PDF extraction includes title, page text/context
  and embedded URI annotations. Results share source/type/title/text/email/link/
  status fields; normalized links return to the existing bounded graph.
- New output is extracted JSON with content-derived names, source hashes and
  explicit completion/error states. No new raw .bin, HTML or PDF copies are written.
  Differing results get separate names; edited existing output is preserved.
  Existing captures, metadata, checkpoints and reports remain unchanged.
- Selected pypdf==7.1.1 as the single PDF dependency, installed only in this
  experiment's ignored .venv. It is lazy-imported; HTML/text/setup/check do not
  require it. No app requirements, Docker images or ML packages were changed.
- Reader controls cover input/decoded stream size, PDF pages, extracted characters,
  annotations and a cooperative between-page time budget. Individual library calls
  are not pre-empted. Unsupported, encrypted, textless, malformed, partial and
  missing-reader outcomes remain explicit; no OCR, scripts or password guessing.
- Enforced private links.failed.txt in the scheduler and transport, including
  robots/ordinary redirects. Existing failed outcomes and retry counts are kept;
  no manual target is implicitly retried. CLI summaries report counts only.
- Updated root/software/research instructions and context. No source file or old
  capture was retired; no new test file or standalone offline-extraction workflow.

## Verification

- Thirty-seven direct checks passed for in-memory multipage PDF text/title/email/
  page context, URI annotations, encryption, textless/malformed PDFs, missing
  dependency, HTML/text results, encoding/size/page limits, persistence, differing
  output preservation, graph links, budget/resume, deferrals and console privacy.
  The PDF fixtures were generated as in-memory test bytes, not saved documents.
- During verification, an obsolete pypdf filter-setting API was replaced with
  its current public Configuration API. The full 37-check rerun passed and
  temporary decoder/log settings are restored after reading.
- The previously captured real PDF also parsed from test bytes: two pages,
  1,778 text characters, one email candidate and 21 links. No new file was needed
  or written for that check; no private content was printed.
- Ran the one approved live check using only the five previously successful
  seeds, in separate private data/task102-live/ state. It stopped at five request
  attempts and fully extracted one PDF and two HTML responses. No failed/blocked
  response in that batch, no raw document files and no manual-review URL requests.
  One manual-review URL discovered in the graph stayed deferred.
- The batch discovered 287 nodes, with 284 pending at the chosen depth/budget.
  This is limited verification, not a full collection run. Exact private evidence
  is in data/task102-live/ and aggregate/source verification metadata in
  data/task102-verification.json. No additional batch was run.
- Hash comparisons passed for 16 pre-existing input/state/report/evidence files,
  including links.txt and links.failed.txt. Lock cleanup passed and the final
  contacts CSV is still absent. Original already-fetched legacy nodes were not
  reset or reprocessed; new responses use the new flow.

Consulted the official [pypdf byte-stream guide](https://pypdf.readthedocs.io/en/stable/user/streaming-data.html),
[text-extraction guidance](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
and [package metadata](https://pypi.org/project/pypdf/) for the installed reader.

Source syntax, offline CLI, dependency integrity, private-output exclusions,
documentation links and whitespace pass. No application build is needed for this
isolated research change. No model, final CSV, outreach, service/DNS, commit or push.
Next slice is 71.4 contact context; next work prompt is 103.

## Publication authorization and handoff

The user requested commit/push of the current work, then a stop while they
prepare a refocus prompt. Publish reviewed source/plans only; private URLs,
research inputs/results and the virtual environment remain excluded. Updated
context/root priorities to wait for that direction. No next prompt or slice
was started; work number 103 remains available.
