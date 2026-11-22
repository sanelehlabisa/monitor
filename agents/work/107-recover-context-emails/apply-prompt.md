# Task 107 amendment: Apply contact cleanup

## Outcome
Apply the owner's requested cleanup to the canonical private CSV: fix extraneous
leading email slashes, recover complete source-confirmed emails, replace eligible
phone entries with email entries and deduplicate without losing original numbers.

## Questions and answers
- The owner explicitly says to update the CSV now, fix leading slash mistakes,
  remove duplicates and replace phones with valid emails where possible.
- This amends the earlier keep-duplicate-phone/preserve-email-text rules: a phone
  may merge into its already registered email when the saved source confirms the
  same contact entry. Preserve its original number/context in notes/private audit.
- Do not guess clipped local parts or domains. Use complete retained source
  entries to distinguish a real address from a short CSV excerpt fragment.
- No unresolved questions. The latest direct execution instruction authorizes
  this correction within Task 107; no new sending/service approval is implied.

## Scope and reuse
Use one-off offline commands and existing CSV/normalization/lock/atomic-save
functions, without another script or CLI. Save a new exact recovery snapshot and
source-linked preview before applying. Strip only the extraneous leading slash
prefixes the owner identified; retain old values in notes. Link phone/email only
through an unambiguous same-line or bounded same-entry source block, not proximity
to an unrelated directory entry. Exclude academic addresses and unresolved text.

Merge duplicate resulting email methods into a stable existing email ID, append
original phone numbers and source-row IDs to notes, and retain retired rows in
the private audit. Keep unrelated rows and all schedules, attempts, sent/reply/
suppression state intact. Hold protected phone rows rather than reassign their
history. New methods are unscheduled and uncontacted. Apply under the shared lock
only if the current file still matches the inspected input. Keep one active CSV.

## Verification
Check prefix cleanup, source association, conversion/merge, multiple emails,
duplicates, academic/corrupt text and protected-state handling with fictional
in-memory cases. Validate the actual 30-column schema, unique IDs/contact pairs,
original number recovery, stable email IDs/history and unchanged unrelated rows.
Reload the saved CSV, check a repeat proposes no changes, and record actual counts.

## Exclusions
No network, LLM, sending, new scripts, app/config/service changes, commit or push.
