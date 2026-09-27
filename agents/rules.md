# Engineering Rules

## Code

- Prefer clear, junior-friendly code over clever or compressed code.
- Search for reusable functions/patterns before adding new ones.
- Extend existing code when practical instead of duplicating it.
- Keep functions focused and names descriptive; explain why in comments.
- Update tests for changed behaviour and run the smallest relevant suite.
- Do not add dependencies, change architecture or expand scope without approval.

## Python

- Add type hints to function parameters and return values.
- Add concise docstrings to public modules, classes and functions.
- Document private helpers when their purpose is not obvious.

## Review size

- Aim for at most 100 changed implementation lines per PR; tests, docs and generated files are excluded.
- Split larger work into numbered tasks. Explain necessary exceptions in prompt.md.
- Keep commits focused on one concern.

## Documentation and data

- Root README: project context and short phased ticket summaries.
- Closest component README: detailed requirements and implementation context.
- Work records: concise, factual changes, reuse and actual verification results.
- No docs directory. Docker/config files stay under software/.
- Do not commit real secrets, meter images, customer information or private bills.
- Prefer simple measured approaches. Do not call desktop tests hardware validation.
- Never label an anomaly as proof of tampering or theft.

## Task workflow

1. Read context, rules, relevant README and existing code.
2. Ask focused questions until aim, scope, reuse, checks and exclusions are clear.
   Offer clickable choices when available, but repeat essential questions in chat.
3. Allocate the next NNN-short-title directory under agents/work/.
4. Fill prompt.md from agents/prompt.md, paste it into chat and wait for approval.
5. Implement and verify only approved work.
6. Write changes.md with results, reused code and checks actually run.

Do not touch sibling repositories without explicit authorisation. Do not start
future tasks merely because their roadmap entries exist.
