# Builder — Gate-C prospective event-plan prestage — 2026-09-21

`MISSION_TYPE = READ_ONLY_ANALYSIS + HANDOFF_ONLY`

`GATE_C_EVENT_PLAN_PRESTAGE = READY_FOR_BLUE_REVIEW`

This is a prospective template for Blue review, not an activated precommit,
launch instruction, target-host observation, or Gate-C acceptance. It advances
the persistent Data/Control Plane's continuity evidence contract; it proves no
scientific alpha or economic eligibility.

## 1. Exact authority and scope

- Work branch: `builder/gate-c-prospective-event-plan-prestage-2026-09-21`.
- Verified starting HEAD: `621b319d34918dbbef486e372c89379a58f1adc5`.
- User-specified Blue authority before dispatch: `ba510bd5e3077c7e29b35aef9cf45c98a5fd128c`.
  The mission's expected-start reference is this Blue base; the user's explicit
  mission-commit HEAD above governs this delivery. The dispatch itself preserves
  its earlier `4c855dca152d237d2b8d86419ebc5e3a59acde42` authority reference.
- Highest product authority: [QUANT_NORTH_STAR.md](../QUANT_NORTH_STAR.md).
- Lane-D dispatch: [Blue parallel preparation](../governance/BLUE_GATE_B_PARALLEL_PREPARATION_DISPATCH_2026-09-21.md).
- Mission: [Builder mission](BUILDER_GATE_C_PROSPECTIVE_EVENT_PLAN_PRESTAGE_MISSION_2026-09-21.md).
- Qualification: [promoted hybrid amendment](../governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md).
- Precommit: [authoritative t0 template](../governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md).
- Sequence: [Gate-B-to-Gate-C runbook](../governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md).
- Calendar/fingerprint: [Blue binding](../governance/BLUE_P0_FINGERPRINT_AND_SOURCE_CALENDAR_BINDING_2026-09-21.md).

The promoted hybrid amendment supersedes historical fixed-P14D statements in
older checkpoints, including the calendar-binding document's historical safety
section. No elapsed-day threshold is added here.

Frozen production identity, distinct from this documentation branch:

```text
CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
VERIFIED_INPUT_TREE_DIGEST = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
SOURCE_CALENDAR_AUTHORITY_VERSION = SEC_EDGAR_CALENDAR_2026 / FROZEN_V4_BLOB_b4fbd58b381e01ec882b60386cf73d4017e7db5c
```

Read directly from frozen V4: `calendar.py` (blob
`b4fbd58b381e01ec882b60386cf73d4017e7db5c`), `collector.py` (blob
`dd301dab4de08719293ef35df02164e9d663248a`),
`tests/test_p0_continuity_compression.py` (blob
`8586c7d7496f9f68ef39cf7547a197d3a3a5a684`), plus scheduler, audit, policy,
clock, CLI and service definition. The tests distinguish settlement boundaries,
Eastern bootstrap date, weekend/holiday exclusion, unbound-year failure, DST,
and direct/CLI attempts to bypass settlement or skip the oldest due day.
No source-calendar web request was made; this analysis uses the committed Blue
binding and frozen code. Git fetch/push are the user's explicit delivery exception
to the mission's no-network work scope. No SEC request or target-runtime command
is part of this handoff.

## 2. Future entrance and anti-selection rule

Before using this template, Blue must receive the exact-host, exact-candidate
Gate-B artifact, validate its evidence/schema and record PASS, then explicitly
authorize preparation of one qualifying launch. A local operator green result
is insufficient. Gate B PASS still leaves `t0 = NOT_DECLARED`.

Immediately before sealing, refresh the entire calendar plan using the actual
future precommit time, current bound calendar, sanitized qualifying-state
bootstrap/history, exact runtime policy, and time-authority recheck. Every
selected closure must still be wholly prospective and covered from its start.
A launch that occurs after the selected ordinary closure starts cannot qualify
that interval. Preserve the failed attempt; do not substitute a later interval
or launch under the same precommit. Bind a latest permissible launch boundary
before that closure and an explicit expiration policy in the plan.

