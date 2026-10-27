# DATA READINESS SPLIT

IS_DOCUMENTARY_SOURCE_READINESS_BLOCKING=FALSE_FOR_SELECTED_FIRST_SCIENTIFIC_WITNESS
IS_QUANT_DATA_READINESS_BLOCKING=TRUE
IS_EXECUTION_COST_DATA_READINESS_BLOCKING=FALSE_FOR_FIRST_BOUNDED_SCIENCE; TRUE_BEFORE_ECONOMIC_VALIDATION
IS_ECONOMIC_DATA_READINESS_BLOCKING=FALSE_FOR_FIRST_BOUNDED_SCIENCE; TRUE_BEFORE_ECONOMIC_VALIDATION

## Documentary source

Repository facts show a real documentary-source shadow and separately qualified source binding/planning capability. This is sufficient to reject a generic claim that documentary sourcing is the current universal blocker. It does not imply readiness for market microstructure, execution or portfolio data.

## Quant data — selected witness

NAMED_EXPERIMENT=`disc-crypto-book-pressure-prospective-l1-v0`

VARIABLE=BitMEX XBTUSD best bid/ask price and size, source timestamp and local capture timestamp; derived book-pressure signal and subsequent frozen-horizon price response only as specified by the frozen protocol.

PIT=prospective observations; declared staleness <=10 seconds, future skew <=1 second, strictly increasing timestamps; no retrospective substitution.

FREQUENCY=21 prospective snapshots, approximately 5-second cadence, bounded run <=120 seconds, as frozen.

UNIVERSE=XBTUSD only for this witness.

PROVENANCE=retain raw payload/receipt, endpoint/source identity, request/capture timestamps, invalid flags, payload/raw hashes, protocol hash and execution code/environment identity.

CURRENT_GAP=the recovered capture returned HTTP success but lacked the required valid BBO fields; zero valid trades/observations were admitted and the correct disposition was `PARK_DATA/CAPTURE_INVALID`. A future valid capture satisfying the exact frozen contract is required. Do not silently switch exchange, symbol, horizon or feature and call it the same trial.

RECOMMENDED_DATA_ACTION=repair or replace only the exact acquisition/parsing boundary necessary to produce the already-declared BBO variables, and only if the resulting source semantics remain equivalent to the frozen protocol. If equivalence cannot be proven, declare a new experiment instead of mutating this one.

## Execution-cost data

NAMED_EXPERIMENT=`disc-crypto-book-pressure-prospective-l1-v0`

VARIABLE=frozen screening transaction-cost assumptions: spread crossing plus declared fee and extra-slippage assumptions; later, if economic validation is authorized, realized/representative spread, fees, depth, latency, market impact and funding where applicable.

PIT=cost assumptions are frozen before the first bounded scientific run; later empirical calibration must use data observable under its separately declared evaluation window.

FREQUENCY=per contemplated trade/event for later economic validation; no additional high-frequency cost feed is required to decide whether the frozen first-stage scientific relation is observed under its stated cost screen.

UNIVERSE=XBTUSD and the exact venue/source used by the selected witness.

PROVENANCE=fee schedule/version, spread/depth observations, timestamped venue source and any fill/latency evidence used later.

CURRENT_GAP=real execution-cost calibration is not demonstrated. This is not a blocker to the first bounded scientific result because the screening assumptions are already explicit and frozen; it becomes a blocker before claiming after-cost implementability.

## Economic data

NAMED_EXPERIMENT=`disc-crypto-book-pressure-prospective-l1-v0` downstream economic validation, only after a scientific result exists and a separate gate authorizes it.

VARIABLE=after-cost returns, capacity/depth, factor/beta exposures, benchmark contribution, correlation/incremental portfolio value and uncertainty.

PIT=separately frozen OOS/prospective evaluation window; no reuse of protected outcome data to tune the original rule.

FREQUENCY=defined by the later economic-validation protocol, not invented in this Pass B.

UNIVERSE=selected witness plus a separately declared benchmark/portfolio universe.

PROVENANCE=market/source receipts, exact strategy expression, holdings/exposure identity, cost model version, benchmark version and portfolio-evaluation code SHA.

CURRENT_GAP=no current repository evidence proves these data and joins are ready for a real economic validation of the selected witness. This blocks economic validation/capital claims, not the first scientific result.

## Explicit rejection

GENERIC_DATA_PLATFORM_MISSION=DO_NOT_BUILD_YET

The observed gap is experiment-specific. New generic infrastructure is unauthorized unless a named experiment demonstrates a reusable missing function that cannot be satisfied by existing source/data contracts.
