# Polymarket standard negative-risk — scientifically valid corrected-measurement rerun

DATE = 2026-10-08
BRANCH = sol/scout-prediction-flb-nr
SOURCE_RUN_ID = 37815709390
RERUN_ID = 37818642950
RERUN_STATUS = SUCCESS
RERUN_ARTIFACT_ID = 11567974518
RERUN_ARTIFACT = polymarket-neg-risk-readonly-screen-v2
RERUN_ARTIFACT_DIGEST = sha256:d9c602ae64aceef00995123fe615434075f99d386f8b7b6cfd31f28190eec164

PRIOR_KILL_VERDICT = INVALIDATED_BY_DATA_QUALITY_GATE
TIMESTAMP_ROOT_CAUSE = API_TIMESTAMP_SEMANTICS_MISUNDERSTOOD
SAME_FROZEN_TEST_REEXECUTABLE = TRUE
ECONOMIC_SPEC_CHANGED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Root cause and measurement correction

The source screen used the difference among per-book CLOB `timestamp` fields as if it measured simultaneity of the batch HTTP acquisition. Source-artifact analysis showed those timestamps behave as book snapshot/state-version times: on the two books that changed during the source run, every timestamp transition matched a hash transition exactly; static books retained both timestamp and hash over repeated later reads.

The sole old-valid event `256577` had six identical timestamps only because all six returned book states shared the same state timestamp. Their common value was 2026-09-10T10:02:48.908Z, about 28.3 days before the source acquisition, proving that zero cross-book timestamp difference did not identify uniquely synchronous HTTP capture.

The correction is measurement-only. The numeric synchrony bound remains exactly 1,000 ms, but it is applied to the monotonic request/response span of the single `POST /books` batch call. Per-book timestamps/hashes remain recorded as state provenance and are not subtracted to infer acquisition simultaneity. Server-side atomicity is not asserted.

The frozen economic collector stayed byte-identical: Git blob `faffb23fc0c0fce0ad498b05681e2608d0f5b347`. Regression tests proved corrected route arithmetic equals the frozen evaluator whenever the old timestamp gate is satisfiable.

## Exact-entrypoint and runtime gates

RUNTIME_GATE = PASS
EXACT_ENTRYPOINT_SMOKE = PASS

- original 11 synthetic collector tests: PASS;
- 4 measurement/regression tests: PASS;
- total tests: 15/15 PASS;
- forced entrypoint failure emitted a persistent diagnostic as required;
- real entrypoint smoke passed against Gamma + CLOB;
- final artifact upload succeeded after the full run.

## Frozen design preserved

Unchanged:
- standard negative-risk only;
- `enableNegRisk=true`;
- `negRiskAugmented=false` explicitly;
- exactly 3 component markets;
- live/order-enabled/neg-risk components;
- unique IDs/tokens and completeness refetch;
- deterministic event-ID selection;
- maximum 10 events;
- the exact source selected IDs were required to match before rerun;
- 60 snapshots;
- 10-second interval;
- one batch `/books` request per event-snapshot;
- executable depth only;
- route `BUY NO_i -> conceptual neg-risk conversion -> SELL YES_j for all j != i`;
- identical common-q rule and fee arithmetic;
- threshold `max(0.10 pUSD, 10 bp * gross traded notional)`;
- persistence rule: same route >=3 non-adjacent snapshots OR exceedance in >=2 distinct events.

## Data-quality gate

DATA_QUALITY_GATE = PASS

EVENTS_ELIGIBLE = 28
EVENTS_SAMPLED = 10
SNAPSHOTS_REQUESTED = 60
SNAPSHOT_ROUNDS_VALID = 60
VALID_EVENT_SNAPSHOTS = 600 / 600
INVALID_EVENT_SNAPSHOTS = 0
DATA_CONTRACT_ERROR = NONE

Batch acquisition span over 600 event-snapshots:
- min = 173.100267 ms
- median = 194.120470 ms
- p95 = 234.951669 ms
- max = 713.119029 ms

Every event-snapshot therefore satisfied the unchanged 1,000 ms numeric acquisition bound under the corrected observable.

## Scientific execution gate

SCIENTIFIC_EXECUTION_GATE = PASS
PRIMARY_STATISTIC_COMPUTABLE = TRUE
ROUTES_EVALUATED = 1260
DISTINCT_ROUTE_KEYS = 21
EVENTS_WITH_EXECUTABLE_ROUTES = 7 / 10
EVENT_SNAPSHOTS_WITH_EXECUTABLE_ROUTE = 420

Three sampled events had no complete executable route at the frozen common-q/depth rule; this is a normal route-unavailability outcome, not a data-quality invalidation. The other seven events produced all three source-market routes on all 60 rounds.

## Frozen economic result

THRESHOLD_EXCEEDANCES = 0
PERSISTENT_ROUTES = 0
EVENTS_WITH_EXCEEDANCE = NONE
STRUCTURAL_VIOLATION = FALSE

Best observed route by net gap was still negative:
- EVENT_ID = 106981
- SOURCE_MARKET = 950852
- Q = 5
- BUY_COST = 4.0
- SELL_PROCEEDS = 3.70
- TAKER_FEES = 0.09608
- NET_GAP = -0.39608 pUSD
- NET_GAP_BPS = -514.3896103896103896103896104
- THRESHOLD = 0.10 pUSD
- PERSISTENCE_COUNT = 0

Because the corrected screen materially executed the frozen primary statistic across 1,260 executable routes and produced zero threshold exceedances, the economic verdict is now admissible.

ECONOMIC_VERDICT = KILL
TERMINAL_STATE = VALID_ECONOMIC_VERDICT

This KILL is a new, scientifically valid verdict from rerun `37818642950`. It does not reinstate the invalid source-run KILL; the source verdict remains explicitly invalidated by its data-quality gate.

## Audit integrity

RERUN_MANIFEST_SHA256 = 19ea37a1a005a15eb2913d241589e0ad89331b6a1a91c33efb00c5f8ebaef0f8
RERUN_PREFLIGHT_SHA256 = a2599db4aa51db672ad9bc41fe80c1d2744fd1ff242772073139014d7d5a21ad
RERUN_SUMMARY_SHA256 = 296863e37b421572bb944bcde7affc68e1e8981c969778e20d4b4773cdb57286
RERUN_SNAPSHOT_AUDIT_SHA256 = ba6ea2efa7c37223deeb71695910a23299176636303c62eb6db68210895c9bbf

No raw network response bodies are committed to Git. The workflow artifact retains compact audit records and raw-response SHA-256 values.

HUMAN_INTERVENTION_REQUIRED = FALSE
NEXT_SINGLE_ACTION = ARCHIVE_THIS_NEGATIVE_RISK_ROUTE_AS_KILLED; DO_NOT_PROMOTE_TO_CONVERSION_COST_LATENCY_VALIDATION

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
