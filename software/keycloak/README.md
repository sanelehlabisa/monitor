# Authentication

Keycloak is planned for local development users. Ticket 2 starts the service;
Ticket 5 adds a minimal realm/client and API/frontend integration. Avoid
speculative role hierarchies; users/devices/admin remain requirements to refine.

Keep development credentials in ignored environment files. Commit only
sanitised reproducible configuration, never real accounts or tokens.
Browser clients must not contain a client secret. Device submission credentials
and owner-scoped access belong to Ticket 10, not copied user credentials.

No production identity configuration or runnable realm exists yet.
