# Agent Instructions

Before starting work, read:

- `agents/context.md` for Monitor scope.
- `agents/rules.md` for engineering standards and the required workflow.
- The nearest directory `README.md` for task-specific detail.

For every new task:

1. Inspect the relevant code and documentation.
2. Ask focused clarification questions before editing code; keep them visible in chat even when using option buttons.
3. Create `agents/work/NNN-short-title/prompt.md` from `agents/prompt.md` after questions are answered.
4. Paste the completed prompt into chat and get developer approval.
5. Implement only approved scope, then verify it.
6. Record results, reuse and checks in `changes.md`.

Use the next three-digit work number. Keep roadmap ticket IDs stable and each
task/PR small enough to review. Read-only Switch UI and Roventics brand reference
inspection is approved; never modify either sibling repository without explicit
authorisation.

## Product boundary

Monitor V1 is a software-only prepaid-electricity planning application. Users
manually record remaining balance and purchased top-up energy in kWh at selected
times. Use simple, tested calculations and show "Not enough data" instead of
inventing forecasts. V1 has no tariffs, Rand forecasts, payment execution,
hardware, OCR, MQTT or ML.

Preserve hardware/OCR research for later evidence-driven reconsideration. Any
future physical integration must not open, electrically modify, bypass or
interfere with a meter. Anomaly output is never proof of theft.

## Future generated design outputs

These rules apply only when a later approved hardware/design ticket resumes the
deferred work.

- CAD: `hardware/mechanical/out/<part>/`; references: `out/references/<model>/`.
- Future PCBs: `hardware/pcb/out/<board>/`; create only when a ticket needs them.
- Retain editable sources in component trees. Group handoff files, checks,
  at least three PNG views and a short sending/rebuild README per design.
- Mark reference models "do not print"; preserve prototype/qualification warnings.
- Reuse exporters, stage temporary output separately and publish after checks.
- Before removing outputs, check dependencies and record paths/recovery.
  Never delete unique drawings or sources as generated clutter.
