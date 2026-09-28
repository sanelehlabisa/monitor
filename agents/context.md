# Repository Context

Roventics Monitor is a separate, non-invasive meter-reading product, not a
Switch firmware extension. Its starting research was moved from Switch's
`meter.README.md` into this repository's main `README.md`.

## Scope

Read one accessible prepaid meter display with an external camera. Extract
balance/value and synchronise it to a web application over HTTP/REST.
Prove useful readings before generalising. Never open, modify electrically,
bypass or interfere with the meter. Safe removable installation is a goal,
not an assurance that every installation is suitable for an untrained user.

## Planned areas

- `hardware/firmware/`: ESP32-class C/C++ camera firmware; board selection pending.
- `hardware/camera/`: image capture, positioning and lighting.
- `hardware/mechanical/`: external mounts/enclosures and grouped print outputs.
- `hardware/experiments/`: measured hardware feasibility and test notes.
- `software/ocr/`: PC photo tests and simple Python recognition; PyTorch if needed.
- `software/backend/`: FastAPI REST service and the preferred initial OCR runtime; no MQTT for V1.
- `software/database/`: PostgreSQL with explicit, versioned SQL migrations through Psycopg.
- `software/frontend/`: React and Material UI application.

Task 002 originally added a four-service development stack. After the Task 007
authentication pivot, only PostgreSQL, backend and frontend remain under
`software/` in `dev.docker-compose.yaml`. Real environment files/secrets must
not be committed.
Task 003 adds the FastAPI application factory, `MONITOR_` settings and a
process-only health contract; database and authentication checks remain later work.
Task 004 uses direct Psycopg connections and versioned SQL without an ORM. For
fast initial iteration, OCR may run in the backend before device fit is evaluated.
Tasks 005-006 are retained as historical records of the superseded Keycloak
baseline. Task 007 removes that active integration and keeps the Material UI
shell as an honest placeholder. Planned human authentication uses authorised
email addresses, short-lived hashed one-time codes and secure HTTP-only cookie
sessions. Device authentication stays separate: each device has a UUID and
revocable credential, with many-to-many user/device access. Development CORS
permits only the configured UI origin.
First-time device setup is planned through a temporary local access point using
an owner email, but firmware and provisioning security are not implemented yet.
No `docs/` directory: use the nearest README. No production/cloud deployment
or infrastructure without an approved ticket.

## OCR and evidence

Start from saved real-meter photos, with reproducible crops and labelled
expected values. PC tests are not ESP32 hardware emulation or proof of RAM,
camera behaviour, timing or deployment compatibility. Long inference is
acceptable experimentally, but model fit and accuracy still need measurement.
Prefer simple digit recognition before training a model. Keep on-device and
server OCR as evaluated choices, not claims of completed support.

Choose capture frequency separately from monthly reporting; alerts and
consumption estimates need sufficient samples. Never silently accept uncertain
OCR as a real reading. Retain only consented data with explicit access and
retention rules; no private bills, account numbers or images in Git.

## Later work

No anomaly ML until real history exists and simpler rules justify it.
Anomalies are investigation signals, not proof of theft. Top-ups, prepaid or
postpaid payment facilitation and municipal analytics remain future research;
use authorised documented interfaces only. No electrical meter interference.

Root README holds short phased tickets. Detailed READMEs hold implementation
context. Agent work records use sequential three-digit directories. Reuse the
Switch workflow, not its application code or obsolete cloud architecture.
