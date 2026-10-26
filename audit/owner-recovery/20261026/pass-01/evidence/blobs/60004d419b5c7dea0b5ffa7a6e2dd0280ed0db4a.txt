# Polymarket standard negative-risk parity — read-only screen execution evidence

DATE = 2026-10-08
MISSION = EXECUTE_FROZEN_MINIMUM_DISCRIMINATING_READ_ONLY_SCREEN
STARTING_REMOTE_HEAD = 45a431ec0c25abb70a6ee7e6409ab813d8635efc
PINNED_IMPLEMENTATION_SHA = 45a431ec0c25abb70a6ee7e6409ab813d8635efc
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
WALLET_USED = FALSE
ORDERS_USED = FALSE
CONVERSION_USED = FALSE
SETTLEMENT_OUTCOMES_USED = FALSE

## Execution provenance

The screen ran on GitHub Actions because the local execution environment had no outbound DNS. The workflow checked out the implementation at the exact pinned SHA above, verified `git rev-parse HEAD`, and ran the frozen synthetic suite before any screen acquisition. Synthetic result: 11/11 PASS.

Primary successful workflow run:
- RUN_ID = 37815709390
- JOB_ID = 113443683769
- WORKFLOW_TRIGGER_SHA = f744564c67202b948e841d5080b689e010f58802
- ARTIFACT_ID = 11567427660
- ARTIFACT_NAME = polymarket-neg-risk-readonly-screen
- ARTIFACT_DIGEST = sha256:af451db7145d31b99890791d98fa401ec0bf1dc4fa0d271784151a058b9ec38f

A prior orchestration attempt, run 37815485577, failed before the first network request because the runner used an `importlib` loading pattern incompatible with Python `dataclass`. The pinned implementation and its 11 tests had already passed. That attempt observed no Gamma or CLOB data and therefore could not influence event selection, thresholds, or arithmetic. The second run changed only the module-loading mechanism, not the collector or research rules.

## Frozen design actually executed

- standard negative-risk only;
- `enableNegRisk == true`;
- `negRiskAugmented == false` explicitly;
- exactly 3 component markets;
- all components active, order-enabled, binary YES/NO and `negRisk == true`;
- unique condition/token IDs;
- completeness re-fetch before sampling;
- deterministic ascending event-ID selection;
- maximum 10 events;
- 60 rounds at 10-second spacing;
- batch `POST /books` per event;
- executable depth only; no midpoint, last trade, or Gamma probability in arithmetic;
- route: BUY executable `NO_i` -> conceptual negative-risk conversion -> SELL executable `YES_j` for all `j != i`;
- threshold unchanged: `max(0.10 pUSD, 10 bp * total traded gross notional)`;
- max cross-book timestamp skew unchanged: 1,000 ms.

## Preflight and universe

PREFLIGHT_ENDPOINTS = PASS
PINNED_CODE_VERIFICATION = PASS
SYNTHETIC_TESTS = 11/11 PASS

Gamma preflight raw-response SHA-256:
`dbdbafc7833d2fc2c1843967a6f43b49daa4e788a0b73025e310e0f9cda466b6`

Gamma discovery canonical-payload SHA-256:
`77b218d6b6d02f5cbf6a80f1e6dedbe379ab80af07882423698ed72115b5a9ae`

CLOB `/books` preflight raw-response SHA-256 (event 106981):
`10335b2150c6efb2cea287d8f4e9b1f7ade25ac75310de87d42c4dbbc146d4fb`

EVENTS_ELIGIBLE = 28
EVENTS_SAMPLED = 10

Selected deterministically:
`106981, 233140, 237722, 250181, 250182, 250183, 256576, 256577, 256578, 259108`

## Artifact integrity

`manifest.json`:
- bytes = 1639
- SHA256 = `388686b2c34527ad50a94104ed60137f12b2b49343a753b96d77f3e920031811`

`summary.json`:
- bytes = 604
- SHA256 = `2f0a17719390574196bb99e732f76a94cf837b0ff97bf3e23ffe6baa4800868e`

`snapshot_audit.jsonl`:
- bytes = 1341782
- SHA256 = `98662a914b4d2866efe0723f2306783c9b3fcec0ba26a6860572082ca858ed9a`

Raw network bodies were not committed to Git. The audit retains request UTC times, token IDs, per-book timestamps/hashes, raw-response SHA-256 values, fee schedules, skew, validity and route evaluations.

