# Software research

Keep each experiment in its own subfolder, separate from application code and
dependencies. Version source and concise instructions; keep private inputs and
generated files inside that experiment and excluded from Git.

- [Market research](market-research/README.md): bounded, resumable public email/phone
  discovery and saved-file import; one private CSV with source context and optional
  loopback LM Studio.
  Access restrictions and manual deferrals remain enforced. Task 105 provides
  fixed messages and verified local SMTP/SMS-mock tests. Two source scripts cover
  collection and CSV-controlled due delivery/reporting; production is disabled
  pending separate approval. Task 106 adds a separate Compose stack for Mailpit
  and a local SMS HTTP capture, without changing app services/configuration.
- [Forecasting](../backend/research/forecasting/README.md): existing isolated
  simulator, retained in its current location.

Each implementation needs its own approved work prompt. Research does not
authorize app integration, contact collection or outreach.