Seal the immutable precommit in the restricted evidence domain BEFORE the next
single launch and before qualifying outcomes exist. Commit this semantic rule:

> The next single qualifying systemd launch that consumes
> QUALIFYING_LAUNCH_AUTHORITY_ID while all bound identities match is the unique
> t0 event for this attempt.

No matching launch, more than one candidate launch, wrong identities, ambiguous
provenance, replay, or a launch preceding the seal means `NO_T0`. An observed
successful interval cannot supply a retrospective t0. New authority requires a
new precommit and a new attempt, never replacement within the old precommit.

## 3. Event definitions and observable completion

All calendar boundaries use `America/New_York`; preserve local timestamps with
UTC offsets AND aware UTC timestamps. Intervals below are half-open `[start,end)`.
A bound business day is Monday–Friday excluding the frozen 2026 closure set.
Unbound years fail closed; weekday arithmetic alone supplies no authority.

| Event | Prospective definition | Restricted evidence needed |
| --- | --- | --- |
| E1 ordinary closed interval | Select consecutive ordinary business dates D and D+1, neither a holiday, with closure D 22:00 ET through D+1 06:00 ET. It is a full ordinary overnight, not a weekend/holiday substitute. Launch must precede its start. | Calendar derivation, live lifecycle/heartbeat continuity across both boundaries, complete scheduler and attempt evidence throughout. |
| E2 subsequent acquisition | First scheduler-required DISCOVERY cycle at or after E1 reopening, within the predeclared business-hours acquisition window. Bind the selection rule before launch; actual obligation IDs arise prospectively at runtime. | Obligation ID/action/due time, durable attempt and validated discovery result, required drain/successor provenance, no unresolved coverage gap. A valid no-new-data response can complete a cycle; a new filing is not required. |
| E3 complete weekend closure | Select a later Friday business close at 22:00 ET through the next Monday business reopening at 06:00 ET, covering all Saturday and Sunday. If adjacent holidays extend closure, enumerate their boundaries separately and use the actual next bound business reopening; the full weekend remains mandatory. | Continuous accountable runtime over the entire closure; attempts and reconciliations still due inside it; no inferred shutdown permission. |
| E4 first post-weekend acquisition | First scheduler-required DISCOVERY cycle at or after the bound E3 reopening. The first cycle and any authorized backoff/cooldown successor must remain visible; never choose a later good cycle and hide the first. | First obligation and resolution, source outcome, successor chain, completed valid acquisition/coverage evidence. Failure is recorded as failure, not successful reopening. |
| E5 applicable reconciliation | For each eligible source business date d, eligibility starts at `UTC(d 22:00 America/New_York) + 30 elapsed hours`. Select the oldest unreconciled eligible day from the qualifying state's Eastern bootstrap date. | Due computation, RECONCILE obligation/attempt, validated daily-index raw-object/provenance digest, reconciliation result, durable reconciled-state and coverage/gap verdict. |

The E1 → E2 → E3 → E4 sequence is prospective. E5 runs whenever due, including
inside E3; it is not deferred until after E4. For closure, this proposed plan
requires reconciliations for the ordinary pre-closure source day, weekend's
last business day, and first post-weekend business day, plus all older eligible
unreconciled days in the state lineage and all further dates that become due
through the final audit cutoff. The first post-weekend day's index therefore
cannot be claimed at Monday reopening: that business day must close and settle.
This explicit event target set prevents arbitrary choice of an easy index.
Blue must bind the actual target dates and initial state history before launch.

