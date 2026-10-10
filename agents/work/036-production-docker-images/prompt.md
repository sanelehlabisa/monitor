# Task 036: Production Docker images

## Aim

Prepare production frontend/backend images while preserving local development
reload (part of Ticket 57).

## Clarifications

- The user selected Task 036 only and approved Nginx serving the built frontend
  and forwarding /api requests to the backend.
- Keep development reload unchanged. No npm/Python dependencies or VPS changes.

## Change

- Add named development/production targets to the existing Dockerfiles. Build
  frontend assets with the lockfile; serve only the output and approved branding
  through a pinned Nginx runtime, with SPA fallback and /api proxying.
- Run production Uvicorn without --reload. Reuse existing Python dependencies;
  keep secrets supplied at runtime and exclude local env files from builds.
- Set development Compose to the development targets; retain its current
  commands, mounts, ports and environment setup.
- Document image build/run requirements and remaining deployment work; update
  context and record results in changes.md. Stay within 100 implementation lines.

## Reuse

- Existing Dockerfiles, npm lockfile/build, requirements.txt, relative /api
  requests, backend health endpoint and development Compose.

## Verify

- Build both production images and smoke-check static assets, SPA fallback,
  proxied API status/body and backend health in disposable local containers.
- Confirm production has no reload/dev server or bundled local env files;
  verify development targets still build and Compose retains reload behavior.
- Clean up only this task's containers/network. Run git diff --check.

## Out of scope

- Tasks 037-038, production Compose/env rollout, migrations/backup operations,
  TLS, DNS, VPS access, registry publishing, CI, household validation, new app
  features or dependency upgrades. No commit/push without a separate request.
