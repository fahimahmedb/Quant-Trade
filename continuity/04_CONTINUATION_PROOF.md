# Durable continuation proof

## Existing equivalent behavior searched first

The exact target already has strong continuation mechanics owned by Control Plane / Oracle:

- fresh immutable Git snapshots and compare-and-swap publication;
- durable READY/CLAIMED task state with lease generations;
- stage artifacts bound to completed-stage hashes;
- atomic publication of stage artifact + event + receipt + task transition;
- direct child-task materialization for validation handoff;
- optional integration child-task materialization only after explicit authorization and cleared blockers;
- idempotent frontier derivation keys and duplicate derivation rejection.

These existing mechanics remain authoritative for task mutation. They were not replaced.

## Proven missing semantic

The base does not expose a generic contract that proves **every declared continuation obligation** has exactly one durable closure when the correct result is not a child task. In particular, a lawful unresolved-authority stop needs a durable closure with reason, scope, missing condition and observable reopen predicate rather than a fabricated historical task or receipt.

Therefore CP04 adds only `research/research_os/continuation.py`, a validation membrane. It has no scheduler mutation API and no scientific-decision API.

## Closure law implemented

For every declared `OBLIGATION_ID`, exactly one closure must validate as one of:

1. `CHILD_TASK` — durable child task already decided elsewhere;
2. `EXISTING_CHILD_REF` — durable reference to an equivalent existing child;
3. `BLOCK`;
4. `PARK`;
5. `TERMINAL`.

Zero closures fail as `ORPHANED_CONTINUATION_OBLIGATION`. More than one closure fails as `MULTIPLE_DURABLE_CLOSURES`.

`BLOCK` and `PARK` require the mission-specified fields: obligation, parent, owner, reason, claim scope, missing condition, observable reopen predicate, authority scope, data scope, source scope, creation time and idempotency key. Their content is hash-bound.

A reopen creates a new event referencing the original closure hash. The historical block/park is not rewritten.

## Non-powers preserved

The continuation contract cannot:

- grant authority;
- select or retune an experiment;
- change source semantics;
- create a Candidate;
- reset exposure;
- make a scientific verdict;
- create a scheduler or Control Plane;
- write runtime tasks by itself.

## Gate assessment

`DURABLE_CONTINUATION_BASE_MECHANICS=REUSED`

`GENERIC_OBLIGATION_CLOSURE_CONTRACT=PORT_MINIMAL_NEW_THIN_CONTRACT`

`COMPETING_TASK_MUTATION_OWNER_CREATED=FALSE`

`AUTHORITY_EXPANDED=FALSE`

`OUTCOME_ACCESSED=FALSE`

Focused qualification is provided by `tests/test_verified_continuation_contract.py`; exact-head execution remains pending final qualification.