Settlement is an eligibility boundary, not a promise of publication or a fixed
completion deadline. Convert close to UTC BEFORE adding 30h: DST must neither
shorten nor lengthen elapsed settlement. No reconciliation for weekend/holiday
dates. No early direct/CLI reconcile; no skipping the oldest due date. Frozen
V4 defers reconciliation while cooldown is active; preserve its cause and due
successor, rather than treating cooldown as successful reconciliation.

HTTP failure/404/429/403, malformed/truncated index, `DAILY_INDEX_UNAVAILABLE`,
or `DAILY_INDEX_GAP` is not a calendar closure and does not fulfill E5. Accounted
source failure remains visible; missing proof keeps Gate C open/blocked and goes
to Blue. Never manually clear gaps, seed reconciled dates, or repair raw state
to achieve a green result. Any invalidator in section 8 terminates the attempt.

The bound plan must provide concrete UTC acquisition-window start/end values
and the deterministic first-obligation selection rule. Use actual service
cadence and frozen backoff/cooldown semantics, not an invented guaranteed request
at exactly 06:00. Failure to complete the selected event window is reported to
Blue; it is not silently rolled to a favorable later window.

## 4. PRELIMINARY ONLY calendar illustration

These are nearest illustrative windows relative to 2026-09-21, derived offline
from the bound 2026 calendar. They are NOT selected qualifying windows, launch
authority, a schedule commitment, or evidence of Gate B PASS. Refresh immediately
before the actual precommit; never copy already elapsed windows.

| Item | Eastern boundary/date | UTC boundary |
| --- | --- | --- |
| Ordinary closure | Mon Sep 21 22:00 EDT → Tue Sep 22 06:00 EDT | Sep 22 02:00Z → Sep 22 10:00Z |
| Subsequent source-open window | Tue Sep 22 06:00–22:00 EDT | Sep 22 10:00Z → Sep 23 02:00Z |
| Complete weekend closure | Fri Sep 25 22:00 EDT → Mon Sep 28 06:00 EDT | Sep 26 02:00Z → Sep 28 10:00Z |
| First post-weekend source-open window | Mon Sep 28 06:00–22:00 EDT | Sep 28 10:00Z → Sep 29 02:00Z |
| Sep 21 daily index earliest eligibility | Wed Sep 23 04:00 EDT | Sep 23 08:00Z |
| Sep 25 daily index earliest eligibility | Sun Sep 27 04:00 EDT, during weekend closure | Sep 27 08:00Z |
| Sep 28 daily index earliest eligibility | Wed Sep 30 04:00 EDT | Sep 30 08:00Z |

The acquisition rows identify enclosing source-open windows. Before launch Blue
must bind their first-required-cycle selection and evidence rules, including
inherited cooldown/backlog. Dates between these examples also create applicable
reconciliation work. Sep 30 08:00Z is only illustrative settlement eligibility,
not a promised completion time. No elapsed duration alone closes Gate C.

## 5. Scheduler, heartbeat and attempt accounting

The calendar describes expected source publication silence, not collector
silence. V4 discovery polling is not disabled overnight or on weekends. A
weekend can contain both polling and daily-index work. Do not infer nothing was
due because no request, filing, or attempt was observed.

Bind these frozen semantics in the precommit's audit plan:

- Preserve transitions with `transition_id`, `recorded_at_utc`, `obligation_id`,
  `next_due_at_utc`, `required_action_kind`, active fingerprint, and any named
  supersession/cooldown/backoff cause. Include pre-t0 commitments due after t0,
  the baseline lifecycle record, and the full continuous window thereafter.
- Each obligation resolves exactly once. An ATTEMPT must explicitly name the
  obligation, match DISCOVERY/FILING/RECONCILE action kind, and occur forward-only
  in `[due, due + tolerance]`. One attempt cannot answer another obligation by
  timestamp proximity or satisfy multiple obligations.
- Frozen audit tolerance is `3 * discovery_poll_seconds`: 180 seconds for the
  frozen 60-second policy. Bind the actual policy and audit argument; do not
  enlarge the tolerance after outcomes. The code value controls over its older
  misleading “one poll interval” comment.
