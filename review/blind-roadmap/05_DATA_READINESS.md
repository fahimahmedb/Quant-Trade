# DATA / SOURCE READINESS — DECOMPOSED

Generic SOURCE_READY/DATA_READY is forbidden. Readiness is experiment-specific.

## DOCUMENTARY_SOURCE_READINESS

Research OS contains documentary source records, a frontier source planner, source bindings and V2 worker verification of source path/blob/record/packet identity. The 0691 lineage's exact hosted checks passed after making qualification explicit rather than default-true. This supports a documentary-source binding capability, not universal source readiness.

For the first scientific witness selected below, documentary research context is secondary to market observations; no generic documentary platform is required.

## QUANT_DATA_READINESS

### Witness: `disc-crypto-book-pressure-prospective-l1-v0`

- NAMED_EXPERIMENT: `disc-crypto-book-pressure-prospective-l1-v0`
- VARIABLE_OR_OBSERVATION_REQUIRED: BitMEX XBTUSD top-of-book bid/ask prices and bid/ask sizes; source timestamp plus local send/receive UTC/monotonic timestamps.
- PIT_REQUIREMENT: each scheduled quote observed prospectively; quote <=10s stale and <=1s future relative to receipt; source timestamps strictly increase within declared interval rules.
- FREQUENCY: 21 scheduled snapshots at 5-second intervals; <=120s acquisition.
- UNIVERSE: XBTUSD on BitMEX for this exact witness.
- PROVENANCE_REQUIREMENT: retain every raw response/invalidity flag plus source/local timestamps and immutable experiment declaration identity.
- CURRENT_MISSING_CAPABILITY: valid BBO payload capture satisfying the frozen schema. Recorded capture had 21 HTTP 200 responses but missing required BBO fields, zero valid trades and `PARK_DATA/CAPTURE_INVALID`.
- READINESS: NOT_READY_FOR_RESULT; protocol is substantially specified, data capture is not valid.

### Witness: `disc-binance-extreme-funding-reversal-l1-v1`

- VARIABLE_OR_OBSERVATION_REQUIRED: BTCUSDT/ETHUSDT funding-rate history and 5m price klines.
- PIT_REQUIREMENT: frozen 2021-01-01 through 2025-12-31 data endpoints; provenance to official endpoints.
- FREQUENCY: funding events / 5m prices; horizon 8h.
- UNIVERSE: BTCUSDT, ETHUSDT.
- PROVENANCE_REQUIREMENT: exact official API retrieval bound to frozen endpoints.
- CURRENT_MISSING_CAPABILITY: source access; recorded execution failed HTTP 451.
- READINESS: PARK_DATA.

### CFE VIX historical lineages

Official CBOE CSV acquisition receipts with SHA256 hashes and QA exist in the v2-reader result. This demonstrates historical quant-data acquisition for that experiment family, but its reuse/history makes it less suitable as the first low-contamination prospective witness.

## EXECUTION_COST_DATA_READINESS

For `disc-crypto-book-pressure-prospective-l1-v0`, the protocol already freezes an explicit screen: observed spread crossing plus 5bp per side fee and 1bp total extra slippage centrally; stress 10bp/side +1bp. These are assumptions, not verified account-specific fee/fill data. Thus:

- scientific screening cost model: READY_AS_DECLARED_ASSUMPTION;
- real execution-cost calibration: NOT_READY / NOT_REQUIRED for the first bounded scientific screen;
- any economic/live claim would require stronger fill/latency/depth/funding evidence.

For the Binance funding witness, frozen round-trip cost is 0.001; source failure prevents reaching economic computation.

## ECONOMIC_DATA_READINESS

Economic Identity / Portfolio Readiness capabilities exist in the architecture, but the audited first-witness evidence does not contain a real qualified scientific result transported into payer/instrument/capacity/portfolio/lifecycle state. Therefore ECONOMIC_DATA_READINESS=NOT_DEMONSTRATED_FOR_FIRST_REAL_MILESTONE.

Do not build a generic data platform. Resolve only the named observation/provenance gap required by the selected experiment, then stop if the source remains invalid or unavailable.
