# Blue Checkpoint — P0 Continuous Service

**Date:** 2026-09-18  
**Authority:** Blue Team / Mission Control continuity checkpoint  
**Repository:** `fahimahmedb/Quant-Trade`  
**Previous verified frontier:** `ef4e1fe30b8f96f6dd70fa26add67d224b5edc8d`

This file exists so future Blue sessions do not depend on chat history. Repository evidence remains
authoritative over prose memory.

## Read first on restart

1. `QUANT_NORTH_STAR.md`
2. `governance/P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md`
3. `governance/BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md`
4. `governance/P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md`
5. `NEXT_BUILD_MISSION.md`
6. `STATE.md`

## Current P0 state

`P0_RAW_CAPTURE_BLOCKER_STATE = NO_SCIENTIFIC_BLOCKER_IDENTIFIED`

`P0_RAW_CAPTURE_OPERATIONAL = TRUE`

`P0_IMPLEMENTATION_GAP = FALSE`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P0_CONTINUITY_T0_BLOCKER_STATE = BLOCKS_CAPTURE_INTEGRITY`

PR #16 established live durable SEC/Form-4 raw capture. Raw acquisition is no longer the blocker for
the insider-filings lane; downstream parsing, qualification, visibility and scientific admissibility
remain separate.

Route B / D05 / D07 / D09 / D19 work may proceed in parallel and does not stop the acquisition
clock unless a concrete capture-integrity, PIT-reconstructability or visibility-firewall blocker is
demonstrated.

## Continuous-service proof — frozen decisions

Closure is temporal, not a point-in-time test.

Minimum observation:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

The qualifying window must also contain:

- one complete weekend;
- one predeclared source-normal silence interval.

The window does not start until all three are deployed:

1. durable scheduler-state provenance sufficient to reconstruct expected polls;
2. external launcher/supervisor lifecycle provenance;
3. a prospectively materialized `ACQUISITION_CRITICAL_FINGERPRINT`.

### Scheduler evidence

Every cadence-changing transition records scheduler state, `next_due_at`, cause, critical
fingerprint/policy and any active backoff/cooldown. Expected attempts are reconstructed from these
transitions, never inferred from missing journal entries.

### Lifecycle evidence

Start/restart cause comes from the external launcher/supervisor, not from the collector itself.
Minimum causes:

- `SCHEDULED_START`
- `AUTOMATIC_RESTART_AFTER_FAILURE`
- `DEPLOYMENT_RESTART`
- `MANUAL_START`

### Intervention rule

The window resets when acquisition-critical semantics change, when a stopped/failed collector is
manually started, when acquisition durable state is manually mutated, when safety controls are
bypassed, or when a deployment/restart leaves an expected acquisition action unexplained.

The window may continue across read-only observation, downstream manifest/gap-ledger/backfill/parser
work, unrelated configuration changes and deployment/automatic restart only if the critical
fingerprint is unchanged, lifecycle cause is recorded, durable state resumes correctly and no
expected acquisition action is unaccounted for.

This rule exists specifically so non-acquisition-critical development can continue while calendar
time accrues.

## Fingerprint V1 implementation finding

The acquisition-critical fingerprint must cover the modules that *produce* scheduler and discovery
transitions, not merely the polling configuration. The frozen V1 membership includes policy,
budget, transport, discovery, collector, store, visibility and timebase semantics plus the
acquisition-specific Control Plane scheduling path and the effective supervisor/restart policy.

Two concrete pre-`t0` implementation gaps were identified:

- `SecAccessPolicy.to_dict()` omits at least `filings_per_drain`, `accept_encoding` and
  `max_response_bytes`; it therefore cannot serve as the fingerprint's canonical config input.
- `transport.py` currently contains an internal fresh-connection HTTP retry after certain failures,
  while the collector reserves/journals only the outer request. This can emit a second network
  request without a distinct budget reservation and durable attempt id.

The observation clock must not start until the runtime fingerprint serialization is complete and
actual HTTP requests obey one reservation / one auditable attempt identity.

### Capture-integrity blockers before `t0`

The reclassification filter now has two concrete class-1 objects:

- `HIDDEN_TRANSPORT_RETRY`: the transport can emit more actual SEC HTTP requests than the budget
  reservations / durable attempt ids record. This is both an audit defect and a real SEC traffic
  budget defect.
- `INCOMPLETE_CRITICAL_POLICY_SERIALIZATION`: the candidate policy serialization can omit effective
  policy fields, allowing semantically different acquisition policies to share a fingerprint.

Preferred retry repair is deletion of the nested transport HTTP retry. If Builder retains any retry,
the retry itself must become a prospective scheduler transition with its own cause, due state,
budget reservation and durable attempt id.

Canonical policy serialization must be complete by construction. A test compares
`dataclasses.fields(SecAccessPolicy)` against three pairwise-disjoint classification sets:
included, deterministically transformed, or explicitly non-critical. A newly added unclassified
field must fail immediately.

Neither blocker revokes the fact that P0 raw capture has operated live. Both prevent authorization
of the fourteen-day continuity `t0`.

## Three operational claims still requiring evidence

1. **Unattended continuity:** after instrumentation and `t0`, the service remains continuously
   accountable for the full qualifying calendar window without an invalidating intervention.
2. **Restart durability:** interruption/restart preserves raw objects, acquisition envelopes and
   remaining work.
3. **Discovery fail-closed:** invalid/incomplete discovery cannot become `NO_NEW_DATA`.

The existing live probe does not by itself close claim 1.

## Historical visibility exposure

An aggregate raw Form-4 capture count was visible during PR #16 review/merge and was observed by
Blue before being removed from current visible surfaces.

That exposure is irreversible and must remain recorded. It has no authority to tune or relax later
claim-defining, D05, D07, D09, liquidity, power or admissibility decisions. Any downstream
admissibility consequence is decided downstream; acquisition does not stop because of it.

## Broken document references

Seven historical governance references resolve only by nearby filename rather than exact filename.
They remain hygiene debt, not acquisition critical path, unless one is later shown necessary to
start/restart the service or interpret a collector failure.

## Restart discipline

Do not reconstruct decisions from chat memory. Re-read the committed files above and bind every
moving implementation claim to an exact SHA.

If a later checkpoint supersedes this one, record that supersession explicitly rather than silently
editing the historical meaning of this file.