- SUPERSEDED requires the explicit target obligation, a unique superseding
  transition recorded strictly BEFORE due, and a frozen authorized cause.
  Post-deadline notes cannot erase holes. An authorized cause in the ledger does
  not independently authorize a prohibited lifecycle or state intervention.
- PENDING is not completed. Frozen ordinary-action pending grace is the audit
  tolerance; RECONCILE pending grace is zero (a due reconciliation must be
  accounted at cutoff). Keep not-yet-due successor obligations as pending with
  their IDs/due times; a running persistent service need not empty its future
  schedule. No required E2/E4/E5 event may be counted while pending. A stopped
  qualifying supervisor with pending obligations cannot pass.
- Reject duplicate/missing IDs, reversed/future timestamps, wrong action kinds,
  orphan attempts or intents, missing successor, disabled/unconfigured lane,
  missing provenance and unexplained due obligations. Audit request intents,
  durable attempts and one global budget reservation per actual network request;
  no hidden retries or second requester-budget authority.
- A recorded source failure or cooldown-suppressed attempt may account for an
  obligation under V4. That accounting does not turn it into acquisition success,
  complete coverage, or successful daily-index reconciliation.

Frozen idle wake cadence is 60 seconds; the Clock's health watchdog flags
`HEARTBEAT_STALE` when age exceeds 900 seconds. Collector liveness independently
uses attempt age with allowance `max(3 * discovery_poll_seconds,
cooldown_remaining + 60)` and requires nonnegative age, configured/enabled state;
no prior attempt means `COLLECTOR_DID_NOT_RUN`, not idle health. These diagnostics
do not override the narrower due-obligation rule or prove historical continuity.

Before launch bind a restricted sampling/retention procedure for heartbeat/wake
state, service/supervisor lifecycle, scheduler and attempts, with concrete sample
cadence, maximum permitted unexplained observation gap, artifact paths/digests,
and coverage through all event boundaries. A mutable latest-heartbeat snapshot
alone cannot prove a historical no-hole interval. Sampling must be read-only to
the qualifying state and preserve evidence externally. If the supported evidence
procedure cannot prove this domain, record MISSING_OPERATIONAL_PROOF before t0;
do not add instrumentation to frozen code during this mission.

Every unexpected heartbeat or attempt gap must be reconciled to the bound
scheduler, request deadline, budget/backoff/cooldown, and lifecycle evidence.
Calendar closure, a still-running PID, a green endpoint, or absence of new filings
is not an explanation. Unexplained holes invalidate. Explainable source errors
remain source failures; service death remains service failure even when EDGAR
is closed.

## 6. Invariants and resource evidence

| Binding | Required invariant from precommit through final cutoff |
| --- | --- |
| Candidate | Exact frozen SHA/tree/input-tree; immutable clean release and fixed service view continue to resolve to it. This handoff commit never replaces the runtime candidate. |
| Fingerprint | Active == materialized == precommitted fingerprint; manifest and lifecycle/scheduler observations agree. No rematerialization to conceal drift; stale/foreign materialization accepted is invalidating. |
| Service | Repository unit, loaded fragment/drop-ins, environment inputs and canonical effective configuration retain the bound digest. Use V4 canonicalization: mutable PID/start-time/InvocationID observations are lifecycle evidence, not semantic service-digest changes. Preserve both domains. |
| Runtime/network | Interpreter real path/version, runtime dependencies, OpenSSL/TLS/trust, relevant environment, resolver/proxy and requester identity binding remain attributable to the sealed runtime/network digests. Preserve only non-secret/opaque identities in public projections. |
| State mount | Same qualifying reservoir identity and lineage, filesystem/mount/source identity and expected path topology. `/opt/quant/var` must continue to reach the bound persistent state, not an empty fallback/substitute. Preserve mount ordering/absence fail-closed proof from Gate B. Normal supported append/state evolution is allowed; out-of-band acquisition-critical edits are not. |
| Deployment authority | Exactly the precommitted fresh one-use authority is consumed once by the unique matching launch. Preserve authority digest, lifecycle chain, InvocationID, supervisor/child identities and boot provenance. No manually forged start, replay, silent authority replacement or unauthorized restart. An automatic child lifecycle event needs positive frozen-supervisor provenance and a clean obligation audit; its label alone is not permission or proof. |
| Evidence | Restricted retention binding remains valid, manifests/hash chains remain verifiable, precommit and launch records survive through Gate D. No truncation or selective window extraction. |

