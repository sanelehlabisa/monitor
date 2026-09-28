# Task 005: Authentication baseline

## Aim

Add reproducible local user authentication with Keycloak and backend bearer-token validation without introducing device credentials or frontend screens.

## Clarifications

- Question: What should the authentication baseline include? Answer: Add a `monitor` realm, a public PKCE browser client with no secret, a fake development user, backend JWT validation and a protected `/auth/me` endpoint.
- Question: What remains public or deferred? Answer: Keep `/health` public, defer browser login/UI work to Ticket 6 and device credentials to Ticket 10.

## Change

- Add a sanitised, reproducible Keycloak realm import for local development.
- Configure a public `monitor-web` client for Authorization Code flow with PKCE and localhost-only development redirects/origins.
- Add one clearly fake development user without committing a real account or token.
- Add typed Keycloak issuer, audience and JWKS settings to the backend.
- Add reusable bearer-token validation and a protected `/auth/me` endpoint returning typed identity claims.
- Add focused tests for missing, invalid and valid tokens while preserving the public health endpoint.
- Update authentication, backend and environment documentation, then mark Ticket 5 complete after verification.

## Reuse

- Extend the existing backend settings and FastAPI application factory.
- Reuse the existing Keycloak Compose service and database.
- Preserve the current process-only `/health` contract and Material UI frontend boundary.

## Verify

- Run the backend pytest suite.
- Validate the Compose configuration and rebuild affected images.
- Start the four-service stack and confirm every service becomes healthy.
- Confirm Keycloak imported the realm, public PKCE client and fake development user.
- Confirm `/health` works without a token and `/auth/me` rejects a missing token.
- Run `git diff --check`.

## Out of scope

- Frontend login screens, session UI or authenticated API calls.
- Client secrets in browser code.
- Device credentials, device ownership or meter-reading authorisation.
- Roles, admin hierarchies, production identity configuration or real users.
- Database-backed application users or domain tables.
