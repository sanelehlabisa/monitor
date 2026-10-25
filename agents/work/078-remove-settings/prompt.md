# Task 078: Remove settings.py

## Aim

Remove settings.py and its configuration object entirely, using direct environment
reads in the existing modules without introducing a replacement settings layer.

## Clarifications

- Remove or shrink the reader? The user explicitly selected "Remove settings.py
  entirely" after the startup repair. Execute that requested cleanup.
- Keep the existing single .env, generated OTP secret and Compose overrides;
  removing the reader does not remove the application's required credentials.

## Change

- Remove Settings imports, constructor/state plumbing and pydantic-settings.
  Existing database, auth, SMTP and scheduler modules read their own variables.
- Pin the already-used Pydantic API library to the installed version if a fresh
  dependency resolution otherwise changes its schema contract; add no library.
- Pass only necessary primitives, such as reminder activation time and database
  connection timeout. Preserve configuration validation without printing secrets,
  cookie/HMAC/SMTP protections, reminder scheduling and endpoint contracts.
- Verify recovery copies before retiring settings.py and its obsolete model
  tests. Adapt existing behavioral tests and update active documentation/context.
- This necessary cross-module caller refactor exceeds the normal 100-line target;
  most changes remove configuration plumbing or update existing test call sites.

## Reuse

Existing environment names, validators, authentication functions, SMTP sender,
reminder lifecycle and isolated database/captured-mail verification helpers.

## Verify

No Settings/configuration replacement or stale imports; backend checks and image
build; isolated HTTP/HTTPS login, meter/ledger/forecast/logout and reminder checks.
Preserve current environment, source containers/data and certificates; clean only
owned test resources. Record actual results and recovery paths in changes.md.

## Out of scope

Credential rotation, real email, schema/data/UI/forecast changes, new dependencies,
VPS work, source-service recreation, commits and pushes.