Capture restricted BEFORE and AFTER resource artifacts on the same host/state/
evidence roots and bind timestamps, process/InvocationID and boot correlation:
disk/free bytes, free inodes, state-root bytes, evidence-root bytes, RSS/memory,
open FDs and FD limits, relevant cgroup/process limits, journald persistence/
retention, evidence permissions/ownership and headroom verdict. Preserve Gate-B
pre-destructive and post-sanitization baselines as separate references.

The prelaunch baseline must be sealed before launch. If the service is stopped,
record process RSS/FD values as explicitly unavailable with reason, not zero or
invented live values; precommit the procedure to capture the first matching
launch's live-process baseline and compare it at the end. This later observation
is a separately bound launch artifact, not a backfilled precommit field. Blue
must accept the baseline arrangement before launch. Missing required resource
proof blocks closure. No arbitrary resource-growth threshold is introduced:
prebind measurement method/cadence and Blue review criteria, then provide
attributable before/after deltas and a restricted health/headroom verdict.

## 7. Exact prelaunch field worksheet

All `REQUIRED` values below are intentionally unpopulated in this prestage.
They must be concrete in the future sealed precommit. Unknown required field
means `PRECOMMIT_VALID = FALSE`; placeholder text is not a value. The constant
candidate/calendar values come from section 1 and must be reverified, not changed
locally. The first block preserves all authoritative prelaunch template fields.

```text
PRECOMMIT_SCHEMA = REQUIRED
PRECOMMIT_CREATED_AT_UTC = REQUIRED
CANDIDATE_SHA = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
GIT_TREE = 4d15ef6f471213ee6ab56337b555d2906ef9bf16
VERIFIED_INPUT_TREE_DIGEST = sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2
GATE_B_ARTIFACT_DIGEST = REQUIRED
TARGET_HOST_OPAQUE_ID = REQUIRED
BOOT_ID = REQUIRED
PERSISTENT_STATE_IDENTITY = REQUIRED
ACTIVE_FINGERPRINT = REQUIRED
MATERIALIZED_FINGERPRINT = REQUIRED
EFFECTIVE_SERVICE_DIGEST = REQUIRED
RUNTIME_IDENTITY_DIGEST = REQUIRED
QUALIFYING_LAUNCH_AUTHORITY_ID = REQUIRED
QUALIFYING_LAUNCH_AUTHORITY_DIGEST = REQUIRED
AUTHORITY_FRESH = TRUE (must be evidenced)
AUTHORITY_UNCONSUMED = TRUE (must be evidenced)
T0_BINDING_MODE = PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH
SOURCE_CALENDAR_AUTHORITY_VERSION = SEC_EDGAR_CALENDAR_2026 / FROZEN_V4_BLOB_b4fbd58b381e01ec882b60386cf73d4017e7db5c
ORDINARY_CLOSED_INTERVAL_EXPECTED_START_UTC = REQUIRED
ORDINARY_CLOSED_INTERVAL_EXPECTED_END_UTC = REQUIRED
NEXT_EXPECTED_LIVE_ACQUISITION_WINDOW_UTC = REQUIRED start/end and selection rule
COMPLETE_WEEKEND_CLOSURE_START_UTC = REQUIRED
COMPLETE_WEEKEND_CLOSURE_END_UTC = REQUIRED
FIRST_REQUIRED_POST_WEEKEND_ACQUISITION_WINDOW_UTC = REQUIRED start/end and selection rule
DAILY_INDEX_RECONCILIATION_RULE = oldest eligible unreconciled bound business date from Eastern bootstrap; target set and cutoff rule attached
DAILY_INDEX_SETTLE_RULE = UTC(source-date 22:00 America/New_York) + 30 elapsed hours
RESOURCE_HEALTH_BASELINE_ARTIFACT_DIGEST = REQUIRED
BLUE_ACTIVATION_ARTIFACT_DIGEST = REQUIRED
ACTIVATED_GATE_B_CONTRACT_DIGEST = REQUIRED
ACTIVATED_RUNBOOK_DIGEST = REQUIRED
GATE_B_RUN_ID = REQUIRED
GATE_B_FINAL_ARTIFACT_DIGEST = REQUIRED
TIME_AUTHORITY_SNAPSHOT_DIGEST = REQUIRED
NTP_SYNCHRONIZED = REQUIRED verified TRUE
BOOT_ID_AT_PRECOMMIT = REQUIRED
REALTIME_MONOTONIC_CORRELATION_DIGEST = REQUIRED
NETWORK_RUNTIME_BINDING_DIGEST = REQUIRED
RESOURCE_BASELINE_DIGEST = REQUIRED
EVIDENCE_RETENTION_BINDING_DIGEST = REQUIRED
SOURCE_CALENDAR_PLAN_DIGEST = REQUIRED
PRECOMMIT_CANONICAL_DIGEST = REQUIRED
PRECOMMIT_STORAGE_REFERENCE = REQUIRED
PRECOMMIT_SEALED_AT_UTC = REQUIRED
```

