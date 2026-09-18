# P0 RAW CAPTURE CRITICAL-PATH RECLASSIFICATION — 2026-09-18

**Status:** CLOSED / FROZEN STRATEGIC RECLASSIFICATION — BUILDER IMPLEMENTATION NOT YET CERTIFIED  
**Authority:** Blue Team / Mission Control  
**Highest authority:** `QUANT_NORTH_STAR.md`

This amendment applies the capture-critical-path test retroactively to the current open governance backlog. Its purpose is to stop later inference/economic dependencies from preventing acquisition of irreversible point-in-time evidence.

The governing question for any dependency is:

> What material error does this requirement prevent at the next step, and why must it be resolved before that step?

## 1. Four capture-critical-path classes

Every current or future dependency must be classified for the immediate step:

1. `BLOCKS_CAPTURE_INTEGRITY`
   - failure would corrupt, overwrite, misidentify, or make the acquired raw source bytes unverifiable.

2. `BLOCKS_PIT_RECONSTRUCTABILITY`
   - failure would destroy an irrecoverable timestamp/source-state fact needed later to reconstruct what was known/received when.

3. `BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL`
   - unresolved human/machine visibility could allow observed source content or derived statistics to tune still-open scientific rules.

4. `BLOCKS_ONLY_LATER_INFERENCE_OR_ECONOMICS`
   - the object matters for later support, inference, economics, execution, or certification but does not determine which source bytes can be acquired and preserved faithfully now.

Only classes 1-3 may block raw P0 capture. Class 4 remains scientifically required but leaves the acquisition critical path.

**Invariants**
- `LATER_INFERENCE_DOES_NOT_BLOCK_RAW_CAPTURE`
- `CAPTURE_BLOCKER_REQUIRES_NEXT_STEP_MATERIAL_ERROR_ARGUMENT`
- `GOVERNANCE_BACKLOG_IS_RETROACTIVELY_RECLASSIFIED`

## 2. Retroactive classification of current Route-B / liquidity backlog

The following currently open objects are classified for **raw SEC/Form-4 capture** as:

`BLOCKS_ONLY_LATER_INFERENCE_OR_ECONOMICS`

including:
- numerical liquidity gate / support threshold;
- `P_MAX_REF` and `P_TARGET_REF`;
- `BETA_LIQ_MAX`;
- `TAU_BETA` / `ALPHA_BETA`;
- candidate ADV windows;
- ADV breach UCB / calendar x corporate dependence method;
- lambda derivation / materiality discharge;
- `K_forward`;
- `M_economic`;
- Route-B mini-D09 remainder / BEEE / MEUE instantiation;
- final D05-A ceiling construction/visibility;
- final D07 outcome/entry geometry where it does not alter raw filing acquisition;
- D19 adverse-completion mechanics;
- final deployment-security / liquidity-support instantiation.

These objects can block later scientific consumption, support classification, inference, economic conclusions, or capital authorization. They do **not** determine which SEC response bytes should be acquired or the local time at which they were received.

Therefore:

`CURRENT_SCIENTIFIC_BACKLOG_HAS_NO_AUTHORIZED BLOCK ON P0_RAW_CAPTURE`.

This statement does not authorize analysis of the captured content.

## 3. Current repository evidence and P0 status

The current system state identifies:

`SCAN-INSIDER-FILINGS-001 — BLOCKED: point-in-time filing feed absent`.

The current Data Plane implements generic ingestion/provenance for daily market data but the Blue branch does not contain a dedicated SEC/Form-4 raw-capture adapter in `src/quant/dataplane/`.

Therefore:

`P0_RAW_CAPTURE_OPERATIONAL = FALSE`

at this checkpoint.

The missing point-in-time filing feed is an implementation gap, not a reason to wait for later inference/economic contracts.

## 4. Day-1 irrecoverable minimum

P0 raw capture should start as soon as the following minimal irreversible properties are implemented correctly.

### 4.1 Immutable raw response preservation

For every successful source response intended for capture:
- store the exact received body bytes without normalization or mutation;
- compute a cryptographic content hash over those exact bytes;
- write to an append-only/content-addressed or equivalently immutable store;
- never overwrite an existing object under the same identity.

A later parser may derive structured objects, but it may not replace the raw source object.

### 4.2 Local receipt timing separated from source timing

Record an append-only local acquisition envelope containing at minimum:
- request/source locator;
- request-attempt timestamp in UTC;
- response-received/completed timestamp in UTC;
- HTTP/result status sufficient to distinguish successful acquisition from failed attempt;
- raw object content hash when bytes were received;
- byte length;
- collector/protocol version identifier.

Source publication/acceptance timestamps are distinct objects. They may be parsed later from authoritative source metadata/raw content but must never be silently substituted for local receipt time.

A backfilled historical filing acquired today does not become contemporaneously captured historical evidence merely because the SEC document contains an older acceptance/publication time.

