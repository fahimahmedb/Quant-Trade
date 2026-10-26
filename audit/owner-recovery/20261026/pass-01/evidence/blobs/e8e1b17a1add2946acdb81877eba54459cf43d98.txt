# BLUE P0 RAW CAPTURE CHECKPOINT ADDENDUM — 2026-09-18

**Status:** CURRENT STRATEGIC CHECKPOINT ADDENDUM  
**Authority:** Blue Team / Mission Control  
**Parent:** `P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md`

This addendum controls the acquisition critical path where older Route-B / D05 / D09 checkpoints are broader.

## 1. Critical-path decision

`P0_RAW_CAPTURE_BLOCKER_STATE = NO_SCIENTIFIC_BLOCKER_IDENTIFIED`.

The current open scientific backlog does not block acquisition of raw SEC/Form-4 response bytes.

Specifically, current liquidity-gate parameters, P_MAX_REF/P_TARGET_REF, BETA_LIQ_MAX, candidate windows, lambda, UCB/dependence method, K_forward, M_economic, mini-D09, D05 ceiling mechanics, final D07 geometry and D19 mechanics remain required for their downstream consumers but are classified for P0 acquisition as:

`BLOCKS_ONLY_LATER_INFERENCE_OR_ECONOMICS`.

## 2. Day-1 P0 minimum

P0 may begin when Builder proves:
- exact raw response bytes are stored immutably / append-only;
- content hash and byte length are recorded;
- request-attempt and local response-receipt UTC timestamps are append-only;
- result/status and collector version/source locator are recorded;
- every scheduled attempt leaves a liveness/heartbeat record.

No complete manifest, parser, gap-reconciliation engine, resume system, liquidity rule or inference stack is required before the first compliant capture.

## 3. Minimal visibility firewall

Before scientific-content visibility is authorized, protocol-mutating actors may see only opaque operational telemetry:
- hash/object id;
- size;
- local receipt/attempt times;
- success/no-new-data/failure;
- collector liveness/storage health.

Raw filing body, parsed fields, counts, distributions and other interpretable/derived Form-4 content remain hidden from protocol-mutating actors.

`CAPTURE_PERMISSION != CONTENT_VISIBILITY_PERMISSION != CONFIRMATION_ADMISSIBILITY`.

## 4. Progressive hardening

After compliant capture begins, Builder should add without rewriting historical raw objects:
- manifest;
- formal gap ledger/reconciliation;
- restart/resume;
- parser/normalizer;
- registry integration;
- completeness checks;
- scientific admissibility state.

Any unfillable historical gap remains explicit.

## 5. Current implementation state

Current Blue system state identifies the insider-filings lane as blocked on the absence of a point-in-time filing feed.

Therefore:

`P0_IMPLEMENTATION_GAP = TRUE`.

The next implementation mission should target the minimal durable SEC/Form-4 capture slice before returning to deeper Route-B specification work, unless a newly discovered issue demonstrates a concrete `BLOCKS_CAPTURE_INTEGRITY`, `BLOCKS_PIT_RECONSTRUCTABILITY`, or `BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL` failure.

## 6. Unchanged downstream protections

This addendum does not:
- certify captured filings for scientific confirmation;
- authorize parsing/aggregates to protocol-mutating actors;
- authorize D05 ceiling visibility;
- satisfy the Route-B final-protocol firewall;
- authorize Form-4 outcome analysis or capital deployment.