Bind the following supporting fields in the hashed plan/attachments before
launch. These are proposed operational field names for Blue's activated successor,
not a claim that an existing JSON schema already implements them:

```text
GATE_C_ATTEMPT_ID = REQUIRED unique identity
BLUE_GATE_B_PASS_DISPOSITION_DIGEST = REQUIRED
BLUE_QUALIFYING_LAUNCH_PREPARATION_AUTHORIZATION_DIGEST = REQUIRED
ACTIVATED_GATE_B_EVIDENCE_SCHEMA_DIGEST = REQUIRED
GATE_A_EVIDENCE_MANIFEST_DIGEST = REQUIRED
CANDIDATE_CI_IDENTITY_AND_ARTIFACT_DIGESTS = REQUIRED
CALENDAR_PLAN_REFRESHED_AT_UTC = REQUIRED
CALENDAR_TIMEZONE = America/New_York
CALENDAR_LOCAL_BOUNDARIES_WITH_OFFSETS = REQUIRED
CALENDAR_BOUND_YEARS_AND_CLOSURES = REQUIRED
LATEST_PERMITTED_LAUNCH_UTC = REQUIRED before selected ordinary closure
PRECOMMIT_EXPIRATION_RULE = REQUIRED
ACQUISITION_FIRST_OBLIGATION_SELECTION_RULE = REQUIRED for E2 and E4
QUALIFYING_STATE_BOOTSTRAP_EASTERN_DATE = REQUIRED
INITIAL_RECONCILED_AND_UNRECONCILED_STATE_DIGEST = REQUIRED
RECONCILIATION_REQUIRED_SOURCE_DATES_AND_SETTLED_AT_UTC = REQUIRED
RECONCILIATION_DYNAMIC_DUE_SET_AND_FINAL_CUTOFF_RULE = REQUIRED section 3 semantics
EVENT_COMPLETION_EVIDENCE_RULES = REQUIRED E1 through E5
OBLIGATION_AUDIT_POLICY_DIGEST = REQUIRED section 5 semantics and actual arguments
DISCOVERY_POLL_SECONDS = REQUIRED verified frozen 60
DUE_TOLERANCE_SECONDS = REQUIRED verified frozen 180
HEARTBEAT_AND_ATTEMPT_OBSERVATION_PLAN_DIGEST = REQUIRED
OBSERVATION_SAMPLE_CADENCE_AND_MAX_UNEXPLAINED_GAP = REQUIRED
LIFECYCLE_AND_LAUNCH_TIMESTAMP_SOURCE_BINDING = REQUIRED
STATE_MOUNT_TOPOLOGY_AND_INVENTORY_DIGEST = REQUIRED
SERVICE_DEFINITION_AND_EFFECTIVE_CONFIGURATION_BINDING = REQUIRED
GLOBAL_REQUESTER_BUDGET_AUTHORITY_BINDING = REQUIRED
RESOURCE_MEASUREMENT_AND_LIVE_BASELINE_PLAN_DIGEST = REQUIRED
RESOURCE_HEALTH_REVIEW_CRITERIA = REQUIRED
EVIDENCE_ROOT_MANIFEST_RETENTION_AND_ACCESS_BINDING = REQUIRED
INVALIDATION_AND_BLUE_ESCALATION_RULE = REQUIRED section 8 semantics
PUBLIC_FIREWALL_PROJECTION_RULE = REQUIRED section 9 semantics
```

