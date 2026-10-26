# P0 Acquisition-Critical Fingerprint V1

**Status:** FROZEN INPUT SET / IMPLEMENTATION REQUIRED BEFORE `t0`  
**Authority:** Blue Team / Mission Control  
**Parent:** `BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2`

## 1. Immediate error prevented

This contract prevents an acquisition-semantic change from crossing the fourteen-day observation
window without resetting `t0`.

The concrete failure class is broader than a changed polling interval. Retry behavior, timeouts,
response/error classification, pagination, continuity, backlog draining, restart behavior or
launcher policy can all change the expected sequence of acquisition actions while leaving
`discovery_poll_seconds` unchanged.

Therefore the acquisition-critical fingerprint is not a configuration-file hash.

The current implementation audit has identified the first concrete objects in this program that are
classified for the continuous-service qualification path as:

`BLOCKS_CAPTURE_INTEGRITY`.

They are:

- `HIDDEN_TRANSPORT_RETRY`: an actual SEC HTTP request can occur without its own traffic-budget
  reservation and durable attempt identity;
- `INCOMPLETE_CRITICAL_POLICY_SERIALIZATION`: two effective acquisition policies can currently
  differ while producing the same candidate fingerprint input.

These blockers do not revoke `P0_RAW_CAPTURE_OPERATIONAL = TRUE`. They block authorization of the
continuous-service observation clock `t0`, because they make the property being observed
inauditable or misstate the real request budget.

## 2. Fingerprint object

Builder must materialize a deterministic canonical manifest and compute:

`ACQUISITION_CRITICAL_FINGERPRINT = sha256(canonical_json(manifest_v1))`

The manifest must contain:

1. code-semantic inputs;
2. effective runtime acquisition policy;
3. external launcher/supervisor semantics that can affect service timing/restart;
4. the fingerprint schema/version itself.

The exact manifest used for the active observation window is persisted before `t0`.

Changing any manifest member changes the fingerprint and resets `t0`.

## 3. Code-semantic inputs — mandatory V1 roots

At minimum the fingerprint must cover the exact code that implements the following behavior.

### SEC acquisition modules

- `src/quant/dataplane/sec/policy.py`
- `src/quant/dataplane/sec/budget.py`
- `src/quant/dataplane/sec/transport.py`
- `src/quant/dataplane/sec/discovery.py`
- `src/quant/dataplane/sec/collector.py`
- `src/quant/dataplane/sec/store.py`
- `src/quant/dataplane/sec/visibility.py`
- `src/quant/dataplane/sec/timebase.py`

These roots cover, among other things:

- request spacing and concurrency;
- connect/read/whole-request deadlines;
- retry and reconnect behavior;
- backoff/cooldown and `Retry-After` handling;
- HTTP/transport failure classification;
- complete/incomplete response classification;
- discovery validation and invalid-discovery semantics;
- pagination and page-budget semantics;
- cursor/continuity and `NO_NEW_DATA` semantics;
- backlog drain behavior;
- raw-object/envelope/attempt durability;
- restart/resume state;
- visibility-firewall behavior;
- the clock source used for deadlines and due-state calculations.

### Control Plane integration

The acquisition-specific scheduling semantics currently live inside the mixed-purpose
`src/quant/clock.py`, including at least the ordering in `tick()`, `_run_due_capture()` and
`_capture_step()`.

Before `t0`, Builder should isolate this acquisition scheduling logic into a dedicated module so
that unrelated Research/Desk changes do not reset the observation window.

Until that isolation is complete, the conservative V1 rule is:

`src/quant/clock.py` is fingerprint-critical in full.

The membership may be narrowed only before the first qualifying `t0`, never retrospectively after
an incident or after observation has begun.

## 4. Effective runtime policy — mandatory V1 values

The fingerprint must include canonical values for every effective runtime setting that can affect
request timing, request shape, response acceptance, backlog drain or source behavior.

At minimum:

- resolved discovery host / endpoint class and query construction version;
- `discovery_poll_seconds`;
- `max_concurrency`;
- `max_requests_per_second`;
- `allow_burst`;
- `connect_timeout_seconds`;
- `read_timeout_seconds`;
- `total_deadline_seconds`;
- `backoff_schedule_seconds`;
- `jitter_ratio`;
- `rate_limit_cooldown_seconds`;
- `forbidden_cooldown_seconds`;
- `discovery_page_size`;
- `max_discovery_pages_per_poll`;
- `filings_per_drain`;
- `accept_encoding`;
- `max_response_bytes`;
- requester-identity digest or equivalent non-plaintext stable identity binding;
- any future parameter that can change scheduler, retry, discovery, coverage, acknowledgement or
  acquisition-firewall semantics.

The current `SecAccessPolicy.to_dict()` is not sufficient as the fingerprint source because it
does not presently expose at least `filings_per_drain`, `accept_encoding` and
`max_response_bytes`.

Builder must create a dedicated complete canonical fingerprint serialization rather than reusing a
telemetry serializer whose purpose is different.

