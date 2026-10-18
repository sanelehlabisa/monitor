# Task 051: Forecast research workspace

## Result

Created software/backend/research/forecasting/ with separate generate.py and
plot.py scripts, explicitly invoked checks.py, research-only requirements,
READMEs and ignored output/environment directories. Preserved Task 050 changes.

- 227 Python implementation lines (121 generator + 106 plotting), plus four
  configuration lines: 231 within the approved 250-line exception. Tests,
  documentation and generated files are excluded from that count.
- Four fictional profiles with stable per-meter IDs: steady low/high, changing
  and weekly. Default seed 42, fixed UTC start and 90-day duration; daily,
  weekly and irregular sampling produce 12 observed datasets. Four separate
  hourly truth files and a manifest record rates, sampling and exact arithmetic.
- Plotting derives top-up-adjusted consumption only from observed records.
  PNG panels distinguish observations, inferred segments, purchase events and
  optional synthetic evaluation truth. Invalid records raise rather than clip.
- Matplotlib 3.11.2 is installed only in the research .venv, with its requirement
  separate from backend dependencies. Agg writes images without GUI windows;
  figures close after saving. No application import or DB connection is needed.
- Outputs remain under ignored forecasting/out/. Research is excluded from
  backend Docker build context; checks.py does not match backend test filenames.
- Updated root/backend/software/research READMEs and context. Tickets 66.1/66.2
  remain open: this is the initial generation/visualisation slice, not full
  acceptance. Further edge fixtures, candidate/backtests and app adoption remain
  separately approved work. Next work number 052. No commit or push.

## Reuse

Ticket 66 ledger contracts, UTC and (previous, current] purchase boundaries;
Python standard library for deterministic data/checks; approved Matplotlib for
images only. No copied live forecasting algorithm or new app dependency.

## Verification

- PASS: all 12 isolated unittest checks in the research environment (13.025s),
  covering repeated/serialized data, seed/cadence/meter isolation, UTC and sparse
  observation separation, every observed/hourly interval's energy conservation,
  exact steady rates, hand-calculated usage, boundary/timezone equivalence,
  invalid energy/time rejection, valid PNG output and figure cleanup.
- PASS: default generate.py and plot.py workflow: 12 observations, four truth
  files, manifest and 12 PNGs. All default PNGs decode. Changing/irregular and
  30-day high/weekly examples were visually inspected; labels remain legible.
- PASS: 30-day high-use example: 450 initial + 300 purchased - 300 remaining =
  450 consumed. Independent 30-day CLI generation also passed.
- PASS: extra wrong-meter truth, reversed observations and NaN rejection checks;
  no output created by rejected truth. Independent source/docs review found no
  blockers. Research dependencies pass pip check; global Matplotlib remains
  3.11.1 while research uses 3.11.2.
- PASS: output/.venv Git exclusions, 250-line limit, explicit check-file naming,
  research Docker-context exclusion and git diff --check. Runtime requirements,
  Dockerfile, app/frontend/database sources and service config are unchanged.
- UNAVAILABLE: backend pytest --collect-only attempt could not connect to Docker
  Desktop's Linux engine. No collection or backend build is claimed; static
  naming/configuration checks passed. No restart, fixtures or DB access attempted.
- The isolated venv and generated data/PNGs are intentionally retained locally,
  ignored and reproducible. Small agent audit/preview outputs are also ignored.

## Boundaries

No forecasting candidate, accuracy backtest, live default policy, app/API/UI/DB,
real/demo data, ML/hardware/OCR, deployment or sibling changes. All future model
integration still requires Ticket 66.5 evidence and fresh approval. No Git writes.
