# Software research

Keep each experiment in its own subfolder, separate from application code and
dependencies. Version source and concise instructions; keep private inputs and
generated files inside that experiment and excluded from Git.

- [Market research](market-research/README.md): planned local contact discovery,
  context enrichment and a single contacts CSV. Offline setup and resumable
  crawling/access diagnostics are ready. The live review has unresolved access
  outcomes. HTML/plain-text/PDF responses are now extracted in memory, without
  saving originals first. Contact context and required LM Studio enrichment are next.
- [Forecasting](../backend/research/forecasting/README.md): existing isolated
  simulator, retained in its current location.

Each implementation needs its own approved work prompt. Research does not
authorize app integration, contact collection or outreach.
