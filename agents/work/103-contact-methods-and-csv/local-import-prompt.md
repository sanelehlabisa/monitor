# Task 103 extension: Import local contact sources

## Outcome
Extend the existing research script to extract contacts from owner-supplied
HTML/PDF/plain-text files into the same private data/contacts.csv, then remove
successfully imported inputs as requested. Continue Task 103; no new ticket ID.
Status: complete; implementation and the approved seven-file cleanup verified.

## Questions and answers
- The owner manually downloaded sources that could not be crawled, and explicitly
  requests local extraction and removal of those inputs after successful import.
- Inspection found seven regular PDFs in
  software/research/market-research/links.failed/: 111 pages total, no encrypted
  files, each below the existing response-size limit. Six filenames uniquely
  match existing seed/failed URL basenames; one has no exact source match.
- Reuse uniquely matching source URLs. Otherwise record the real local file URI
  with an empty source_domain; never guess an original website or organisation.
  Keep local input path/hash provenance privately for every imported document.
- No unresolved requirements. No web retry or extra crawl is needed for import.

## Scope and reuse
1. Add a local-directory mode to the existing typed pipeline.py, for example
   --import-dir links.failed, plus --delete-imported for the requested cleanup.
   Reuse extract_content, PDF/HTML/plain-text readers, contact validation, optional
   bounded loopback enrichment, ContactRegister, locks and atomic writes. No new
   dependencies, scripts, storage framework or contact schema.
2. Process supported regular files directly inside the explicitly selected
   experiment-local directory. Reject symlinks/reparse escapes and protected
   source/output paths. Use existing byte/page/text limits; unsupported or
   unreadable inputs remain with explicit reasons. Do not run embedded content,
   fetch links/assets, access remote shares or follow directories automatically.
3. Preserve the exact 15-column canonical CSV, stable IDs, independent method
   deduplication and manual/status/contacted/response data. Retain source title,
   local provenance, relevant context and page associations in private evidence.
   Permit validated local provenance only for this import mode; leave public
   crawler URL/network checks unchanged. Do not infer identities from publishers.
4. Save and verify complete extracted evidence and CSV before deleting an input.
   Require complete successful extraction, verify all discovered method pairs are
   persisted, and recheck that the source path/content has not changed. A fully
   readable file with no contacts may be removed after its evidence is verified.
   Keep partial/textless/encrypted/challenge/failed inputs for review. Never
   recursively delete folders, HTML asset directories, existing captures, seeds,
   deferred lists, app files or outputs. No replacement raw-document archive.
5. Record exact input paths, hashes, resolved source URLs, extraction results and
   cleanup outcomes in an ignored local-import report. Make reruns/crash recovery
   safe through existing pair deduplication and saved evidence; never delete a
   changed file based on an earlier import. Record results and the private report
   path in changes.md, keeping private source inventories out of tracked docs.
6. After direct checks, run one import of the seven current PDFs with requested
   cleanup. Use source fallback by default for this batch because LM Studio was
   unavailable; retain the existing optional enrichment controls. Report imported,
   removed, retained, added/duplicate contacts and failures. Keep web crawl state,
   links.failed.txt and blocked-URL records unchanged: local success does not mean
   automated access restrictions have been lifted.
7. Update the concise research instructions and active context. Keep the current
   Task 103 implementation and all prior evidence/history intact.

## Verification
- Direct temporary fictional HTML/PDF/plain-text scenarios: extraction, method
  deduplication, original/local provenance, CSV/manual-field preservation, repeat
  import, source changes, invalid paths and partial/unreadable retention.
- Exercise write/evidence failures and deletion failure: no input removal before
  verified persistence; successful files delete individually, unrelated files stay.
  Verify resolved targets are inside the explicit input directory before cleanup.
- Before the real batch, snapshot the seven input hashes and existing contact
  IDs/state fields privately. Afterward verify retained IDs, unique pairs, default
  states for additions, complete evidence, exact cleanup results and ignored paths.
  Do not create persistent test files or print bulk contact data.
- No web requests, app/service operations, sending, commit or push.

## Exclusions
No outreach, SMTP, authentication/app changes, dependency additions, OCR, archive
unpacking, automatic web retries, access bypass, recursive deletion or deletion
of failed/partial imports. Existing captures remain untouched.
