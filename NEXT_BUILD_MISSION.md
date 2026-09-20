# Current Build / Mission Router

This file is intentionally a **router**, not a frozen mission specification.

Do not use historical content from this path to infer the current task.

## Authority

Read, in order:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
3. `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`
4. `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md`
5. the exact branch-specific mission/handoff referenced by those current documents

Resolve the live HEAD of `blue/master-v2-2026-09-20` before acting.

## Current routing at last update

Blue currently owns multiple explicit workstreams rather than one global Builder mission:

- Gate A v4 effective-unit-digest correction: Builder delivery / Blue reception / independent Astra review;
- P14D hybrid qualification challenge: governance-method review, amendment still non-authoritative;
- repository hygiene: 35 delete-ready refs physically pending plus default-branch migration pending;
- target-host qualification: paused until a corrected independently accepted candidate exists;
- Product integration: paused, with canonical Forward/Economic leaves preserved.

Safety state remains:

- `t0 = NOT DECLARED`
- `P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`
- `P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `PRODUCT_INTEGRATION = PAUSED`

This router must never be used as proof that a particular branch, CI run, candidate or gate is current. The current governance index and exact GitHub state control.
