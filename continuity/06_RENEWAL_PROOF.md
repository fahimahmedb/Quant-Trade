# Bounded renewal proof

## Existing behavior reused

The current Research OS already owns queue refill, source-aware preflight and bounded task derivation. It enforces:

- at most one new task per refill;
- a configured maximum of 12 issued tasks per frontier;
- globally empty queue before refill;
- no producer execution in the refill wake;
- no recursive refill in the same wake;
- deterministic derivation keys;
- duplicate derivation rejection;
- source-aware bounded NOOP states;
- closed economic/prospective/capital/live authority.

Those mechanics remain the only operational scheduler path.

## Missing semantic

The base did not expose a predecessor-cohort → successor-cohort scientific accounting contract that explicitly preserves cumulative exposure, prevents budget reset and charges a new scientific epoch after post-outcome policy changes.

CP06 therefore adds a pure fixed/preregistered policy membrane, `renewal_policy.py`. It creates no task and is explicitly `RENEWAL_OPERATIONALLY_ENABLED=FALSE`.

## Budget law

No new scientific budget was invented. The isolated witness binds to existing configured limits:

- `max_new_tasks_per_refill=1`;
- `max_issued_per_frontier=12`.

There is no separate authorized variant budget, so the witness records `NO_NEW_VARIANT_BUDGET_AUTHORIZED`. Validation capacity is explicitly reused from the existing Control Plane and cannot be increased by this contract.

Any successor change to root budget, variant budget, cumulative program budget or validation capacity fails as `OWNER_POLICY_DECISION_REQUIRED`.

## Renewal law proven by focused tests

- same scientific root/variant remains the same across cohort IDs;
- cumulative exposure is a monotone superset of predecessor exposure;
- a new cohort cannot count as independent confirmation;
- repeated evaluation of the same successor is deterministic and keeps the same idempotency key;
- stale policy hash fails closed;
- no qualified source version produces bounded `PARK` and no scheduler mutation;
- authority remains closed;
- a policy change after charged outcome exposure requires a new `SCIENTIFIC_EPOCH_ID` and an explicit triggering information set;
- the new epoch retains prior exposure and still cannot count as independent confirmation.

## Fixed first policy

The first policy is `FIXED_PREREGISTERED`. No adaptive productivity optimizer exists in this mission.

The machine-readable isolated witness is:

`continuity/evidence/RENEWAL_WITNESS.json`

It is a mechanics witness only. Fixture source identity does not enter production science or activate renewal.

## Gate 4

`FRONTIER_RENEWAL_STATUS=BOUNDED_SUCCESSOR_CONTRACT_BUILT_NOT_ACTIVATED`

`RENEWAL_OPERATIONALLY_ENABLED=FALSE`

`BUDGET_INCREASE=FALSE`

`AUTHORITY_CHANGED=FALSE`

`OUTCOME_ACCESSED=FALSE`

`SYNTHETIC_PRODUCTION_CONTAMINATION=FALSE` pending final exact-head execution of the isolated test suite.
