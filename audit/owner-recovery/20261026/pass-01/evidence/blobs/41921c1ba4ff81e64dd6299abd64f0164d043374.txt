# Polymarket standard negative-risk — frozen read-only screen result

DATE = 2026-10-08
BRANCH = sol/scout-prediction-flb-nr
PINNED_IMPLEMENTATION_SHA = 45a431ec0c25abb70a6ee7e6409ab813d8635efc
WORKFLOW_RUN_ID = 37815709390
WORKFLOW_ARTIFACT_ID = 11567427660
WORKFLOW_ARTIFACT_DIGEST = sha256:af451db7145d31b99890791d98fa401ec0bf1dc4fa0d271784151a058b9ec38f

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
WALLET_USED = FALSE
ORDERS_USED = FALSE
CONVERSION_USED = FALSE
SETTLEMENT_OUTCOMES_USED = FALSE

## Preflight

PREFLIGHT = PASS

The GitHub Actions runner checked out exactly `45a431ec0c25abb70a6ee7e6409ab813d8635efc`, verified the exact HEAD, and ran the frozen synthetic suite before the live read-only screen. The suite passed 11/11. The first orchestration attempt failed before any network read because of a Python dynamic-import/dataclass loader error; the orchestration loader alone was corrected and the second run executed the same pinned collector. No threshold, universe rule, route arithmetic or collector code was changed after book observation.

Public Gamma discovery and CLOB `/books` preflight both passed. `DATA_CONTRACT_BLOCKER = FALSE`.

## Frozen universe and sampling

UNIVERSE_RULE = standard neg-risk; `enableNegRisk=true`; `negRiskAugmented=false` explicitly; exactly 3 component markets; all components live/order-enabled/negRisk; unique condition/token IDs; completeness refetch; deterministic event-ID ordering; max 10 events.

EVENTS_ELIGIBLE = 28
EVENTS_SAMPLED = 10
SELECTED_EVENT_IDS = 106981, 233140, 237722, 250181, 250182, 250183, 256576, 256577, 256578, 259108
SNAPSHOTS_REQUESTED = 60
INTERVAL_SECONDS = 10

## Observation quality

VALID_EVENT_SNAPSHOTS = 60
INVALID_EVENT_SNAPSHOTS_TIMESTAMP_SKEW_GT_1000MS = 540
FULLY_VALID_SNAPSHOT_ROUNDS = 0

All 60 valid event-snapshots belonged to event `256577`, for which all six relevant token-book timestamps were synchronous under the frozen <=1000 ms rule. The other nine sampled events were rejected on every round because their returned cross-token book timestamps exceeded the frozen 1-second skew cap.

## Executable-route result

ROUTES_EVALUATED = 0
THRESHOLD_EXCEEDANCES = 0
PERSISTENT_ROUTES = 0
EVENTS_WITH_EXCEEDANCE = NONE
BEST_ROUTE = NONE
BEST_NET_GAP = NONE
BEST_NET_GAP_BPS = NONE

The pinned route evaluator only emits a route when the common minimum share quantity can be filled on the source `NO_i` ask and on every required destination `YES_j` bid using displayed depth. On the sole event with valid synchronized snapshots, no route met that executable-depth condition in any of the 60 observations. No midpoint, last trade, Gamma probability or settlement result entered the arithmetic.

The frozen structural-violation rule was therefore not satisfied: neither the same route exceeded the fixed threshold in >=3 non-adjacent snapshots nor did exceedances occur in >=2 distinct events.

STRUCTURAL_VIOLATION = FALSE
PRIMARY_STATE = NO_MATERIAL_QUOTE_SPACE_VIOLATION_IN_SCREEN
DECISION = KILL

Interpretation: under the exact frozen screen, there was no executable quote-space evidence supporting promotion. The absence of sufficient synchronized executable depth is itself adverse economic evidence for this proposed route at the frozen minimum-size rule. No second opportunistic test is authorized by this result.

## Audit hashes

MANIFEST_SHA256 = 388686b2c34527ad50a94104ed60137f12b2b49343a753b96d77f3e920031811
SUMMARY_SHA256 = 2f0a17719390574196bb99e732f76a94cf837b0ff97bf3e23ffe6baa4800868e
SNAPSHOT_AUDIT_JSONL_SHA256 = 98662a914b4d2866efe0723f2306783c9b3fcec0ba26a6860572082ca858ed9a

NEXT_ACTION = STOP_THIS_NEGATIVE_RISK_ROUTE_AND_RETURN_EDGE_SEARCH_CAPACITY_TO_OTHER_CAUSALLY_DISTINCT_FAMILIES

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
