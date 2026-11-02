# Engineering rules

- Keep code small, readable and focused; reuse existing functions and patterns.
- Use Python type hints, typed schemas and explicit types where supported.
  Add concise comments/docstrings when useful.
- Use direct parameterized SQL, not an ORM, when database work is in scope.
- Add no speculative tables, indexes, dependencies, frameworks or services.
  Preserve existing constraints, security and data; justify necessary additions.
- Do not create test files by default. Preserve existing checks; use the smallest
  relevant build, existing check or manual walkthrough and record actual results.
- Keep secrets and private user/research data out of Git and tool output.
- Root README: short introduction, setup links and grouped ticket titles.
  Component READMEs: detailed requirements. Context: current facts/priorities.
  Historical results stay under `agents/work/`.
- Follow the workflow in `AGENTS.md`; do not duplicate it in other guides.
