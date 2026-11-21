# Task 103: Contact methods, enrichment and CSV

## Outcome
Complete the collection milestone in the existing research script: one command
reads private seeds, crawls within limits and upserts one private contacts.csv
containing independent email/phone rows with grounded context. Show a small
sample of the generated CSV to the owner, then stop before outreach.
Status: complete; approved collection scope and local-import extension verified.

## Questions and answers
- The refocus replaces email-only rows with one row per contact method. Never
  match an email and phone into a guessed person record.
- LM Studio is optional under the latest brief, superseding the earlier required
  stage. Current source has no LM integration yet. Use the installed small Qwen
  if available, with an explicit off option and graceful source-based fallback.
  Confirm its actual identifier; do not download a model or call a cloud service.
- South Africa is the default region for unqualified phone numbers; explicit
  international prefixes remain respected. Keep the original in notes if uncertain.
- No canonical contacts.csv exists now. Preserve any existing/newly supplied CSV
  or unknown schema rather than resetting it. Existing captures/state stay intact.
- links.failed.txt remains deferred. Restrictions/anti-bot protection must not be
  bypassed. A self-redirect or generic network error is not automatically a bot ban.
- The owner explicitly requests a generated CSV sample after completion. Show
  only a few review rows, never bulk records or private prompts/secrets in Git.
- No unresolved questions for the proposed collection-only scope.

## Scope and reuse
Implement the open contact milestone together in small functions, reusing the
single typed pipeline.py, in-memory readers, existing graph and isolated .venv.

1. Extend HTML visible/contact text, mailto/tel links and PDF text/URI annotations
   to emit email and phone candidates with nearby text, title, page and exact
   source provenance. Plain-text responses use the same contract. Do not save new
   original files or hardcode a source. Unsupported/textless sources stay explicit.
2. Validate/normalize emails and phones. Prefer E.164 for credible South African
   numbers, including landlines/mobile and formatted national/international forms.
   Avoid dates, prices, IDs and other unrelated numerals. Keep clearly labelled
   uncertain phone candidates with original text/uncertainty notes; do not invent
   country/area codes for ambiguous numbers. Add only a small necessary research
   dependency if it improves validation. Deduplicate by (contact_type, contact_value).
3. Gather evidence for explicit name, organisation, role and location. Leave
   unknowns empty. Free-mail domains never identify an organisation. Optionally
   send only bounded relevant context/title to loopback LM Studio for the five
   string fields name, organisation, role, location, details. Validate JSON, reject
   unsupported facts and keep details to one short sentence. Retrieved text is
   untrusted data; the model has no tools or sending ability. Bound calls/timeouts
   and retries; unavailable/invalid enrichment must not stop contact collection.
4. Write exactly one canonical software/research/market-research/data/contacts.csv
   for real runs, including when crawl checkpoints use another --data-dir. Reuse
   the writer-lock/atomic-replacement pattern for this shared contact register.
   Assign stable sequential IDs and upsert normalized pairs. Fill missing context
   from better evidence, preserving manual edits and contacted/response/status/notes.
   Keep conflicting nonempty information for review rather than guessing. Preserve
   CSV on malformed input, interrupted writes or concurrent changes. Use correct
   CSV quoting and safe text handling without changing normalized contact identity.
5. Add a shared per-domain page budget alongside existing depth/per-seed/request
   limits, delays, timeouts and URL deduplication. Honor manual deferrals, robots,
   terms and rate limits. Detect explicit anti-bot/access restrictions without
   evasion; mark blocked and continue other sources. Distinguish temporary rate
   deferrals and network/reader errors from actual blocks. Keep a private
   data/blocked_urls.csv with url,reason,seed_url and deduplicated entries.
6. Reuse available extracted evidence when safe, without silently re-fetching
   legacy sources or pretending old text includes previously unrecorded tel links.
   Save contacts before marking the corresponding resource complete, so resume
   cannot lose contacts or duplicate IDs. Keep all real inputs/results ignored.

CSV columns in this exact order:

```text
id,contact_type,contact_value,name,organisation,role,location,details,source_url,source_domain,status,contacted,contacted_at,response_status,notes
```

New rows use contact_type=email/phone, status=new, contacted=false, and empty
contacted_at/response_status. No contact or send status is inferred from discovery.

Print Pages visited, PDFs processed, Emails found, Phone numbers found,
Unique contacts added, Duplicates skipped, Blocked URLs and Errors. Explain
remaining pending work or unavailable enrichment without printing bulk records.

## Verification
- Direct temporary scenarios cover HTML/PDF/tel/mailto extraction, ZA/international
  formats, uncertain numbers, numeric false positives, per-type duplicates,
  free-mail evidence, optional LM success/outage/invalid/hallucinated output,
  blocked sources, shared domain budgets, resume and CSV preservation.
- No persistent test files. Inspect current official library/API documentation
  and available local model before adding necessary implementation details.
- After approval, perform one bounded live run from the existing seeds/checkpoint,
  capped at 30 request attempts, depth 2 and ten pages per seed/domain. Include
  robots/redirects in the cap and keep all manual failed URLs deferred. No automatic
  extra batches. Limit model verification to 20 bounded requests, reusing context
  where appropriate; remaining rows keep factual fallback/pending context.
- Confirm the requested header, stable unique pairs/IDs, default statuses, ignored
  files and no raw-document copies. Show three to five actual generated review
  rows plus a local CSV link; label any redaction. Report whether LM actually ran.

## Exclusions
No email/SMS sending, SMTP checks, outreach drafts, survey distribution, account
or app changes, heavy ML, guessed person matching, new databases/queues/services,
access bypass, broad/unbounded crawl, commit or push.