### Policy-field completeness invariant

The canonical serializer must be complete by construction rather than by a hand-maintained list
with no coverage check.

For every field returned by `dataclasses.fields(SecAccessPolicy)`, exactly one classification must
exist:

- `INCLUDE_CANONICAL`: serialize the effective value directly in canonical form;
- `TRANSFORM_CANONICAL`: serialize a deterministic semantic transform, such as a non-plaintext
  stable digest of requester identity;
- `EXPLICITLY_NONCRITICAL`: permitted only with a frozen rationale showing that the field cannot
  alter request timing, request shape, source identity, response acceptance, retry/failure
  classification, backlog drain, discovery/coverage or firewall semantics.

The implementation test must assert:

`POLICY_FIELD_SET == INCLUDE_CANONICAL ∪ TRANSFORM_CANONICAL ∪ EXPLICITLY_NONCRITICAL`

and that those three sets are pairwise disjoint.

Adding a new `SecAccessPolicy` dataclass field without classifying it must fail tests and prevent
fingerprint generation. This is the required defense against a future policy field silently
escaping the fingerprint.

For V1, `user_agent` must be transformed to a stable non-plaintext identity binding rather than
omitted. Any source/policy metadata field that is not runtime-critical must still be explicitly
classified; silent omission is forbidden.

## 5. External launcher / supervisor input

The runtime artifact or configuration that controls process/service launch, automatic restart,
deployment replacement and restart delay is fingerprint-critical whenever it can alter the expected
acquisition timeline.

The manifest therefore records the digest/version of the active supervisor/service definition and
its effective restart policy.

Lifecycle cause remains a separate durable event supplied by that supervisor:

- `SCHEDULED_START`
- `AUTOMATIC_RESTART_AFTER_FAILURE`
- `DEPLOYMENT_RESTART`
- `MANUAL_START`

## 6. No hidden network retries

Before `t0`, the implementation must satisfy:

`ONE_BUDGET_RESERVATION == ONE_NETWORK_REQUEST_ATTEMPT == ONE_AUDITABLE_ATTEMPT_ID`

A reconnect may occur without semantic consequence, but a second HTTP request may not be emitted
inside a transport call under the first request's limiter reservation / attempt record.

Current implementation audit at the parent frontier found an internal fresh-connection retry in
`transport.py` after certain request failures. That retry is not separately reserved/journaled by
`collector._request()`.

Builder must either:

1. **preferred:** remove the hidden HTTP retry and let the collector's normal failure/backoff path
   schedule the next request; or
2. route every actual retry through the Control Plane / collector request path with:
   - a fresh traffic-budget reservation;
   - a distinct durable attempt id;
   - an explicit scheduler transition / retry cause;
   - a reconstructible `next_due_at` or equivalent due-state transition;
   - the resulting backoff/cooldown state.

Option 2 is not satisfied by adding a second attempt record after the fact. The retry must be part of
the prospective scheduler state from which the retrospective audit derives the expected sequence.

The hidden retry is also a request-budget defect: a limiter that counts reservations while the
transport can emit more requests than reservations understates real SEC traffic and increases the
risk of source throttling/blocking and an irreversible acquisition gap.

The qualifying observation window cannot start while an actual SEC request can occur outside the
auditable budget/journal path.

## 7. Change classification

A change to any V1 manifest member is acquisition-critical by construction and resets `t0`.

Examples that necessarily reset `t0`:

- changing timeout values or timeout implementation;
- changing internal retry/reconnect logic in a way that can emit requests;
- changing which exception/status maps to transient/permanent/invalid discovery;
- changing `Retry-After`, 403, 429 or 5xx handling;
- changing page-budget, cursor or continuity logic;
- changing `NO_NEW_DATA` qualification;
- changing backlog drain precedence or poll scheduling;
- changing supervisor restart timing;
- changing raw acknowledgement/cursor-advance ordering;
- changing the P0 visibility-firewall implementation.

Manifest, gap-ledger, backfill, parser/normalizer and downstream scientific work remain outside this
fingerprint only when they cannot alter any of the behavior above.

## 8. Before-`t0` acceptance

The fourteen-day clock must not begin until Builder demonstrates all of:

- deterministic manifest generation;
- stable fingerprint across two identical clean builds/runs;
- mutation test: changing each representative critical class changes the fingerprint;
- non-critical mutation test: a downstream-only change does not change the fingerprint;
- effective runtime values in the manifest match the service actually launched;
- supervisor/service-definition digest is bound;
- no hidden network retry can bypass budget/journal accounting;
- the implementation proves one budget reservation per actual HTTP request and one durable attempt
  identity per actual HTTP request;
- if any retry remains, the scheduler journal prospectively explains why and when that retry became
  due;
- the policy-field completeness invariant is tested against `dataclasses.fields(SecAccessPolicy)`
  so an added field cannot be silently omitted;
- the fingerprint is emitted with scheduler/lifecycle transitions used by the retrospective audit.

Only after those conditions are met may Blue record the qualifying `t0`.
