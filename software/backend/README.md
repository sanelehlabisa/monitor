# Backend

Planned FastAPI REST service. Ticket 3 establishes configuration, a health
endpoint and small tests. Ticket 9 adds reading submission and latest/history
queries after the device and reading models exist.

Ticket 10 must enforce scoped device credentials and ownership before real
uploads. Keycloak handles user authentication, not an assumed device password.
Define units, UTC timestamps, duplicate/retry semantics, validation errors and
confidence rejection with Tickets 8-9. Do not invent missing OCR values.

Use clear typed Python with docstrings and reusable functions. Task 002 adds
only a development health placeholder; API behaviour and production settings
do not exist yet.
