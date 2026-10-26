# AGENT 1 — CRYPTO MECHANISM SCOUT

See branch history for the original one-shot scout and intermediate second-pass notes.

FINAL SECOND-PASS STATUS (2026-10-08):
- Hyperliquid forced-liquidation classification is deterministic from market-wide node fills carrying `liquidation.method`, with canonical execution collapse by `(block_number, coin, tid)`.
- Point-in-time availability is enforced with node `local_time` and local WS receive timestamps; no post-t0 quote may be used.
- Completeness is conditional on a fail-closed sequential block-gap audit and valid contemporaneous BBO capture.
- The single BTC/ETH 5-second-bucket / 30-second-horizon test is frozen in `research/edge_search/scouts/hl_liquidation_v1/HL_LIQUIDATION_V1_FROZEN_SPEC_2026-10-08.md`.
- Recorder/parser/replay harness plus synthetic tests are persisted under `research/edge_search/scouts/hl_liquidation_v1/`.
- Exact published harness blob was locally exercised: 11 unit tests PASS and Python compilation PASS.
- No F1 Stage A/B outcome was opened, downloaded, computed or modified. No candidate return outcome was consumed.

CANDIDATE_1_STATUS = MEASUREMENT_BLOCKER_RESOLVED
TEST_FROZEN = TRUE
HARNESS_BUILT = TRUE
SYNTHETIC_TESTS = 11_PASS
READY_TO_RECORD = TRUE_ON_COMPLIANT_NODE_HOST
READY_TO_EXECUTE = FALSE_IN_CURRENT_ENVIRONMENT
BLOCKER = COMPLIANT_HYPERLIQUID_NON_VALIDATING_NODE_HOST_ONLY
NEXT_ACTION = provision/reuse a compliant mainnet non-validating-node host; launch `--write-fills --batch-by-block --disable-output-file-buffering` plus the frozen public-WS recorder; accumulate prospective BTC/ETH data; run the frozen harness only after its minimum sample gate.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
