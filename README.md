# Roventics Monitor

A non-invasive camera reader for existing prepaid electricity meters.
Capture the display, extract its balance with OCR, and show readings/history
in an application. Start with **one real meter**, not universal support.

## V1 scope

Prove reliable readings on our own accessible meter, then a small end-to-end
PoC: camera -> OCR -> HTTP/REST API -> PostgreSQL -> web application.
Develop recognition using saved photos on PC first; decide where OCR runs
after measuring accuracy and device memory requirements.

Never open, electrically modify, bypass or interfere with the installed meter.
Use a removable external camera mount where safe and permitted. Monitor does
not actuate household loads; that belongs to [Switch](https://github.com/sanelehlabisa/switch).
No MQTT, top-ups, production deployment or anomaly ML in the initial PoC.

## Product context

This plan continues the former Switch `meter.README.md`, now maintained here
as the main README rather than a duplicate document. A municipal councillor
discussion highlighted meter shortages, installation delays, failures, cost
and suspected tampering. First prove useful readings for a household; later
evaluate needs of municipalities, utilities and property managers.

Anomaly flags are investigation signals, **not proof of theft or tampering**.
Reading/image storage needs consent, minimal retention and access controls.
Future prepaid/postpaid payment facilitation needs authorised providers,
auditability and explicit failure handling; it is not a V1 feature.

## Planned tech stack

- Device: ESP32-class camera hardware and C/C++; final board not selected.
- OCR: Python; simple display-specific recognition first, PyTorch if needed.
- API/data: FastAPI, PostgreSQL and explicit SQL through Psycopg; no ORM.
- Identity: Keycloak; device credentials designed separately from user login.
- Web: React with Material UI; minimal current balance, history and device-status screens.
- Development: Docker Compose under `software/dev.docker-compose.yaml`.

Long inference time is acceptable for the initial reading experiment, but
memory fit and accuracy still need measurement. Monthly reporting does not
mean monthly-only capture; low-balance alerts and consumption estimates need
a separately chosen reading frequency.

## Repository structure

```text
monitor/
|-- AGENTS.md
|-- agents/             # rules, context, template and numbered work
|-- .github/            # PR template
|-- hardware/
|   |-- firmware/
|   |-- camera/
|   |-- mechanical/
|   `-- experiments/
`-- software/
    |-- backend/
    |-- frontend/
    |-- database/
    |-- keycloak/
    `-- ocr/
```

Documentation stays in these READMEs; no `docs/` directory. Development
Compose, Docker build files and `.env.example` live under `software/`; real
`.env` files are ignored.

## Implementation progress

Ticket numbers start at 1 for Monitor and remain stable. Root summaries stay
short; implementation detail belongs in the relevant component README.
Work records use `agents/work/NNN-short-title/` and may reference roadmap tickets.

### Phase 1: Repository & development foundation

- [x] Ticket 1: Repository Bootstrap — structure, workflow and roadmap (Task 001).
- [x] Ticket 2: Development Docker Stack — four services with backend/frontend reload and placeholder health checks.
- [x] Ticket 3: Backend Baseline — FastAPI configuration, health endpoint and tests (Task 003).
- [x] Ticket 4: Database Baseline — raw SQL connectivity and migrations (Task 004).
- [x] Ticket 5: Authentication Baseline — development realm and API token validation (Task 005).
- [ ] Ticket 6: Frontend Baseline — minimal React shell connected to the API (after 3, 5).

### Phase 2: Meter reading data model

- [ ] Ticket 7: Device Model — unique device identity and ownership (after 4, 5).
- [ ] Ticket 8: Reading Model — timestamp, value/unit, confidence and optional image metadata (after 7).
- [ ] Ticket 9: Reading API — submit readings and retrieve latest/history (after 8).
- [ ] Ticket 10: Device Authentication — scoped credentials and ownership checks before real uploads (after 9).

### Phase 3: Camera & OCR PoC

Saved-photo recognition can proceed alongside the software foundation.

- [ ] Ticket 11: Camera Hardware Experiment — readable image of one real meter.
- [ ] Ticket 12: Capture Pipeline — reproducible crop/resolution and labelled PC photo fixtures (after 11).
- [ ] Ticket 13: OCR Baseline — simple digits first; compare PyTorch only if needed, assess device fit (after 12).
- [ ] Ticket 14: Balance Parser — extract a structured value with correct units/decimal point (after 13).
- [ ] Ticket 15: Confidence & Failure Handling — reject unclear readings and allow review/retry (after 14).
- [ ] Ticket 16: Device Upload — send a verified reading or approved image payload via REST (after 10, 15).

### Phase 4: User visibility

- [ ] Ticket 17: Current Balance — latest valid value, unit and timestamp (after 6, 9).
- [ ] Ticket 18: Reading History — history API and table (after 17).
- [ ] Ticket 19: Balance Trend — simple graph with gaps/invalid samples made clear (after 18).
- [ ] Ticket 20: Low-Balance Warning — threshold and capture-frequency requirements (after 17).
- [ ] Ticket 21: Device Status — last contact, stale readings and capture failures (after 16, 17).

### Phase 5: Hardware PoC

Placement and lighting experiments may run alongside Phase 3.

- [ ] Ticket 22: Camera Placement — test repeatable distance and angle (after 11).
- [ ] Ticket 23: Removable Mount — safe external attachment without meter modification (after 22).
- [ ] Ticket 24: Lighting Experiment — assess glare and controlled illumination (after 22).
- [ ] Ticket 25: Enclosure/CAD — simple mount/enclosure based on measured hardware (after 23, 24).
- [ ] Ticket 26: End-to-End Self-Test — camera through dashboard with failure cases (after 16, 21, 25).
- [ ] Ticket 27: Multi-Day Readings — record reliability on the real installation (after 26).

### Phase 6: Analytics / anomaly research

Only after enough real reading history exists; never an accusation of theft.

- [ ] Ticket 28: Consumption Estimate — handle units, top-ups, tariffs and missing readings (after 27).
- [ ] Ticket 29: Usage Baseline — learn normal patterns from consented history (after 28).
- [ ] Ticket 30: Rule-Based Signals — flag unusual changes with uncertainty (after 29).
- [ ] Ticket 31: ML Experiment — only if data and rule-based results justify it (after 30).
- [ ] Ticket 32: Anomaly View — explain investigation flags, not verdicts (after 30).

### Phase 7: Beta validation

Basic reading beta need not wait for optional analytics research.

- [ ] Ticket 33: Self-Use Review — accuracy, usefulness and go/no-go from real readings (after 27).
- [ ] Ticket 34: Second Meter — explicitly test compatibility beyond the first display (after 33).
- [ ] Ticket 35: Controlled Beta — consent, secure access, installation limits and tester group (after 34).
- [ ] Ticket 36: Reliability Review — collect feedback before expanding scope (after 35).

### Phase 8: Future meter integration

Beyond the initial PoC; no implementation now.

- [ ] Ticket 37: MQTT Evaluation — only if measured use reveals a REST limitation.
- [ ] Ticket 38: Interface Survey — document supported interfaces and relevant meter models.
- [ ] Ticket 39: Optical/IR Research — supported interfaces only, without meter interference (after 38).
- [ ] Ticket 40: Top-Up Research — validate user need and authorised payment/vending options.
- [ ] Ticket 41: Supported Top-Up Prototype — only with documented integration, consent and failure handling (after 39, 40).

## Documentation

- [Agent workflow](AGENTS.md), [context](agents/context.md), [engineering rules](agents/rules.md).
- [Hardware](hardware/README.md), [software](software/README.md), [OCR](software/ocr/README.md).
- [Task 001](agents/work/001-repository-bootstrap/changes.md), [PR template](.github/pull_request_template.md).

## License

Proprietary - Roventics Pty Ltd
