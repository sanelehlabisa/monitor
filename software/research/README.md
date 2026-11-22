# Software research

Keep each experiment in its own subfolder, separate from application code and
dependencies. Version source and concise instructions; keep private inputs and
generated files inside that experiment and excluded from Git.

- [Market research](market-research/README.md): bounded, resumable public email/phone
  discovery and saved-file import; one private CSV with source context and optional
  loopback LM Studio.
  Access restrictions and manual deferrals remain enforced. Two source scripts
  cover collection and configured CSV sending/reporting. Task 108 reads its own
  .env: Mailpit/fictional data by default, real SMTP after owner configuration,
  hard five/day/channel and no hour/weekday gate. Live SMS needs a chosen gateway.
  The separate Compose capture stack does not change app services/configuration.
- [Forecasting](../backend/research/forecasting/README.md): existing isolated
  simulator, retained in its current location.

Each implementation needs its own approved work prompt. Research does not
authorize app integration, contact collection or outreach.