Cross-check `GATE_B_ARTIFACT_DIGEST` and `GATE_B_FINAL_ARTIFACT_DIGEST` against
the same accepted final artifact, or explicitly identify their distinct canonical
objects in the manifest. Likewise identify whether the resource digest fields
reference the same baseline or distinct Gate-B/prelaunch artifacts; never leave
alias semantics ambiguous. BOOT_ID and BOOT_ID_AT_PRECOMMIT must match the fresh
time snapshot. Hash canonical payloads/attachments with the activated contract's
algorithm; keep the digest/seal envelope outside its own hashed payload to avoid
self-reference. Every digest must resolve to retained evidence.

Do NOT prefill observed launch time, PID or InvocationID. After launch, create a
separate retained artifact containing every authoritative launch field:
`OBSERVED_LAUNCH_UTC`, `SYSTEMD_INVOCATION_ID`, `SUPERVISOR_ID`, `MAIN_PID`,
`OBSERVED_BOOT_ID`, `CONSUMED_AUTHORITY_ID`, `OBSERVED_ACTIVE_FINGERPRINT`,
`OBSERVED_MATERIALIZED_FINGERPRINT`, `OBSERVED_EFFECTIVE_SERVICE_DIGEST`,
`OBSERVED_PERSISTENT_STATE_IDENTITY`, `PRECOMMIT_CANONICAL_DIGEST`, authoritative
timestamp source and monotonic correlation/reference if available. Verify runtime
identity against its binding too. Only verified unique launch, matching identities,
exactly-once authority consumption and unambiguous provenance permit Blue's t0
acceptance. Shell/chat time or filesystem mtime alone cannot supply that timestamp.

## 8. Invalidation, reset and incomplete events

Before launch, unexplained wall-clock step, NTP loss, boot change, or time-authority
change after sealing invalidates the precommit: `NO_T0`; refresh time authority
and seal a new precommit. No late edits to the old seal.

During Gate C, any of the following invalidates/resets the attempt:

- Acquisition-critical fingerprint change, active/materialized mismatch, or
  stale/foreign materialization accepted.
- Unbound service/config/runtime/network identity change, lost/substituted state
  mount, unauthorized acquisition-critical durable-state edit, deployment or
  lifecycle replacement, or integrity latch.
- Unexplained due obligation, heartbeat/attempt hole, ambiguous time/lifecycle
  provenance, source failure relabeled normal silence, or visibility/firewall leak.
- Loss of required precommit/launch evidence, or evidence loss/tampering that
  prevents proof of the continuous interval.

