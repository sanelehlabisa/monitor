# Task 107: Recover emails from saved context

## Outcome
Clean the existing private data/contacts.csv offline: recover clearly stated
emails from stored context, prefer email over phone where the association is
clear, and preserve original numbers. Keep one canonical CSV and no new script.

## Questions and answers
- The owner's final preference is the same CSV, not separate channel files.
- Phone rows may become email rows when their context clearly supplies the
  relevant email. Preserve the original phone as text in details/notes.
- Existing email rows remain unchanged; their other columns may supply new,
  additional email rows. Multiple clear emails may produce separate entries.
- Reuse the existing independent contact-method identities; do not infer that
  different people share an organisation or contact group.
- No unresolved product questions. For duplicate-only matches, retain the phone
  row rather than alter an existing email row or create a duplicate.
- Read-only inspection: 2,142 rows; 689 phone rows contain email candidates.
  All context contains 54 potentially new non-academic addresses before evidence
  review. These are candidate counts, not promised additions. CSV was unchanged.
- Task 106 was committed/pushed first as 9065e32. The owner then explicitly
  approved Task 107; the scope below is authorized.

## Scope and reuse
1. Use one-off offline processing with existing CSV loading, normalization,
   duplicate checks, contacts lock and guarded atomic writing. No new crawler
   behavior, CLI mode, dependency, third script, network request or LLM call.
2. Inspect stored descriptive fields, primarily details. Accept only complete,
   valid emails explicitly present in readable contact context. Never repair
   guessed/corrupted addresses, manufacture addresses from names/domains, or
   assign a neighbouring directory entry's email to the wrong phone/person.
   Skip academic .ac.za addresses and leave unclear cases unchanged for review.
3. Deduplicate against every existing email and all candidates in the batch.
   Preserve existing email rows byte-for-byte in field values, including their
   IDs, source context, schedules, attempts, replies and contact status.
4. For an eligible untouched phone row with a clear new associated email,
   retain its ID and context, change contact_type/contact_value to the email,
   update method mirrors/default channel fields, and append the exact original
   number to details/notes without overwriting existing text. Additional unique
   clear emails get IDs above the current maximum and their own source context.
   Keep phone rows with no new clear email, duplicate-only or ambiguous matches.
5. Do not convert phone rows with delivery schedules/attempts, contacted/replied,
   suppressed or unresolved states. New/recovered email methods are unscheduled
   and uncontacted; do not copy sending permission, SMS state or inferred groups.
   Blocked source context must not create fresh sendable rows through another
   identity. Existing suppression/contact history remains authoritative.
6. Before applying, preserve an exact ignored CSV snapshot and a private dry-run
   audit of proposed conversions/additions/skips with source row IDs/evidence.
   Once checks pass within this approved scope, apply only confident changes
   to the canonical CSV, verify it and retain an exact before/after audit.
7. Record counts, paths, reuse and actual checks in changes.md and update current
   context/README. Keep contact values, evidence, backups and CSVs out of Git/chat.

## Verification
Check one/multiple/duplicate emails, corrupted and academic text, mixed-contact
context, original number preservation and protected delivery states with small
fictional cases. Validate unique IDs and contact pairs, the existing 30-column
contract and method mirrors. Confirm all original email rows and unchanged phone
rows retain their field values; recovered identities have no assigned send date.
Recheck input hashes before saving and confirm an immediate repeat proposes no
further change. Report real conversion/addition/skip counts without contact data.

## Exclusions
No sending, new scraping, account/DNS/config changes, service operations, CSV
splitting, guessed identity matching, scheduled-date edits, commit or push.
