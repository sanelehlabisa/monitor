# Task 082: Simplify forecast layout

## Aim

Make the four forecast figures readable in a compact 2 by 2 layout across devices.

## Clarifications

- The user explicitly approved the minor layout/font polish and removal of the
  hardware/modification note, while keeping the UI simple.
- Keep two columns at 360px and wider; stack on narrower screens. Keep the current
  blue/teal palette, open white layout and clearly labelled starting assumption.

## Change

- Reuse the existing four metrics with subtle dividers, consistent labels and
  responsive 20–24px values; allow long values to wrap.
- Improve local heading/spacing only, without changing the global theme.
- Remove the footer planning/hardware sentence, keeping the Roventics credit.
- Update existing layout assertions and current frontend/context documentation.

## Reuse

ForecastPanel, EstimateMetric, current Material UI theme and footer attribution.

## Verify

Run frontend build and existing checks using isolated cached dependencies.
Check the two-column/narrow-phone styles and absence of the removed footer text.

## Out of scope

Backend/calculation/API/data changes, new dependencies, service recreation,
new controls/charts, commits and pushes.
