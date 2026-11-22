# Task 107 preparation

Committed and pushed completed Task 106 to origin/master as 9065e32 before
starting this ticket. Only reviewed source/build files and documentation entered
Git; the branch was synchronized and the working tree clean after publication.

Read the current collector/normalizer, contact-method contract, delivery-state
rules and the owner's request. Ran a read-only aggregate CSV check without
printing contact values or source excerpts. The canonical CSV hash was unchanged.
Current rows: 2,142 (643 email, 1,499 phone). Email text appears in 689 phone rows;
617 email rows also mention other emails. Candidates appear in details, with
54 distinct potentially new non-academic addresses across all context before
evidence validation. Existing 30 scheduled/history-bearing rows were observed;
their data must remain unchanged. Candidate presence does not prove identity.

Prepared prompt.md from agents/prompt.md for a one-off offline cleanup, not a new
script or crawler feature. One CSV remains authoritative. The plan preserves
numbers, existing email rows and delivery history, skips uncertain association
and duplicate-only conversions, and records private before/after evidence.
Added a planned roadmap entry and current context. No implementation or contact
change, network lookup, message submission or service operation for Task 107.
Implementation awaits approval of Task 107.

## Approved offline review

The owner approved Task 107. Reused load_contacts, normalize_email, delivery
defaults, the shared contacts lock and the existing sender's validate_rows.
Processing was one-off and offline; no source script, CLI, dependency, service,
configuration, sending logic or schema was changed. No files were retired.

Preserved an exact original CSV snapshot before any proposed mutation at
software/research/market-research/data/task107/contacts.before.csv. The only
active contact register remains data/contacts.csv; the snapshot is recovery
evidence, not another channel list or sender input.

Scanned the stored descriptive fields and compared candidate emails against
the existing register and complete tokens/contact methods in 31 saved source
JSONs. All potentially new candidates have same-source evidence available.
This matters because details are approximately 220-character excerpts: their
left/right boundaries can cut through an email while leaving a syntactically
plausible fragment. A regex match alone does not establish a new address.

## Result

- 689 phone rows contain email-like text; 637 reference an already registered
  email. The approved duplicate-only rule leaves their original phone rows and
  existing email rows unchanged.
- 640 unique already registered email values appear across stored context;
  this count includes rows mentioning their own email. Academic .ac.za
  candidates were excluded (54 distinct values); none was reintroduced.
- All 54 apparently new non-academic values failed complete same-source token
  and email-method checks. 47 are clipped local parts, four are clipped domains
  and three remain unverified/corrupted. No address was guessed or repaired.
- Zero conversions and zero added rows were justified. The canonical CSV was
  deliberately not rewritten: 2,142 rows, 643 emails and 1,499 phone methods.
  Every existing email, phone number, ID, context, schedule, attempt, response,
  suppression and contact state remains byte-for-byte intact.

Private source-linked candidates/spans/decisions and hashes are in
data/task107/dry-run.json. data/task107/result.json records the completed no-op
and before/after hashes. These files and the recovery CSV remain ignored;
contact values and source excerpts were not printed or put into Git.

## Verification

33 direct checks pass, recorded in data/task107/verification.json. Small
fictional in-memory cases cover one/multiple/duplicate/academic/corrupt emails,
mixed contexts, stable conversion IDs, original phone text, method mirrors,
unscheduled/uncontacted defaults and protected delivery states. Actual-register
checks verify all original rows, the 30-column contract, unique IDs/contact
pairs, unchanged saved schedules/history, no academic reintroduction, exact
snapshot/hash equality and all retained source hashes. An independent repeated
complete-source check proposes zero further changes.

This completes the approved cleanup review without manufacturing new contacts
or duplicating existing emails. No web/model request, message, service operation,
commit or push was performed for Task 107. Production sending remains disabled.

## Applied cleanup after the owner's correction

The owner explicitly requested updating the CSV now, cleaning leading slash
artifacts, removing duplicates and replacing phone methods with valid emails
where possible. Recorded this authorized amendment in apply-prompt.md and
presented its scope before applying. It supersedes the earlier keep-phone rule
for duplicate-only matches: same-entry phone records can merge into the existing
email row, with the original number/context retained. The earlier no-op review
and artifacts remain historical evidence; they were not overwritten.

Inspected all registered emails and saved source records offline. Three email
values began with a slash; their original source methods were retained, and all
three were cleaned under the owner's explicit prefix-normalization request.
Their prior values are in notes and the private audit. No domain, name or clipped
local part was guessed; valid internal slash characters were not stripped.

Matched phone/email associations only on complete same-source lines. Unlabelled
multiline directory blocks were excluded to avoid assigning a neighbouring
provider's email. A preliminary broader private preview was retained as
data/task107/apply/preview-initial.json but never applied; the final narrower
preview uses 582 complete-line associations. Protected phone histories/groups
and protected email targets remain untouched. Existing scheduled email targets
retain their saved dates and all other sending state.

Saved an exact fresh recovery snapshot at data/task107/apply/contacts.before.csv
and the source-linked final proposal/full retired rows at preview.json, plus
contacts.preview.csv. Applied only that checked proposal to data/contacts.csv
using the existing shared lock and guarded atomic writer, after rechecking input
and source hashes. Saved reload exactly matches the preview.

Actual changes:
- Three leading-slash email prefixes corrected; all 643 existing email IDs remain.
- 582 eligible phone rows merged into their already registered email methods,
  removing the duplicate identities that conversion would otherwise create.
  Every original number and phone excerpt is appended to the retained email's
  notes, with its source row ID/source URL. Full retired rows are recoverable.
- Current unique rows: 1,560 (643 emails, 917 phone methods). No new speculative
  email or academic contact was added. Remaining phone rows are unchanged.
- All email schedules, attempts, sent/contact/reply/suppression states are intact.

40 fictional/actual checks pass: prefix/internal-slash handling, one/multiple
emails, source-line association, ambiguous/unlabelled directory separation,
phone conversion/merging, protected states, original-number recovery, stable
email IDs, remaining-row equality, unique pairs, schema and source hashes.
Post-write reload/hash validation passes and an immediate independent repeat
proposes zero changes. Results: data/task107/apply/result.json and verification.json.

No source scripts, dependencies, app/configuration, services, sending or network
behavior changed. No files were deleted; snapshots, audit, previews and canonical
CSV remain private/ignored. No commit or push was performed.
