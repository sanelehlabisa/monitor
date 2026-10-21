# Production: existing VPS HTTPS edge

Task 070 prepares files and isolated verification, not a live deployment. Use
`monitor.roventics.com` on the existing Roventics VPS. Do not run these operator
steps against the VPS until its deployment is separately approved (Ticket 57.2).

Internet -> existing Nginx :80/:443 -> monitor-frontend:80 -> backend:8000.
Only the frontend joins external `roventics_proxy`; PostgreSQL/backend have no
published ports. The backend retains outbound SMTP access. Monitor adds no TLS
container, host listener, certificate volume or renewal scheduler.

## 1. Inspect before changing anything

Confirm the reported `roventics-nginx-1` name, its Compose working directory,
loaded configuration/includes, certificate/webroot mounts, network, Nginx version
and Certbot installation. Inspect metadata, never print environment secrets or
private keys. Do not replace the shared Nginx file with Monitor's example.

Task 072's patched image pin applies only to Monitor's inner frontend gateway,
not the existing shared VPS edge. Check that edge's actual version against the
[vendor security advisories](https://nginx.org/en/security_advisories.html) before
deployment; any needed shared-edge patch requires separate approval. Local test
edge versions do not verify or upgrade the VPS. No VPS changes were made here.

```sh
docker ps --format 'table {{.Names}}\t{{.Ports}}'
docker network inspect roventics_proxy --format '{{json .IPAM.Config}}'
docker network ls
docker exec roventics-nginx-1 nginx -v
sudo certbot --version
sudo certbot certificates
systemctl list-timers --all | grep -i certbot
```

Also inspect the existing cron/deploy-hook configuration if renewal is not owned
by that timer. Keep one existing renewal owner. Inspect all Docker network
subnets: the Monitor private proxy network uses `172.30.70.0/24`. If this overlaps
any existing route/network, stop and choose a non-overlapping subnet in BOTH the
Compose IPAM and Uvicorn trusted-proxy setting before deployment. Do not change
another project's network. The shared network must already exist and the public
proxy must already belong to it; do not recreate it blindly.

Confirm `monitor.roventics.com` A/AAAA records resolve to this VPS, not an address
copied from a repository. An AAAA record requires working IPv6 routing/listeners.
Preserve root, Job Talk, mail and all other DNS records/sites.

## 2. Configure this installation

From the VPS checkout's `software/`, create `.env` from
[.env.example](../.env.example) ONLY if `.env` does not
already exist. Never copy/overwrite the development environment or another app's
file. Keep restrictive file permissions and fill every required deployment value.
Use one `.env` per installation, never commit it or pass secrets as build args.
This is the same template as development, not another active environment file.
Its local Mailpit host, database password and OTP secret MUST be replaced for
the VPS. The local port/mode values can remain: production Compose fixes production
mode and does not publish those ports. Do not copy the local reminder cutoff.

- `APP_DOMAIN=monitor.roventics.com` derives the public HTTPS origin and gateway
  hostname. No duplicate public/API URL or admin email setting is needed.
- Choose independent database credentials and a unique random
  `MONITOR_OTP_HMAC_SECRET` (not the committed development secret). Database name,
  user and password are embedded in a PostgreSQL URI: use URI-unreserved values,
  for example a long random hex password, not an unencoded `@`, `:`, `/`, `#` or `%`.
- Supply the provider's real SMTP host/port, TLS choice, credentials and sender.
  Single-quote literal `.env` passwords containing `$` to prevent interpolation.
  `SMTP_SECURE=true` uses implicit TLS; false upgrades with STARTTLS when offered.
  The sender refuses to authenticate without encryption. Mailpit is not deployed.
- Production Compose deliberately forces automatic monthly reminders off, even
  if an inherited environment contains a local activation cutoff. External
  activation needs a separately approved saved cutoff and compatibility check;
  never copy the local Mailpit cutoff or invoke the finite reminder CLI casually.

Validate without printing rendered secrets:

```sh
docker compose --env-file .env -f prod.docker-compose.yaml config --quiet
docker compose --env-file .env -f prod.docker-compose.yaml up -d --build --wait
docker compose --env-file .env -f prod.docker-compose.yaml ps
```

The production project owns its own persistent `postgres-data` volume. On an
empty volume PostgreSQL runs only `database/schema.sql`: no demo users/meters,
admin seed, migrations or startup role changes. Existing volumes are never
upgraded by restart. If initialization fails partway or an existing schema differs,
stop and inspect; do not delete volumes or replay setup/seed SQL as a repair.
This ticket transfers no development data and adds no backup work; preserve all
existing recovery artifacts. `/health` checks process health, not DB/SMTP readiness.

## 3. Add only Monitor's public edge route

[monitor-edge.conf.example](monitor-edge.conf.example) contains Monitor-only maps,
rate-limit zones and two server blocks for the existing Nginx **http context**.
Inspect its real loaded includes/mounts first; merge all of these Monitor entries
into that managed configuration (maps/zones stay outside the server blocks).
Do not replace its top-level configuration, root/Job Talk vhosts or Docker mounts.

The HTTPS edge budgets only `POST /api/auth/request-otp` (also its trailing-slash
form): 10 requests/minute per connection address with burst 5, and 60/minute
overall with burst 10. Excess requests receive 429 without delayed processing.
Other routes are exempt. The client key is the real edge connection address,
before forwarding headers are stripped; do not move this limiter to the inner
gateway or trust client-supplied forwarding headers. Shared-IP users share a
budget; these small pilot limits do not eliminate distributed/provider abuse.

The frontend gateway rejects unsafe API methods with a foreign/null Origin or
`Sec-Fetch-Site: same-site/cross-site`; only the configured HTTPS Origin is trusted.
Headerless non-browser clients remain supported but still require backend auth.
GET/HEAD/OPTIONS are unchanged. `X-Frame-Options: DENY` and CSP `frame-ancestors
'none'` prevent framing; this is not a full content-security policy. Development
Vite is unchanged. No extra environment settings, CSRF service or client-IP trust
layer is introduced.

The example uses the existing `/etc/letsencrypt/live/roventics.com/` certificate
and `/var/www/certbot` HTTP webroot. Confirm those exact paths first; if the
inspected certificate name/webroot differs, adapt only the Monitor blocks.
The certificate must already be readable for testing the TLS block. If no selected
certificate exists, enable only the HTTP challenge/redirect block until issuance
creates it, then add the TLS block. Existing certificates need not yet cover
Monitor for its HTTP challenge, but HTTPS will not validate until they do.
Both proxy hops use Docker DNS resolution on requests, allowing upstream
replacement/absence without a shared Nginx startup dependency on Monitor.

```sh
docker exec roventics-nginx-1 nginx -t
docker exec roventics-nginx-1 nginx -s reload
```

Reload only after successful validation. Verify the HTTP challenge path is
served from the existing webroot, not redirected into the app. Other HTTP
requests redirect to the fixed HTTPS hostname. Confirm other sites still work.

## 4. Reuse certificate issuance and renewal

Read `sudo certbot certificates` first. If the existing valid certificate already
covers `monitor.roventics.com`, skip issuance. Otherwise use host Certbot's
`certonly --webroot -w /var/www/certbot` with the **inspected** `--cert-name`,
existing `--key-type` (`ecdsa` or `rsa`), `--expand`, and one `-d` for **every current
certificate name**, plus `-d monitor.roventics.com`. Construct/review that full
list before execution; do not drop `www`, Job Talk or any other existing name.
For an absent lineage, omit `--expand` and issue under an inspected, non-conflicting
certificate name, then use its paths in Monitor's TLS block; preserve other lineages.
Do not delete working certificates, use standalone issuance that stops Nginx,
or mount private keys into Monitor containers. Public issuance is not part of
Task 070 and is not proven by its isolated self-signed TLS checks.

After issuance validate/reload Nginx as above and verify HTTPS for Monitor AND
all existing certificate names/sites. Reuse the installed renewal timer/cron and
webroot renewal configuration. Its existing deploy hook must run `nginx -t`
successfully before reloading `roventics-nginx-1`; do not add a second hook/timer.
Review any old stop-Nginx standalone hook before changing it. Run the installed
Certbot's supported renewal dry-run and separately exercise the reviewed reload
hook if that version does not run deploy hooks during dry-runs.

## 5. First admin and live acceptance

After HTTPS/SMTP work, sign in normally as `hlabisasanele730@gmail.com`. Open OTP
signup creates a regular user; a separate explicit operator action may promote
that exact verified account in this installation's DB:

```sh
docker compose --env-file .env -f prod.docker-compose.yaml exec database \
  sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

At the SQL prompt, run:

```sql
UPDATE monitor.users SET type = 'admin'
WHERE email = 'hlabisasanele730@gmail.com'
RETURNING id, type;
```

Require exactly one returned account. Zero means stop/check normal signup, not
insert a seed or bypass login. Future roles remain manual DB edits; login/startup
never re-promotes accounts. Live signup/admin assignment is not executed by 070.

Ticket 57.2 must verify trusted HTTPS/no mixed-content redirects, emailed OTP,
login/logout, meter creation/deep links, balance/top-up edits, meaningful forecast,
sharing/member/admin isolation and restart persistence. `/api/me` must reject
signed-out requests, including outside clients that forge forwarding headers.
Routine access logging is disabled only for Monitor's production Uvicorn and
Nginx blocks, avoiding search-email query strings in normal request logs. Keep
application/error logging, but treat those logs as private: Nginx errors can
still include request URIs. Redact private records before sharing; never log
OTPs/cookies or commit household data. Other sites' logging is unchanged.

For upgrades, rebuild only this project's changed services with the same explicit
Compose/env selection. Docker DNS can take several seconds to refresh after
upstream replacement; verify recovery and health rather than restarting other
sites. Never use global prune, `down -v`, seed replay or unreviewed SQL upgrades.
If Monitor fails, remove/disable only its new edge blocks and validate/reload;
leave the shared certificate, other sites and Monitor's persistent data intact.

Reference behavior: [Nginx proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass),
[Uvicorn trusted proxy settings](https://uvicorn.dev/settings/#http),
[Certbot certificate updates](https://eff-certbot.readthedocs.io/en/stable/using.html#re-creating-and-updating-existing-certificates).
