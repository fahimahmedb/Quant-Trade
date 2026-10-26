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

PR #16, `P0: durable SEC/Form-4 raw capture, running and probed live`, is merged into
`blue/handoff-memory-2026-09-15` at merge commit
`52dfe380c753cad44f2876fd5a04d68c46ead8db`.

Committed live-probe evidence:
`handoff/SEC_FORM4_P0_FIRST_LIVE_PROBE_2026-09-18.json`.

The recorded Day-1 acceptance state is:

- `VALID_DISCOVERY = TRUE`;
- `COVERAGE_STATE = COMPLETE`;
- `HEARTBEAT_DURABLE = TRUE`;
- `RAW_CAPTURE_DURABLE = TRUE`;
- immutable/content-addressed raw storage present;
- restart/resume evidence present;
- conservative SEC request controls active;
- visible evidence sanitized to opaque acquisition telemetry.

Therefore the current acquisition state is:

`P0_RAW_CAPTURE_OPERATIONAL = TRUE`.

`P0_IMPLEMENTATION_GAP = FALSE`.

The `insider_filings` research lane remains blocked on downstream scientific protocol /
visibility / admissibility work, not on absence of raw acquisition.

The remaining acquisition-critical operational question is continuous service. The live probe
demonstrates the capture path and restart safety, but does not by itself prove unattended
long-duration service across future source/network/runtime disturbances.

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`.

This open service question does not reclassify the existing scientific backlog as a raw-capture
blocker. Work on Route B, D05, D07, D09 and D19 may proceed in parallel without stopping the
acquisition clock.

### 5.1 Historical visibility exposure note

During PR #16 review/merge, an aggregate raw Form-4 capture count was visible in repository-facing
state/evidence and was also observed by Blue. The current tip removes that count from the visible
P0 state/probe surfaces.

That prior exposure cannot be made unseen. It therefore has no authority to justify, relax, tune or
select any later claim-defining, D05, D07, D09, liquidity, power or admissibility rule.

This is a recorded anti-selection constraint, not a new raw-capture blocker. Acquisition continues
under the existing P0 firewall.

### 5.2 Continuous-service observation rule — FROZEN

The continuous-service proof is temporal. It cannot be closed by a live probe, a unit test, or a
point-in-time health check.

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`.

The qualifying observation window starts only after the following are deployed and durable:

- scheduler-state provenance sufficient to reconstruct every expected poll from recorded state
  transitions rather than from the absence of attempts;
- lifecycle provenance emitted by the external launcher / supervisor, not self-attested by the
  collector;
- a prospectively materialized `ACQUISITION_CRITICAL_FINGERPRINT`.

The observation window must contain at least one complete weekend and at least one predeclared
source-normal silence interval. A holiday may satisfy the latter only when the applicable source
calendar was identified before observing the publication outcome. If the minimum fourteen days
elapse before those calendar conditions are satisfied, the window remains open until they are.

#### Scheduler provenance

Every transition that can change the next expected acquisition action must durably record at least:

- transition time;
- scheduler state;
- `next_due_at`;
- transition cause;
- effective acquisition-critical policy/fingerprint;
- active backoff/cooldown state when applicable.

The retrospective audit derives the expected attempt sequence from these transitions. It must never
infer that an attempt was not due merely because no attempt was recorded.

#### Lifecycle provenance

Every service start/restart must carry an externally supplied boot/instance identifier, timestamp
and launch cause. The minimum cause vocabulary is:

- `SCHEDULED_START`;
- `AUTOMATIC_RESTART_AFTER_FAILURE`;
- `DEPLOYMENT_RESTART`;
- `MANUAL_START`.

A collector process cannot authoritatively classify its own origin.

#### Acquisition-critical fingerprint

Before `t0`, Builder must materialize and commit a deterministic fingerprint over the code and
effective configuration that control acquisition semantics. At minimum it covers:

- polling cadence / scheduler transition rules;
- request limiter, backoff and cooldown semantics;
- discovery endpoint/query construction and response validation;
- pagination / continuity / cursor semantics;
- the rule by which `NO_NEW_DATA` is earned;
- coverage-state transitions;
- acknowledgement / cursor-advance / restart semantics;
- raw-object and acquisition-envelope durability semantics;
- P0 visibility-firewall behavior;
- scheduler and lifecycle provenance semantics used by this audit.

The fingerprint definition itself is prospective: its membership cannot be narrowed after an
incident in order to preserve the observation window.

#### Intervention classification

The following invalidate the active observation window and reset `t0`:

- any change to the `ACQUISITION_CRITICAL_FINGERPRINT`;
- `MANUAL_START` after a stop or failure;
- manual mutation of collector durable state, cursor, acknowledgement state or acquisition journal;
- manual bypass/override of cadence, limiter, backoff, cooldown, coverage or discovery validation;
- any deployment/restart that leaves an expected acquisition action unexplained or missed.

The following do not invalidate the window when fully journaled and when the
`ACQUISITION_CRITICAL_FINGERPRINT` is unchanged:

- read-only observation/audit;
- downstream manifest, gap-ledger, backfill, parser/normalizer, registry or scientific work;
- unrelated configuration changes outside the critical fingerprint;
- a `DEPLOYMENT_RESTART` or `AUTOMATIC_RESTART_AFTER_FAILURE` whose external cause is recorded,
  whose durable state resumes correctly, and which leaves no expected poll unaccounted for.

This distinction permits non-acquisition-critical development to continue while the calendar proof
runs. It does not permit an operator to create a planned silence and relabel it as healthy service.

#### Closure condition

`P0_CONTINUOUS_SERVICE_STATE` may close only when one retrospective audit establishes all of:

1. the qualifying calendar window above has elapsed;
2. every expected acquisition action is derivable from scheduler-state transitions and is accounted
   for by an attempt, an authorized backoff/cooldown transition, or an explicit failure state;
3. there is no unexplained heartbeat/attempt hole;
4. the window contains no invalidating intervention;
5. restart/deployment events preserve raw objects, acquisition envelopes and remaining work;
6. invalid or incomplete discovery never resolves to `NO_NEW_DATA`;
7. source-normal silence is distinguishable from collector death by the durable heartbeat/lifecycle
   record.

Until then:

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`.

## 6. Unchanged downstream protections

This addendum does not:
- certify captured filings for scientific confirmation;
- authorize parsing/aggregates to protocol-mutating actors;
- authorize D05 ceiling visibility;
- satisfy the Route-B final-protocol firewall;
- authorize Form-4 outcome analysis or capital deployment.