Preserve and close the interval as FAIL/INVALIDATED, classify the defect or
missing proof, and return to Blue. Do not move t0 forward inside it, erase rows,
rematerialize, restart to obtain favorable evidence, or reuse consumed authority.
A new attempt needs Blue disposition, re-established relevant entrance bindings,
a refreshed prospective calendar plan, a new precommit and a new unique launch.
A changed candidate cannot inherit Gate B silently.

An accounted source error is not automatically an unexplained service hole, but
it cannot satisfy the required successful event. Maintain the original evidence
and frozen failure/backoff semantics; unresolved coverage/index/resource proof
prevents Gate-D acceptance. Report missed event-window obligations to Blue rather
than inventing replacement windows. Read-only audits are permissible only if they
cannot mutate qualifying runtime/state; other lanes must remain isolated.

## 9. Gate-D reception package and return to Blue

After all bound events actually occur, retain one canonical restricted manifest
binding:

1. Exact candidate SHA/tree/input-tree and exact CI identities/artifacts; Gate-A
   repository/fault/calendar evidence and Blue disposition, without transferring
   proof to this documentation SHA.
2. Activated Gate-B contract/runbook/schema and activation, run ID, final accepted
   host artifact, schema validation, sanitization/state lineage and Blue PASS.
3. Sealed precommit, calendar plan and all attachment digests, next-launch authority,
   launch record, timestamp provenance and all identity/one-use verification results.
4. Full interval from accepted t0 through declared final evidence cutoff; each
   E1–E5 expected-versus-observed verdict with restricted evidence references;
   all applicable source dates, settled-at times and reconciliation/coverage verdicts.
5. Complete scheduler/attempt/intent/budget and lifecycle/deployment chain; final
   one-obligation-to-one-resolution audit, boundary-crossing obligations, named
   pending future successors, no unexplained holes, no open coverage gaps and
   no integrity latch. An `accountable` audit alone does not prove calendar,
   heartbeat, resource, or event completion domains.
6. Runtime/interpreter/OpenSSL/network identities, service/configuration digest,
   active/materialized fingerprint equality and state-mount continuity throughout.
7. Restricted resource-health before/after artifacts and verdicts, first-launch
   live baseline where prebound, time-authority continuity, retention/hash checks,
   and explicit classification/disposition of every failure or missing proof.

Missing or mismatched proof domain means fail closed at Gate D. Only a separate
Blue disposition can declare qualification. Thereafter the amendment requires
`P0_POST_QUALIFICATION_SURVEILLANCE = ACTIVE`; this document does not activate it.

Public handoffs contain opaque digests and safe verdicts only: no requester
secrets, filings/accessions/locators/raw SEC content, filing counts, per-event
journal dumps, or count proxies. The detailed obligation/resource evidence stays
restricted; “non-identifying” event rows can still reveal volume.

## 10. Delivery validation and disposition

This delivery is documentation only. Calendar arithmetic and required-template
field coverage are checked offline; frozen code/tests were inspected, not altered.
Validation passed: all 44 authoritative prelaunch fields are present; local
authority links resolve; example UTC boundaries and all three 30h settlement
calculations match; the three named frozen calendar/collector/test blobs match
the candidate tree. The staged diff passes `git diff --cached --check`.
No live qualification, host readiness, Gate B PASS, t0, Gate C PASS or P0
qualification is claimed. Future host-specific worksheet values remain unfilled
by design and are mandatory blockers to execution until Blue binds them.

```text
GATE_C_EVENT_PLAN_PRESTAGE = READY_FOR_BLUE_REVIEW
GATE_B = NOT_STARTED (dispatch authority; no new execution evidence in this lane)
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
CONTROL = RETURN_TO_BLUE
```

Blue's next action is to review this Lane-D template with the other preparation
lanes. Only after future Gate-B PASS may Blue refresh and seal concrete prelaunch
values. Builder stops at this handoff.
