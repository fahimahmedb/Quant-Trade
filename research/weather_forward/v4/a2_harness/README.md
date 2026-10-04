# Weather V4 A2 dedicated offline harness

## Authority and current governance state

This static repair is bounded by Owner repair authority:

`08b40c41bdadb05b572a88fc1279310c436d32f7`

and addresses the exact Astra audit:

`07405b3c20168014993f1616c19e7d47f5e2a41f`

against audited Builder target:

`649be59e69d8e0724d61352cc76abcac7f3f588e`

The original construction authority remains documentary construction authority only:

`37e3b25f17a7c5d3b3bc8d37df730aa988585b6c`

`CONSTRUCTION_AUTHORITY != EXECUTION_POLICY_AUTHORITY`

`IMPLEMENTATION_COMPLETE != CONTROL_EFFECTIVENESS_VERIFIED`

`IMPLEMENTATION_COMPLETE != A2_EXECUTION_AUTHORIZED`

`IMPLEMENTATION_COMPLETE != A2_HARNESS_APPROVED`

`A2_FIXTURE_GENERATION_AUTHORIZED = FALSE`

`A2_FIXTURE_TESTING_AUTHORIZED = FALSE`

`A2_EXECUTION_AUTHORIZED = FALSE`

`ECONOMIC_AUTHORITY = 0`

`CAPTURE_AUTHORIZATION = NONE`

`DATA_T0 = NOT_DECLARED`

`EXPERIMENT_T0 = NOT_DECLARED`

## D1 — independently anchored trusted execution-policy root

`CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY = NONE`

`CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT = NONE`

`NO_TRUSTED_EXECUTION_POLICY_ROOT = DENY_ALL_PERMIT_RELEASE_ADMISSION_PATHS`

`trusted_root.py` is the static trust-anchor boundary.  It intentionally returns
`None` and exposes no caller-supplied active-root setter.  `HarnessPolicy`
remains a caller-supplied contract object, but it is not a root of trust.
Future permissive use would require a separately authorized source-level trusted
root carrying an execution-policy authority SHA and exact `HarnessPolicy`
identity.  The trusted root must bind the construction authority, harness
identity/version and deterministic policy identity.  Without that independent
root, input read, fixture admission, output release and resource-boundary
permission all fail closed.

The same caller supplying manifests, bindings, roles or action authorizations
cannot make the current trusted-root resolver return a permissive root merely by
coordinating those objects.

## Exact manifests preserved

Input and output manifests retain deterministic SHA-256 identities over
canonical JSON.  Every material manifest dataclass field is represented in its
canonical identity.  Set-like tuples are sorted for canonicalization while
duplicate entries are not silently deduplicated.

`HarnessPolicy` carries the exact expected input and output manifest identities.
A structural identity mismatch fails closed.

## D2 — exact fixture provenance / lineage contract

`FixtureProvenance` has a deterministic SHA-256 structural identity covering:

- fixture ID;
- construction input classes;
- generator identity;
- generator version;
- lineage references;
- reproducibility metadata keys and values;
- contamination state;
- admissibility state.

`FixtureProvenanceContract` supplies future exact expected generator/fixture
identity, exact construction classes, exact lineage set, required and allowed
reproducibility keys, and the exact expected provenance digest.  Validation
fails closed on missing/ambiguous values, duplicate lineage, duplicate metadata
keys, missing required keys, forbidden unexpected keys, wrong generator,
wrong construction classes, unknown/contaminated state, non-admissibility or
digest mismatch.

`CURRENT_APPROVED_FIXTURE_PROVENANCE_IDENTITY = NONE`

The current `HarnessPolicy` may therefore carry no fixture provenance contract;
fixture admission remains non-permissive.  No fixture or sample fixture is
contained here.

## D3 — exact recipient authorization

A role allowlist in `OutputManifest` is necessary but not sufficient.
`HarnessPolicy.permitted_recipient_actor_roles` is the future exact
actor-ID-to-role authorization map and is covered by the deterministic
`HarnessPolicy` identity that a future trusted root must bind.

Current approved recipient identities do not exist:

`CURRENT_APPROVED_RECIPIENT_ACTOR_IDS = NONE`

