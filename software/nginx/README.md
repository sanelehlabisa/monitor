# Production Nginx and shared HTTPS

The existing public Nginx owns public HTTP80/HTTPS443 and Certbot certificates. Monitor's frontend
serves HTTP80 on the shared `roventics_proxy` network as `monitor-frontend`, with
an optional loopback diagnostic port `127.0.0.1:8082`. Its backend and database
have no published ports. The frontend proxies `/api` to the private backend.

There are exactly two Compose files and one ignored `software/.env`. Development
runs independently at `http://localhost:5173`, with Compose overriding URL/SMTP
for Mailpit. Production now requires the shared proxy; the previous standalone
local HTTPS setup is retired. Existing private certificate files are preserved,
but are no longer mounted. No launcher or local certificate script is required.

## 1. Prepare Monitor

On the VPS, point the `monitor.roventics.com` A record to its public IPv4 address.
Any AAAA record also needs working IPv6. Keep all existing DNS records/sites.
In this installation's `software/.env`, set:

```dotenv
APP_BASE_URL=https://monitor.roventics.com
```

Use real SMTP credentials, an independent strong database password and a unique
OTP secret. Database credentials are embedded in a URI: a long random hex
password avoids reserved-character escaping. Do not overwrite an existing
installation's credentials. Production contains no Mailpit and still forces
automatic monthly reminders off. Development keeps its Compose overrides.

Confirm the existing public proxy belongs to `roventics_proxy`. Create that
network only if absent. Check that Monitor's private `172.30.70.0/24` subnet does
not overlap an existing network; if changing it, also update the backend's
trusted-proxy CIDR in Compose. From `software/`:

```sh
docker network inspect roventics_proxy
# Only if the network does not exist:
docker network create roventics_proxy

docker compose -f prod.docker-compose.yaml config --quiet
docker compose -f prod.docker-compose.yaml up -d --build --wait
```

Fresh production databases run `schema.sql` then `seeds/010-users.sql`, creating
`hlabisasanele730@gmail.com` as admin and **no meters**. Create meters in the app.
Development additionally runs `020-demo-meters.sql`. Initialization runs only on
an empty database volume: existing data and manually assigned roles are never
reset or re-seeded. See [database setup](../database/README.md). Never remove a
data volume to force seeding; inspect an existing account separately if needed.

## 2. Deploy the shared proxy route

The public edge needs the Monitor hostname/upstream route. Preserve its other
virtual hosts and certificate settings; route configuration belongs to the edge
operator, not this application's runtime. The equivalent standalone
[Monitor fragment](monitor-edge.conf.example) is provided for comparison; do not
append it a second time or replace the shared configuration with it.

The route uses the existing `/etc/letsencrypt/live/roventics.com/` certificate and
`/var/www/certbot` webroot. Confirm those files already exist
and are mounted in the shared proxy. Existing certificates allow Nginx to load
the new HTTP challenge route before the certificate covers Monitor. Public
Monitor HTTPS is not ready until its hostname is included in that certificate.

In the public edge's deployment directory, validate and reload only that proxy:

```sh
docker compose -f docker-compose.yaml build nginx
docker compose -f docker-compose.yaml run --rm --no-deps nginx nginx -t
# Only after validation succeeds:
docker compose -f docker-compose.yaml up -d --no-deps nginx
```

Both Monitor upstream hops use runtime Docker DNS, so Monitor being absent does
not prevent shared Nginx startup. Normal HTTP requests redirect to HTTPS; the
ACME path is served from the existing webroot. Check the HTTP challenge route
without changing other virtual hosts.

## 3. Extend the existing certificate

Inspect `sudo certbot certificates`. If its `roventics.com` certificate already
covers Monitor, skip issuance. Otherwise preserve **every existing domain** and
add `monitor.roventics.com`. Have the edge operator expand the actual existing lineage using its current
webroot, retaining every SAN shown by Certbot and adding Monitor. Do not replace
the domain list with Monitor alone. Validate the actual edge's Nginx configuration
before reload, and verify the resulting certificate covers this hostname.

Use the actual certificate/container names if the live installation differs.
Reuse its current renewal timer and validated Nginx reload hook; do not add a
second renewal mechanism. Verify renewal with `sudo certbot renew --dry-run`.
See [Certbot's certificate-update instructions](https://eff-certbot.readthedocs.io/en/stable/using.html#re-creating-and-updating-existing-certificates).
No VPS operation or public certificate issuance is performed by this repository change.

## 4. Check the deployed app

Open `https://monitor.roventics.com`, verify a trusted certificate, receive a real
OTP, log in as the seeded admin, and create a meter and balance. Check estimates,
sharing, logout and that a restart retains records. Admins select **All** for
global meter access. Existing databases keep their existing roles.

Monitor's edge limits OTP issuance by connection address and globally; other
routes are unaffected. The inner frontend retains foreign-origin write checks,
framing protection and canonical forwarded headers. Backend authentication and
meter permissions remain required. The private diagnostic port is not a public
login URL. Public browser traffic must use HTTPS through the shared proxy.

Isolated checks use synthetic records and captured mail; they cannot establish
VPS DNS, certificate issuance or real SMTP delivery. Inspect the existing shared
Nginx version before deployment; this change does not upgrade its image. Keep
logs private and never print OTPs, cookies or environment secrets.
