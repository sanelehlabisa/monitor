# Task 099: Local research workspace

## Outcome
Implement Ticket 71.1 only: one typed Python entrypoint that initializes and
checks the private research workspace without crawling or sending data.
Status: explicitly approved by the user; implementation authorized for 71.1.

## Questions and answers
- The user requests the next small task, keeping the implementation simple.
- Crawl seeds are roots of a linked graph, not independent single-page fetches.
  Future crawling must explore reachable in-scope nodes, avoid cycles and retain
  the pending queue when limits pause a run. Record every discovered node's
  source/type/status, including unsupported files rather than silently dropping them.
- LM Studio is already installed. Its enrichment stage is required in 71.5;
  temporary unavailability preserves raw data and pending work for resume.
- The user has supplied links.txt inside the experiment. Reuse it in place as
  the documented seed default; preserve its bytes and never duplicate/move it.
- LM Studio is open. The user prefers a small Qwen model of approximately 1.3B
  parameters; confirm the actual installed identifier in 71.5 rather than guess.
- No unresolved questions for 71.1. Confirm external-domain scope and document
  readers against the actual seeds before their respective implementation steps.

## Scope and reuse
- Reuse software/research/market-research/ and its private-by-default ignore rules.
- Add one standard-library-only pipeline.py with type hints, --help, explicit
  initialization/check modes and readable counts/status messages.
- Initialize data/, data/evidence/, drafts/ and logs/ inside this experiment.
  A comment-only seed template may be created only when absent. Never overwrite
  existing files or create a misleading final contacts CSV before 71.7.
- Check workspace paths, write access and seed availability. Keep all generated
  and temporary paths within this experiment, independent of the calling folder.
- Define configurable crawl depth/page/request limits, timeouts and delay in the
  same script/CLI, ready for 71.2; make no HTTP/model requests in this slice.
- Keep requirements.txt local to research. No third-party dependency or model
  installation is needed for this setup. Document the command and later stages.

## Verification
- Run --help, initialize and repeat initialization from two working directories.
- Check missing/empty seed-file messages, preservation of existing fictional
  files and rejection of output paths outside the experiment.
- Use temporary fictional data within ignored paths and check Git exclusions.
- Use direct/manual checks, without adding test files or touching app services.

## Exclusions
No crawler, document reader, model call, contact CSV, outreach, app/database
change, dependency installation, service restart, commit or push in this task.
