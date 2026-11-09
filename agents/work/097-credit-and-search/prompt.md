# Task 097: Restore credit and improve search metadata

## Outcome
Restore the original Roventics logo credit and improve public-homepage discovery without redesigning Monitor.

## Questions and answers
The user explicitly requested the original credit and small, nonvisual indexing improvements. This request authorizes implementation. No hidden keyword text or additional app sections. City/province remains unconfirmed.

## Scope and reuse
Reuse the footer from commit 336ad2e's parent, existing logo, metadata, Nginx and discovery files. Add a homepage canonical HTTP header and noindex on nonpublic app routes. Keep authentication unchanged.

## Verification
Existing frontend tests, production build, served metadata/headers and desktop/mobile footer checks using an isolated frontend preview.

## Exclusions
No production rollout, Git publication, account/ledger writes or additional app marketing sections.
