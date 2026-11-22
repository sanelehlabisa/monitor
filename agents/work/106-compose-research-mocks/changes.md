# Task 106 preparation

Inspected the existing two-script research implementation, local-only transport
guards, README, source allowlist and Task 105 context. Mailpit currently uses a
native local capture; SMS is an offline file capture. Reuse their one-pass CSV
selection/state rather than introducing a separate scheduler or sender.

Prepared prompt.md from agents/prompt.md for independent Compose capture services
and a mock SMS API in the existing runner. Scope preserves application Compose,
credentials, real contacts, existing fixtures and production-delivery boundaries.
No unresolved product question; selected loopback ports will be checked before
use. Docker's Linux engine was unavailable during read-only inspection.

Added a planned roadmap entry and current context. No implementation, package
installation, service operation, message submission, data change, commit or push.
Implementation awaits approval of Task 106.

## Implementation and approval

The owner approved Task 106 on 22 November 2026. Docker was accessible with the
necessary local tool permissions; the existing app containers were recorded
before starting only the new research project.

Added software/research/market-research/docker-compose.yaml, Dockerfile and
.dockerignore. Official Mailpit v1.31.4 and the Python base are digest-pinned.
The Docker build includes only the two existing Python sources and requirements;
no credentials, contacts, evidence or environment enters the image. Runtime
inspection confirms no SMTP/SMS credentials, .env or canonical CSV. Only ignored
dedicated capture subdirectories are mounted. No production settings were edited.

Extended send_due_messages.py with a standard-library SMS capture-server mode
and explicit loopback HTTP client option. Default SMS stays offline. Reused
send_sms, the existing CSV writer/lock, schedule/cap selector, state transitions,
templates and reports. The client ignores gateway/proxy settings and follows no
redirects. Server JSON/request/message limits, local Host/origin guards and
fictional provenance validation keep the interface scoped to mocks. The server
captures then disconnects for the uncertain-outcome check; the runner preserves
sending for manual review. No framework, dependency, schema or third script.

Updated the research README, source allowlist, research index and current
context. No files were retired or removed. No Android gateway, production sender,
DNS change, new crawl, real-contact edit, commit or push.

## Docker networking correction

The approved internal-only bridge started healthy but Docker 29.4.0 silently
omitted the requested published ports. docker port returned no mappings and
host HTTP connections were refused. Recreated only this new project on a
separate bridge with explicit 127.0.0.1 bindings. No other stack was stopped,
recreated or restarted. This is a connectivity adjustment to the local mock
setup, not a claim of outbound-network blocking. The README/context state that
limit; mocks have no forwarding/relay or real credentials/transport. No daemon,
host firewall or shared proxy changes were needed.

References used for configuration: [Mailpit Docker](https://mailpit.axllent.org/docs/install/docker/),
[Mailpit options](https://mailpit.axllent.org/docs/configuration/runtime-options/),
[Docker port publishing](https://docs.docker.com/engine/network/port-publishing/)
and the [upstream internal-network report](https://github.com/moby/moby/discussions/53256).
The Docker behavior was reproduced locally, not assumed from the report.

## Verification and retained results

63 direct checks pass; private details are in data/task106-verification.json.
The new fictional success fixture captured five exact-template emails and five
HTTP SMS requests. A fresh process, then rebuilt/restarted mock services, produced
zero duplicate sends and preserved captures. Verified actual SMTP rejection,
HTTP temporary/permanent rejection, continued later contacts, maximum three safe
attempts and held ambiguous acceptance. Weekends, outside hours, future dates,
closing minute and daily limits pass. Browser-origin/Host, malformed/oversized
payload, provenance, redirect, invalid-port and real-CSV guards pass. Existing
offline behavior remains available.

An initial fictional run encountered an OS-level atomic CSV save error. The
runner stopped, preserved sent/unknown state and did not continue submissions
after persistence failure. Cause of the file-access failure is unverified; no
writer relaxation or unsafe retry was added. Preserve its CSV/journal under
data/local-test/compose/demo/ for manual review. A new untouched fixture under
data/local-test/task106-success/ then passed the complete actual-delivery and
restart checks; controls are under data/local-test/task106-controls/. Never
reset the interrupted states or delete captures to make tests pass.

Saved hashes prove both original app Compose files, both actual .env files,
canonical contacts.csv and the owner's existing ready fixture are unchanged.
Original app container identities/start times are unchanged. Container inspection
confirms all three host port bindings use 127.0.0.1, the bridge contains only the
two mocks, and only dedicated mock data is mounted. Both new services are healthy
and remain running for the owner: Mailpit http://127.0.0.1:8026 and SMS captures
http://127.0.0.1:8086/messages. No real email or SMS was submitted.

Final whitespace, source syntax/two-script layout, 17 relative documentation
links and private-output ignore checks pass. Protected hashes still match the
before-state after all verification. Work is uncommitted; no push was requested.

## Publication authorization

The owner now requests committing and pushing Task 106 to master before preparing
the next ticket. Publish reviewed mock source/build files and documentation only;
actual configuration, CSVs and captures remain excluded. No further service or
message operation is part of this publication.
