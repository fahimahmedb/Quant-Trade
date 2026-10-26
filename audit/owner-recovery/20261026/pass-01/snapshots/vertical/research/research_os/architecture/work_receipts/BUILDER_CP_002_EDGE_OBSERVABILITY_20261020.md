# BUILDER CHECKPOINT 002 — V2 ECONOMIC EDGE OBSERVABILITY

CHECKPOINT_ID: BUILDER_CP_002_EDGE_OBSERVABILITY_20261020
TASK_CAPABILITY: Fail-closed machine-readable projection of existing V2 research truth
BUILDER_ROLE: V2 Forward Builder / Quant Engineer
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: 721e73901df4075da4f2e53c37923de47c2fa5f3
CURRENT_BUILDER_HEAD_DESCRIBED: c9331e86c88dbebcdbd586d77c3464fda694ce28
FRESH_OBSERVED_ORACLE_V2_HEAD: 7e2a6de231939f4b559a63fac3ea7eee28d81e1f
UPSTREAM_RELATED_BRANCHES:
- builder/oracle-v2-core-20261020
- audit/forensic-checkpoint-20261019

## Objective

Close the bounded residual identified by CP001: owner-facing economic-research observability without adding a second state store, without modifying the Site, and without consuming outcomes.

## North-Star property advanced

- factual owner observability;
- ability to see what is attempted, blocked, missing, frozen, validated or merely ready;
- preservation of negative scientific information without converting it into an economic result;
- UI/projection remains derived from durable truth.

## Current capability found before change

V2 already writes durable research, dossier, disconfirmation, candidate, validator, readiness, negative-memory and frozen-export artifacts. The information was truthful but distributed. Producer dossier detail already exposes per-field `SUPPORTED`, `PARTIAL`, `UNKNOWN`, limitations and blockers.

## Prior design intent consulted

CP15 proposed an Edge Board and a mechanism-maturity vector. CP16 explicitly required those proposals to be challenged instead of implemented mechanically.

## Historical capability consulted

Historical Edge Lab/dashboard concepts exist, but this task does not import their state model or create another UI. The projection is deliberately contained in current Research OS V2 and accepts caller-supplied durable artifacts only.

## Actual gap concluded

A bounded derived projection was missing: one machine-readable object that can summarize current V2 scientific maturity and missing evidence without asserting profitability or opening the economic membrane.

## What changed

Added `research/research_os/expansion/edge_observability_v2.py`.

The new pure function `build_edge_observability_projection(...)`:
- performs no fetch, write, observation, evaluation or trading action;
- accepts only caller-supplied durable task/artifact records;
- rejects outcome/P&L/return/result-bearing payload fields;
- rejects any supplied open authority flag;
- rejects `outcome_accessed != false` and any economic result other than `NOT_OBSERVED`;
- projects the existing dossier into a per-field evidence maturity vector;
- lists non-SUPPORTED evidence explicitly as missing evidence;
- keeps scientific maturity and experiment readiness as separate axes;
- distinguishes `BLOCKED_NOT_FAILED`, `UNEXECUTED_NOT_NEGATIVE`, `PRE_OUTCOME_RESEARCH_ONLY`, and `READY_IS_NOT_PROFITABLE`;
- preserves `empirical_correlation = UNKNOWN` and `marginal_portfolio_contribution = NOT_ESTIMATED`;
- emits all four authority flags false and `projection_only = true`;
- hashes the deterministic projection for provenance/comparison.

Added `tests/test_research_os_edge_observability_v2.py` with five focused tests.

## Files / surfaces modified

- research/research_os/expansion/edge_observability_v2.py
- tests/test_research_os_edge_observability_v2.py

No existing runtime, task, candidate, validation, Site, Capital Desk, Book, policy or epoch file was modified.

## Commits produced

- 721e73901df4075da4f2e53c37923de47c2fa5f3 — CP001 system delta
- c9331e86c88dbebcdbd586d77c3464fda694ce28 — fail-closed V2 edge observability projection + tests

## Tests run

Local bounded unit invocation against the exact new module/test logic:

`python -m unittest -v test_edge_observability_v2.py`

RESULT: 5 tests PASS.

Covered:
1. documentary evidence vector with SUPPORTED/PARTIAL/UNKNOWN premises;
2. blocked attempt remains `BLOCKED_NOT_FAILED`;
3. READY package remains pre-outcome with closed authority and no profitability claim;
4. P&L/outcome-like field injection fails closed;
5. open authority or observed economic result fails closed.

The repository `Oracle V2 Core` GitHub workflow is configured to trigger on pushes to `builder/oracle-v2-core-20261020`, not on this isolated Builder rail. Therefore no CI-success claim is made for this branch. The new module is isolated/unreferenced by existing runtime, so the change cannot alter Oracle execution until explicitly integrated later.

## Adversarial / falsification checks

- Attempted P&L leakage -> rejected with `OUTCOME_FIELD_VISIBLE_TO_PROJECTION`.
- Attempted `real_capital_authorized=true` -> rejected with `AUTHORITY_OPEN_IN_PROJECTION`.
- Attempted `economic_result=POSITIVE` -> rejected with `ECONOMIC_RESULT_VISIBLE_TO_PROJECTION`.
- A stage blocker is surfaced as `BLOCKED_NOT_FAILED`, not an economic negative.
- A ready/exportable design is surfaced as `READY_IS_NOT_PROFITABLE`.
- Structural portfolio economic quantities remain unknown/not-estimated rather than numerically fabricated.

## Authority flags

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE

OUTCOME_ACCESS_STATUS: NOT_ACCESSED
ACTIVE_EPOCH_SAFETY_STATUS: CLEAN / BLINDED from latest reacquired durable state; no epoch mutation by this task

## What is now proven

- A deterministic fail-closed projection can summarize existing V2 scientific/process truth without outcome access.
- Dossier field maturity and missing evidence can be exposed without changing CandidateCore or duplicating producer architecture.
- Blocked, unexecuted, ready and validated states can remain epistemically distinct.

## What is not proven

- No economic edge, alpha or profitability is proven.
- No current candidate is asserted READY by this work.
- No Site/Live Lab integration is proven or attempted.
- No runtime/reboot proof is asserted.
- GitHub CI on the isolated Builder rail is NOT_RUN because the existing workflow does not target it.
- Global historical scientific-memory reconciliation is not closed.

## Known risks

- A future consumer must treat this object as a projection only and must not persist edits back as research truth.
- Integration must use actual durable artifacts and preserve their hashes/lineage; synthetic UI activity is forbidden.
- Oracle V2 can advance independently; convergence must reacquire and reconcile fresh HEAD.

## Unresolved questions

- Whether the best convergence consumer is the existing Site bridge, a Research OS status endpoint, or another existing projection surface must be decided by Final Integrator after Closure 1/3 evidence is current.
- Source breadth remains a separate mechanism-driven gap and should not be expanded symmetrically without evidence need.

NEXT_RECOMMENDED_TASK: inspect current live task/artifact corpus to determine whether this projection needs one repository-level read adapter (read-only) or whether existing Site/bridge collection already supplies all required records. Build only if a real integration gap is proven.
EXACT_RESUME_ACTION: read CP001 and CP002; reacquire fresh Oracle V2 HEAD; inspect current v2_bridge / Site bridge inputs and current artifact paths; do not integrate by assumption.
FINAL_INTEGRATOR_IMPLICATION: c9331e86c88dbebcdbd586d77c3464fda694ce28 is an isolated import candidate. Import only as derived projection logic; do not turn it into a second state authority.
SAFE_TO_CONTINUE: TRUE
