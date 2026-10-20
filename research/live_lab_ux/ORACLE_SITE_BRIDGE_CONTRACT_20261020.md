# Oracle -> Live Lab Site Bridge Contract

Date: 2026-10-20
Status: FRONTEND CONTRACT READY / PRODUCTION PRINCIPAL UNBOUND

## Objective

Project real Oracle Research OS activity into the existing native Live Lab transport without making Oracle depend on Live Lab availability.

Canonical visualization path remains:

`Oracle semantic event -> authenticated Site ingress -> D1 -> public SSE -> LiveEventAdapter -> mapper -> reducer -> scene`

GitHub remains scientific/durable project memory. It is not the live UI polling transport.

## Architectural rule: projection must not be in the critical research path

A Site outage, credential failure, D1 issue or SSE issue MUST NOT block, retry, roll back or scientifically alter an Oracle task.

Recommended runtime shape:

`Oracle worker -> local bounded UI outbox -> independent live-lab emitter -> authenticated Site ingress`

The emitter is a projection process, not a research authority.

### Failure semantics

- Research completion does not wait for Site acknowledgement.
- Emitter retry state is operational telemetry only.
- Missing UI delivery must never mutate research outcome, validation or task status.
- UI delivery can be reconciled from the bounded local outbox, but replay must keep the same event ID/sequence so D1/SSE/reducer idempotency suppresses duplicate business animation.

## Required Oracle-side principal

Use a dedicated production principal, distinct from historical probe/canary identities.

Suggested semantic identity only (actual credential/endpoint is Site-owned):

- worker identity: actual Oracle worker identity from runtime config;
- UI role: `researcher` only when emitted explicitly by the Oracle projection contract;
- UI label: `Oracle`;
- scope: `ORACLE_RESEARCH_PRE_OUTCOME`.

No credential is stored in GitHub.

## Event lifecycle

### 1. ACTION_STARTED

Emit only after Oracle has actually claimed a task/stage and real work is beginning.

For cognitive candidate generation:

- `ui_activity = hypothesis-generation`
- progress remains unknown unless there is an objectively known total;
- no economic result fields;
- no alpha/PnL/return language.

### 2. WORKER_HEARTBEAT

Independent of slow GPT-OSS inference.

Heartbeat proves presence/lease only.

It MUST NOT:

- create an actor from nothing in the client;
- start/restart a gesture;
- update business progress;
- claim research completion.

### 3. ACTION_COMPLETED

Emit only after the underlying result is durably persisted by Oracle.

Completion must carry bounded effect proof:

- exit/status code where meaningful;
- durable output SHA-256 or equivalent content-addressed artifact identity.

The Live Lab may display the completion fact; it must not infer economic success from it.

### 4. SESSION_ENDED

Terminates UI activity without inventing additional work.

## Packet contract

The historical production canary proved this native ingress family:

- `worker_id`
- `session_id`
- `lease_id`
- `session_generation`
- `sequence`
- `event_id`
- `scope`
- `type`
- `action_id`
- `label`
- `detail`
- `ui_activity`
- optional completion `effect_proof`

The 2026-10-20 frontend extension additionally supports explicit authenticated:

- `ui_role`
- `ui_label`

The Site ingress must preserve those fields into the native stored/SSE event payload. It must not derive them from `worker_id`.

Reference builder:

`research/live_lab_ux/adapters/oracle-native-contract.js`

## Site-side changes required

The deployed Site source is not present in the Quant-Trade Git repository used by this workstream. Therefore the following are REQUIRED but NOT YET CLAIMED IMPLEMENTED:

1. create/configure a dedicated Oracle ingress principal;
2. accept the bounded Oracle semantic fields above;
3. preserve `ui_activity`, `ui_role`, `ui_label` through D1/SSE;
4. retain existing session/generation/lease/sequence validation and duplicate suppression;
5. keep anonymous ingress rejected;
6. keep public SSE read projection separate from authenticated ingress;
7. never expose Oracle credential material to the browser.

Do not invent the ingress URL or credential until the Site runtime exposes them.

## Runtime-side changes required

The active Oracle runtime is maintained on a different branch/workstream. The Live Lab branch must not concurrently mutate it.

Codex/Oracle workstream should implement the smallest projection hook/outbox that can provide:

- task/stage identity;
- actual start timestamp;
- semantic UI activity;
- stable worker/session/generation/lease identity;
- independent heartbeat;
- durable completion artifact hash;
- idempotent event sequence.

Prefer an outbox + independent sender rather than a synchronous HTTP request inside the scientific stage execution.

## End-to-end qualification

`LIVE_LAB_ORACLE_DESKTOP_QUALIFIED` requires one real benign Oracle stage to prove:

1. real Oracle claim/work start;
2. Oracle outbox event exists;
3. dedicated emitter authenticates to Site;
4. Site accepts event;
5. D1 persists it;
6. public SSE emits it;
7. browser mapper/reducer creates explicit Oracle actor;
8. `hypothesis-generation` produces only its allowed non-economic gesture;
9. independent heartbeat creates no additional business animation;
10. durable completion emits the same lineage with effect proof;
11. actor stops work gesture;
12. reload/snapshot reconstructs state without replaying motion;
13. duplicate/retry does not create another transition;
14. `REAL_CAPITAL_AUTHORIZED = FALSE`;
15. `LIVE_TRADING_AUTHORIZED = FALSE`.

Until all 15 are evidenced, use narrower statuses such as `FRONTEND_CONTRACT_QUALIFIED` or `ORACLE_SITE_TRANSPORT_PENDING`.
