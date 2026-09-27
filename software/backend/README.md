# Backend

FastAPI REST service with a reusable application factory, typed configuration
and a process-only health endpoint. Settings use the `MONITOR_` prefix; see
`.env.example` for supported development values.

Run the focused test suite from this directory:

```powershell
python -m pytest
```

`GET /health` reports the service name, version and configured environment. It
does not check PostgreSQL or Keycloak; those integrations belong to Tickets 4
and 5. Ticket 9 adds reading submission and latest/history queries after the
device and reading models exist.

Ticket 10 must enforce scoped device credentials and ownership before real
uploads. Keycloak handles user authentication, not an assumed device password.
Define units, UTC timestamps, duplicate/retry semantics, validation errors and
confidence rejection with Tickets 8-9. Do not invent missing OCR values.

Use clear typed Python with docstrings and reusable functions. Production
deployment settings are not defined yet.