### 4.3 Minimal liveness / attempt journal

A receipt timestamp alone cannot distinguish:
- no source item existed;
- polling was attempted and returned no eligible new object;
- the collector was down and never asked.

Therefore every scheduled capture attempt must leave a minimal append-only attempt/heartbeat record, including success/no-new-data/failure state.

The full gap-reconciliation ledger and automatic resume logic may be added later, but the attempt history needed to reconstruct collector liveness begins on day 1.

**Invariants**
- `RAW_BYTES_AND_RECEIPT_TIME_ARE_DAY1_IRREVERSIBLES`
- `ATTEMPT_LIVENESS_IS_DAY1_IRREVERSIBLE_EVIDENCE`
- `SOURCE_TIME_IS_NOT_LOCAL_RECEIPT_TIME`
- `BACKFILL_RECEIPT_DOES_NOT_RETROACTIVELY_CREATE_HISTORICAL_CAPTURE_TIME`

## 5. Minimal P0 visibility firewall

Raw capture may precede scientific protocol completion.

However "raw" does not mean "non-interpretable": a Form-4 XML/HTML payload can directly expose transaction codes, dates, issuer/owner identities and amounts.

Therefore while protocol-mutating scientific decisions remain open:

**Visible operational telemetry may include:**
- collector RUN/IDLE/BLOCKED state;
- opaque object identifier/hash;
- byte length;
- local receipt timestamp;
- request-attempt timestamp/status/error class;
- source endpoint class;
- storage/immutability health;
- liveness / outage duration.

**Not authorized for protocol-mutating actors by P0 capture alone:**
- raw filing body/content;
- parsed filing fields;
- filing counts by period/issuer/owner/code;
- transaction distributions;
- qualification counts;
- crossing/event counts;
- any derived aggregate or statistic that can tune an open claim-defining rule.

This firewall is intentionally smaller than the D05 ceiling-visibility firewall. It protects only against content-driven tuning while allowing acquisition-health observability.

**Invariants**
- `CAPTURE_PERMISSION_DOES_NOT_IMPLY_CONTENT_VISIBILITY_PERMISSION`
- `OPAQUE_OPERATIONAL_TELEMETRY_IS_VISIBLE_BEFORE_SCIENTIFIC_CONTENT`
- `NO_DERIVED_INTERPRETABLE_P0_STATISTICS_BEFORE_AUTHORIZED_VISIBILITY`

## 6. Progressive hardening after capture starts

The following are high-priority P0/P1 hardening work but do not justify delaying day-1 capture once Section 4 is correct:
- complete manifest schema;
- formal gap-reconciliation ledger;
- restart/resume cursor;
- backfill/reconciliation engine;
- parser/normalizer;
- qualification logic;
- dataset registry integration;
- completeness reports;
- scientific admissibility labels.

They must be added without mutating historical raw objects or rewriting their original receipt envelopes.

If later hardening discovers an unfillable gap, the gap remains explicit; it is not repaired by inventing historical receipt timestamps.

## 7. Capture versus confirmation

Three independent states are required:

`DATA_CAPTURED`

`DATA_VISIBLE_FOR_SCIENTIFIC_PROTOCOL`

`DATA_ADMISSIBLE_FOR_CONFIRMATION`.

None implies the next.

Data collected before final protocol freeze may preserve future options but does not acquire confirmation authority retroactively merely because it exists.

Admissibility depends on the eventual separation, protocol-freeze, visibility and anti-selection rules.

## 8. Operational source-policy dependency

Source-specific access requirements that are necessary to acquire data lawfully/reliably — identification, fair-access/rate behavior, retry/backoff, endpoint semantics, response validation — are capture-integrity dependencies.

Their exact current values must be verified against the authoritative source before Builder implementation and cannot be inferred from stale project assumptions.

This is an operational capture dependency, not a Route-B scientific inference dependency.

## 9. Immediate strategic consequence

The current critical path is split:

**P0 acquisition lane — start now when Day-1 irreversible minimum is implemented**
`source -> request/heartbeat -> receipt timestamp -> immutable raw bytes/hash`.

**Parallel scientific lane — continue without blocking capture**
`liquidity / D09 / UCB / D07 / D19 / final visibility-admissibility authority`.

A new governance item may block P0 only by stating which Section-1 class it belongs to and the concrete next-step error it prevents.

Absent that demonstration, it remains off the acquisition critical path.

## 10. Current decision

`P0_RAW_CAPTURE_BLOCKER_STATE = NO_SCIENTIFIC_BLOCKER_IDENTIFIED`.

`P0_IMPLEMENTATION_GAP = TRUE`.

The next Builder objective should therefore be a minimal durable SEC/Form-4 capture slice centered first on the irreversible Day-1 properties, then hardened while capture is already accumulating.

This amendment does not certify the resulting data for scientific confirmation, does not authorize derived Form-4 statistics, and does not satisfy the Route-B final-protocol firewall.
