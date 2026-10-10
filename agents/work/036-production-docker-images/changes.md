# Task 036: Production Docker images

## Results

- Added named development/production targets to both existing Dockerfiles.
  Production frontend builds from the existing lockfile and serves dist/ through
  version-pinned Nginx; production backend uses the existing Python dependencies,
  runs as UID/GID 10001 and starts Uvicorn without reload.
- Production backend defaults to production mode, retaining the existing refusal
  of the development OTP secret. No runtime secret or local env file is copied.
- Added a small Nginx config: preserve /api paths and upstream responses, SPA
  fallback for application routes and 404 for missing built assets.
- Development Compose changes only two build-target selections; existing reload
  commands, environment configuration, ports and mounts are retained.
- Implementation totals 45 changed lines across Dockerfiles, ignores, Compose
  and the new Nginx configuration; application code and dependencies are unchanged.
- Updated README/runtime requirements and repository context. This is image
  preparation only; Tasks 037-038, actual deployment and household trials remain
  separate. The user subsequently requested commit/push after Docker recovered.

## Reuse

- Reused existing Dockerfiles, npm lockfile/build, Python requirements, backend
  production-secret validator, process-health endpoint and relative API paths.
- Confirmed the Nginx tag in the [official image list](https://raw.githubusercontent.com/docker-library/official-images/master/library/nginx).
  Used [Docker multi-stage targets](https://docs.docker.com/build/building/multi-stage/)
  and the documented [proxy_pass path behavior](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass).
- Prepared a dependency-free temporary smoke runner under ignored
  .tmp/task036/. It uses a unique disposable Docker network/containers, a generated
  runtime secret and unauthenticated requests; no database or SMTP access needed.

## Verification

- PASS: git diff --check; temporary smoke runner passes node --check.
- PASS: Compose parses with both development targets; comparison with HEAD proves
  those two target lines are the only development-stack configuration changes.
- PASS: static checks confirm named image targets, env-file exclusions,
  production backend command/mode and dist-only frontend serving configuration.
  These are source checks, not proof that image builds or runtime behavior pass.
- Initial blocker: both production docker build commands stopped before building because
  the Docker Desktop Linux engine's unversioned /_ping endpoint returned HTTP 500.
- Read-only diagnostics found the same error on both local Docker pipe contexts.
- The user subsequently approved restarting Docker Desktop. Its normal restart
  command stalled, so identified Docker Desktop/backend/build processes were
  stopped, only `docker-desktop` was terminated through WSL, and Desktop was
  relaunched. No global WSL shutdown, context change or data reset was performed.
- Initial restart still failed: Docker logs reported
  `Wsl/Service/CreateInstance/HCS_E_CONNECTION_TIMEOUT` and bootstrap termination.
  WSL and VM compute services were running, but `docker-desktop` was stopped.
- Recovery confirmed on 2026-10-10 after the user reported Docker working:
  engine version 29.4.0 answers requests and all four Monitor development
  services are healthy. No further WSL/Windows restart was needed in this turn.
- PASS: production and development builds for both frontend and backend,
  using only task-specific `monitor-task036-*` image tags.
- PASS: disposable runtime checks for nginx -t, built JS/logo, SPA fallback,
  missing-assets 404, preserved API paths/query/body/status/JSON, secure logout
  cookie headers, production process health and missing-secret startup refusal.
- PASS: production image inspection confirms no reload/dev server, no bundled
  local env files, no Node/npm in the Nginx runtime and non-root backend startup.
  Development commands retain Vite and Uvicorn reload; Compose behavior is unchanged.
- PASS: task-created containers/network cleaned up, with none remaining under
  the task label. Existing services/data/volumes were not changed by the checks.
  Task images remain as local build artifacts. HTTPS login, database/SMTP
  integration and real deployment remain outside this image-only task.