## Screen result before data-contract adjudication

SNAPSHOTS_REQUESTED = 60 rounds
EVENT_SNAPSHOT_ATTEMPTS = 600
VALID_EVENT_SNAPSHOTS = 60
INVALID_EVENT_SNAPSHOTS = 540
FULLY_VALID_ROUNDS = 0
ROUTES_EVALUATED = 0
THRESHOLD_EXCEEDANCES = 0
PERSISTENT_ROUTES = 0

All 540 invalid event snapshots failed the frozen `max timestamp skew <= 1,000 ms` rule. Only event 256577 had zero reported cross-token skew in all 60 rounds; its executable-depth evaluation returned zero complete routes.

Observed per-event book timestamp skew in milliseconds (`min / median / max` across 60 rounds):
- 106981: `61,401 / 120,762 / 173,992`
- 233140: `91,323 / 437,871 / 1,092,538`
- 237722: `26,867 / 26,867 / 26,867`
- 250181: `67,072 / 67,072 / 67,072`
- 250182: `40,516 / 40,516 / 40,516`
- 250183: `34,644 / 34,644 / 34,644`
- 256576: `2,399,655,452 / 2,399,655,452 / 2,399,655,452`
- 256577: `0 / 0 / 0`
- 256578: `39,094 / 39,094 / 39,094`
- 259108: `57,716 / 57,716 / 57,716`

The large skews frequently remained exactly unchanged across repeated batch requests. For example, event 256576 contained token-book timestamps separated by about 2.400 billion ms while the six books were returned in one `/books` request. This is incompatible with the frozen assumption that the per-book `timestamp` field is a request-synchronous capture timestamp suitable for a <=1 second cross-leg simultaneity gate. Whether the field represents last mutation time, cached book state time, or another per-book clock does not need to be guessed: empirically it cannot support the frozen synchrony test as specified.

## Data-contract adjudication

DATA_CONTRACT_BLOCKER = TRUE

MATERIAL_DIFFERENCE = The actual CLOB batch response supplies per-book timestamps whose cross-token values are not synchronized to the batch request and can differ by tens of seconds through weeks. The frozen screen treated those timestamps as evidence of simultaneous quote capture. That assumption is materially false/unsupported in production data.

Per mission rule, the economic test stops here. The observed `0 routes evaluated / 0 threshold exceedances` is **not** a clean falsification and must not be converted into `KILL`; almost the entire intended sample was rejected by a broken synchrony assumption before basket arithmetic could be evaluated.

STRUCTURAL_VIOLATION = FALSE_NOT_EVALUABLE_UNDER_FROZEN_DATA_CONTRACT
DECISION = KEEP_AS_RESERVE

PROMOTE is forbidden because the frozen structural-violation criterion was not satisfied. KILL is also not supported because zero routes were evaluated. The candidate remains reserve-only until the timestamp/synchrony contract is independently resolved and a new screen is preregistered before further book observation.

## Requested economic output

EVENT_ID = NONE_EVALUABLE
SOURCE_MARKET = NONE_EVALUABLE
Q = N/A
BUY_COST = N/A
SELL_PROCEEDS = N/A
TAKER_FEES = N/A
NET_GAP = N/A
NET_GAP_BPS = N/A
DEPTH = NO_COMPLETE_ROUTE_EVALUATED_UNDER_VALID_FROZEN_SNAPSHOT
TIMESTAMP_SKEW = DATA_CONTRACT_BLOCKER; 9/10 sampled events exceeded 1,000 ms in all 60 rounds
PERSISTENCE_COUNT = 0

EVENTS_ELIGIBLE = 28
EVENTS_SAMPLED = 10
SNAPSHOTS_REQUESTED = 60
SNAPSHOTS_VALID = 0 fully-valid 10-event rounds; 60/600 individual event snapshots passed skew
ROUTES_EVALUATED = 0
THRESHOLD_EXCEEDANCES = 0
PERSISTENT_ROUTES = 0

BLOCKER = CLOB per-book timestamp semantics are incompatible with the frozen <=1s cross-leg synchrony gate; therefore executable negative-risk parity was not economically tested.
NEXT_ACTION = Resolve a production-supported synchrony primitive/semantics, then preregister a replacement read-only screen before observing additional books. Do not reinterpret the present books with a relaxed skew or alternative clock post hoc.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