`CURRENT_APPROVED_ACTOR_ROLE_MAP = NONE`

Therefore an arbitrary actor with a valid role cannot satisfy release.
Cumulative disclosure remains an independent necessary condition and cannot
substitute for exact recipient authorization.

Exact cumulative-disclosure matching remains:

`output_id + recipient_actor_id + recipient_role`

Global `BLOCKED` state keeps precedence over `UNRESOLVED` and `CLEAR`; empty
history remains `UNRESOLVED`.

## D4 — minimum release independence

For outputs where `release_approval_requirement = REQUIRED`, the enforced
minimum rule is:

`RELEASE_ACTOR_ID_MUST_DIFFER_FROM_RECIPIENT_ACTOR_ID`

The release actor must additionally satisfy exact actor ID, `RELEASE_APPROVER`
role, `RELEASE_OUTPUT` action, execution-policy authority identity and
`AUTHORIZED` authorization state.  The identity-separation rule is additive;
it does not replace any of those checks or any future stronger Owner rule.

## D5 — exact logging attribution

Each `LogRecord` can bind:

- exact actor ID and role;
- exact authorization ID and authorization authority identity;
- construction authority identity;
- execution-policy authority identity when one exists;
- exact attempted action;
- exact target kind and target ID;
- exact manifest/provenance structural identity;
- permit/deny state;
- quarantine state;
- release state;
- incident ID when applicable;
- cumulative-disclosure state when applicable;
- exact recipient actor ID and role for release.

Two actors sharing one role are therefore distinguishable by `actor_id`.
Logging remains only an immutable-value/in-memory functional interface.  It is
not cryptographically immutable, deployed immutable storage or tamper-proof.

## D5 — logging required for completion

Action APIs use atomic evaluate-and-log semantics.  Input read, fixture
admission and output release take an immutable `StructuredAuditLog` plus a
unique exact log record ID and return `LoggedActionResult`.

The harness first computes only a private eligibility assessment.  No public
final `PERMIT` / `AUTHORIZED` action decision is produced from that assessment.
The exact log record is appended and acknowledged first.  Only after successful
append acknowledgement is the final `HarnessDecision` constructed with
`completion_state = COMPLETED` and, where eligible, `PERMIT` / `AUTHORIZED`.

Missing, ambiguous or duplicate required log record identity, or failed append
acknowledgement, yields:

`permit_or_deny_state = DENY`

`release_state = BLOCKED`

`completion_state = NOT_COMPLETED`

`stop_reason = LOGGING_REQUIRED`

There is no separate optional `append_log_record()` permission path.

## Fail-closed properties preserved

The static contract preserves:

- exact input and output manifest canonicalization;
- exact recipient cumulative-disclosure matching;
- `BLOCKED` disclosure precedence;
- empty disclosure history = `UNRESOLVED`;
- actor mismatch denial;
- role mismatch denial;
- action mismatch denial;
- execution-authority mismatch denial;
- authorization-state mismatch denial;
- unresolved visibility denial;
- unresolved permission denial;
- unknown/prohibited input-class denial;
- output exportability restrictions;
- quarantine restrictions;
- efficacy-leakage restrictions;
- resource-boundary fail-closed behavior;
- no permissive fallback.

The implementation uses only Python standard-library modules and has no wall
clock, randomness, environment-derived authority, network calls, endpoint
queries, credential management, database integration, filesystem writes,
collector logic, source/station/city/model selection, economic scoring,
backtesting, PnL, paper trading or live trading.

## Construction / repair non-actions

During this repair mission:

- no harness source was executed or imported;
- no tests, pytest, syntax checks, linters, type checkers or CI were run;
- no fixture content was opened;
- no fixture or sample fixture was created;
- no real data was accessed;
- no real operational or efficacy metadata was accessed;
- no endpoint was queried;
- no credential was used;
- no `src/` file was changed;
- the historical Gate-B runner was not changed;
- no economic validation or trading activity occurred.

Successful source repair means only:

`ASTRA_D1_D5_STATIC_REPAIR_IMPLEMENTATION_COMPLETE`

It does not mean runtime verification, control effectiveness, harness approval,
execution readiness, fixture approval or economic validation.
