# Task 001: Repository bootstrap

## Result

- Created Monitor's documentation-only hardware/software tree and agent/PR workflow.
- Adapted Switch's meter.README.md into the main README, including its product
  learning, boundaries, consent requirements and future payment research.
- Added 41 phased roadmap tickets; only repository bootstrap is complete.
- Kept Docker/config under software as a future task; no docs directory.
- Deferred all product code, models, dependencies, firmware and deployments.

## Reuse and migration

Reused Switch's task template, small-review engineering rules and PR conventions.
The developer explicitly approved making the old Meter plan the main Monitor
README, not a separate historical file. Old Switch ticket IDs are not reused:
69 maps to Monitor 11/34/38; 70 to 38/39; 71 to 40/41; 72 to 12-16;
73 to 8/10 and data-retention requirements; 74 to 28-32; 75 to 33/36.

After Monitor is safely pushed, remove only Switch's meter.README.md and update
the current pointers in Switch README/context. The original remains recoverable
from Switch commit 38eccd808fd73d6843fe54424b0d32d19348a255.
No firmware, PCB, CAD or existing untracked user files are in scope.

## Verification

- PASS: 20 scaffold files (19 Markdown plus gitignore); no product code/config.
- PASS: all 17 relative documentation links resolve.
- PASS: roadmap IDs 1-41 are sequential and unique; only Ticket 1 is complete.
- PASS: environment secrets, private captures/models, volumes and dependencies
  are ignored; software/.env.example remains trackable.
- No application tests or hardware claims apply to this documentation-only task.
