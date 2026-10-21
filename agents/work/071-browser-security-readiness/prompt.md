# Task 071: Browser and Security Readiness

## Aim

Test the current production candidate locally and give an evidence-based merge/deployment recommendation for Tickets 65/57, not a guarantee of zero vulnerabilities.

## Clarifications

- Use an isolated production stack, synthetic regular/admin/shared users and captured email.
- Findings only: no automatic fixes, running-app changes, VPS actions or Git publication.

## Change

- Reuse Task 070's production stack and Task 066's browser driver, removing API mocks. Use real local HTTPS/API/DB/mail through desktop/mobile views, normal UI OTP login and admin promotion only in the synthetic DB, not injected sessions.
- Create only labelled task-owned resources and synthetic fixtures. Browser ports bind loopback only; map Monitor and a synthetic sibling only in the new profile. Pin local test certificates and allowlist owned requests; never change system DNS/hosts/trust or contact the real VPS. Keep monthly automation off and capture all mail locally.
- Check login/logout, name-only meters, balance/top-up create/edit/delete, unavailable/valid forecasts, sharing/removal, admin All/My and reload/deep links. Verify unrelated users, revoked members, invalid/expired/replayed OTPs and sessions cannot access protected operations.
- Review SQL/input handling, HTML rendering, cookie/proxy/origin boundaries, OTP abuse controls and current dependency/vendor advisories. Use bounded synthetic CSRF/framing probes, verifying actual fixture state changes rather than CORS headers alone; no memory-corruption exploits, flooding or public-host probes.
- Record reproducible findings with severity, affected files, demonstrated versus suspected impact and the smallest proposed follow-up fixes. Separate merge blockers, deployment gates and residual risks; do not silently upgrade Nginx or weaken checks to obtain a pass. Update work results/current context without closing live acceptance.

## Reuse

- Production images/config, existing authorization tests, Task 070 fixture/cleanup helpers and Task 066 Edge CDP utilities; no new application dependency, service or architecture.

## Verify

- Compare read-only source identities/config hashes before/after; inspect the ignored source .env by hash only, never its values. Report actual checks, synthetic screenshots and advisory/scanner coverage/limits. Keep tokens/OTPs/network bodies/TLS keys ignored and out of chat/Git; share only public package metadata with advisory services, never repository uploads. Clean only verified task-owned resources.
- End with ready/not-ready plus specific blockers. Local self-signed TLS and captured SMTP do not validate real certificates/provider delivery/VPS security or prove vulnerability-free software.

## Out of scope

- Production-code/config/dependency fixes, source DB/login/mail/env/service changes, external mail, reminder activation, VPS/DNS/SSL changes, backups, sibling edits, commits, merges and pushes. Any fix or live deployment needs separate approval.
