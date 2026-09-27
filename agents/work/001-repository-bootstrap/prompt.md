# Task 001: Monitor repository bootstrap

## Aim

Create the Monitor repository foundation and a concise, phased todo roadmap.

## Clarifications

- Repository: sibling of Switch, using https://github.com/sanelehlabisa/monitor.git (currently empty).
- Scope: repository, workflow and README/todo files only; no working application yet.
- Layout: separate hardware/software; no docs directory; future Docker and environment files belong under software/.
- OCR: plan saved-photo tests on PC, simple recognition first and PyTorch if needed; verify on-device feasibility later.

## Change

- Adapt AGENTS.md, agents rules/context/prompt template and the PR template for Monitor.
- Add concise root/component READMEs, gitignore and sequential phased tickets starting at 1.
- Plan non-invasive camera reading of one prepaid meter, REST, FastAPI, PostgreSQL, Keycloak and a frontend; defer implementation.
- Adapt Switch's meter.README.md into Monitor's main README (developer clarification at approval); keep no duplicate and update only current Switch references.
- Initialize local Git, connect the supplied remote, commit and push Monitor; separately commit/push the limited Switch documentation cleanup.

## Reuse

- Switch's engineering rules, task workflow, documentation style and parked Meter research.

## Verify

- Check links, ticket numbering, product boundaries, ignored secrets and both Git diffs.
- Confirm pushes match local commits and unrelated Switch files remain untouched.

## Out of scope

- Docker services, application code, OCR/model training, firmware, CAD, payments and deployment.
- No MQTT for V1; later anomaly signals are not proof of theft, and top-ups require authorised interfaces.
