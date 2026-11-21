# Task 098: Market-research pipeline tickets

## Outcome
Create small ordered tickets for a local Python contact-research pipeline.
This task creates plans and privacy exclusions only, not executable features.

## Questions and answers
- The user requests tickets now, with implementation approved separately.
- New research belongs under software/research/, grouped by experiment.
- Private inputs and generated files stay inside that experiment and out of Git.
- No unresolved planning questions. Locate the existing survey and confirm the
  local model, seed scope and sender details in their respective future tickets.

## Scope and reuse
- Add Ticket 71.1–71.11 and detailed acceptance under
  software/research/market-research/README.md.
- Link the plan from short root/software research indexes; update context.
- Add default-deny Git rules for this experiment, allowing reviewed source and
  documentation only. Preserve existing backend forecasting research in place.
- Reuse existing agent workflow, typed Python conventions and ignored environments.

## Verification
Check relative links, ticket order, required CSV columns, ignore coverage,
whitespace and the documentation/configuration-only diff. Use hypothetical
private paths, without creating or collecting contact data.

## Exclusions
No crawler/LLM/sender implementation, dependency installation, contact gathering,
survey edits, email/DNS/service changes, application changes, commits or pushes.
