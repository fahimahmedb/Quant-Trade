# Next Build Mission — P0 SEC/Form-4 Continuous Service

This is the next Builder milestone.

Before acting, read `QUANT_NORTH_STAR.md`, `STATE.md`, and:

- `governance/P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md`
- `governance/BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md`

Do not reopen Route-B scientific specification as part of this mission.

Current recorded state:

`P0_RAW_CAPTURE_BLOCKER_STATE = NO_SCIENTIFIC_BLOCKER_IDENTIFIED`

`P0_RAW_CAPTURE_OPERATIONAL = TRUE`

`P0_IMPLEMENTATION_GAP = FALSE`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

PR #16 established the durable capture slice with real SEC requests, immutable raw storage,
PIT acquisition envelopes, durable heartbeat/attempt history, restart safety, conservative
request controls and the minimal visibility firewall.

## Mission

Turn the proven SEC/Form-4 P0 collector into a continuously operating acquisition service owned
by the existing Quant Control Plane.

The critical path is now service continuity: keep the acquisition clock running reliably without
letting research, desk backlog, process restarts, transient source/network failures or local
runtime configuration silently stop point-in-time capture.

This mission is operational hardening, not scientific analysis.

## Existing contracts remain controlling

Do not weaken or reinterpret the already-frozen P0 rules.

In particular preserve:

- exact immutable raw response bytes;
- content-addressed / append-only storage;
- request-attempt and local response-receipt timestamps;
- durable heartbeat / attempt history;
- earned `NO_NEW_DATA`, never default success;
- explicit `COVERAGE_UNKNOWN` when continuity cannot be proven;
- frozen SEC request limiter/backoff policy;
- fail-closed requester identity/contact configuration;
- `CAPTURED != VISIBLE_FOR_PROTOCOL != ADMISSIBLE_FOR_CONFIRMATION`;
- no interpretable Form-4 content or scientific aggregate on protocol-mutating surfaces.

Route-B, D05, D07, D09 and D19 work may proceed in parallel. None of that work may stop the raw
capture clock unless a concrete failure is shown to be
`BLOCKS_CAPTURE_INTEGRITY`, `BLOCKS_PIT_RECONSTRUCTABILITY`, or
`BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL`.

## Continuous-service work

Use the existing Control Plane / Clock. Do not create a separate one-off collector architecture.

Close the operational gap by proving that:

1. SEC capture remains scheduled ahead of replayable research/desk work and cannot be starved by backlog.
2. Repeated poll cycles leave durable liveness evidence even when there is no new filing.
3. Process restart, host restart or ordinary deployment restart resumes from durable collector state without mutating prior evidence.
4. Transient network/5xx, 429 and automated-access 403 states remain bounded by the frozen limiter/backoff rules and never hot-loop.
5. Loss of requester identity/contact configuration fails closed and is visible as `BLOCKED`, not as healthy idle service.
6. A collector that stops polling becomes observably stale; heartbeat health cannot masquerade as source coverage.
7. Only one effective SEC request budget is active for this requester. Until a shared multi-host limiter exists, concurrent collectors on separate machines must be prevented operationally.
8. Source-window continuity failures remain explicit and feed the existing gap/reconciliation state rather than being silently skipped.
9. The production status surface remains firewall-safe while still showing enough opaque telemetry to diagnose service health.
10. Capture continues while downstream parser, reconciliation, Route-B and scientific work advance independently.

## Evidence required

Commit durable evidence sufficient to establish continuous-service behavior without exposing
scientific Form-4 content.

At minimum demonstrate:

- multiple scheduled poll cycles under the Control Plane;
- durable liveness across idle/no-new-data periods;
- at least one restart/resume during the service run;
- no capture starvation from other Quant work;
- explicit stale/blocked behavior when polling cannot proceed;
- preserved request-policy configuration and cooldown state;
- preserved raw-object/envelope integrity;
- firewall-safe status / Chief Brief / journal surfaces.

Do not publish filing identities, filing counts, parsed fields, distributions or outcome-bearing
statistics as proof.

## Progressive hardening

The following may advance while service remains live:

- formal denominator manifest and reconciliation;
- backfill / gap repair;
- parser / normalizer downstream of immutable raw storage;
- Data Plane registry integration;
- scientific admissibility state;
- Route-B / D05 / D07 / D09 / D19 specification and implementation.

Do not stop a healthy collector merely because one of these downstream layers is unfinished.

## Definition of done

This milestone is complete when the SEC/Form-4 capture path is not merely demonstrated in a live
probe but is operated as a persistent Quant service with durable scheduling, restart/resume,
observable liveness, explicit coverage state, bounded failure behavior and the existing visibility
firewall intact.

If continuous operation is blocked by environment or SEC/network behavior, leave the collector in
an explicit persistent `BLOCKED` or `STALE` state with the attempt history intact. Do not weaken
the request policy or fabricate continuity.
