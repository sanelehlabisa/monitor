# Authentication

Keycloak provides local development user authentication. Compose imports the
`monitor` realm, its public `monitor-web` browser client and one clearly fake
development user from `realm/monitor-realm.json`. The browser client uses the
Authorization Code flow with PKCE and has no client secret.

Keep any replacement development credentials in ignored environment files. The
committed realm contains only sanitised, explicitly fake local data—never real
accounts or tokens. Browser clients must not contain a client secret. Device
submission credentials and owner-scoped access belong to Ticket 10, not copied
user credentials.

The committed development login is `monitor.developer` / `monitor_dev_only`.
It is not a real account and must never be reused outside local development.
Realm import only creates a missing realm; reset the local Docker volumes if a
changed import must be applied from scratch.

The backend validates RS256 access tokens for issuer, audience and expiry.
Frontend login is Ticket 6. Device credentials and owner-scoped submission stay
separate in Ticket 10.
