# Agent instructions

Read `agents/context.md`, `agents/rules.md` and the nearest `README.md`.
Load historical work records only when the task needs them.

## Workflow

1. Inspect relevant files and reuse existing work.
2. Ask focused questions about unclear requirements; do not invent answers.
3. Before implementation, create the next `agents/work/NNN-short-title/prompt.md`
   from `agents/prompt.md` with the answers, scope and verification.
4. Present the prompt in chat and obtain approval before building.
   Existing explicit approval covers only its approved scope.
5. Implement that scope, verify it and record results/reuse/checks in `changes.md`.

Tickets are plans, not implementation approval. Keep tasks small and IDs stable.
Do not commit/push, publish, change live data or restart services without authorization.
Preserve history, research, unique sources and user files. Before retiring files,
check dependencies/recovery and record exact paths in `changes.md`.
