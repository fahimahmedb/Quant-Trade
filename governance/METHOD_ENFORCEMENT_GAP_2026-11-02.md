# Quant-Trade — AI method enforcement gap

DATE=2026-11-02
STATUS=DECISION_CHANGING_FINDING
SCOPE=AI_WORKING_METHOD_V1 enforcement

## Finding

The existing AI working method and its green CI/tests prove the method specification, validator behavior, canonical entrypoint wiring and exact-SHA checkout. They do **not** prove that every real AI mission actually executed the bootstrap/admission gate before substantive work.

Observed counterexample: a ChatGPT/GitHub work session prepared and published a new post-operational resume program before explicitly proving that it had first applied the canonical bootstrap/admission gate. The Owner had to remind the session that the two-branch method was already intended to absorb the final meta-audit recommendations. This is a real behavioral failure even though the method tests were green.

Therefore the prior interpretation is corrected:

- METHOD_SPECIFICATION=PASS
- METHOD_UNIT_TESTS=PASS
- METHOD_ENTRYPOINT_WIRING=PASS
- METHOD_REAL_AGENT_ENFORCEMENT=NOT_PROVEN
- F1_RECOVERABLE_CANONICAL_STATE=NOT_PROVEN_BY_UNIT_TESTS_ALONE

## Why the tests did not catch it

`tests/test_ai_working_method.py` calls `evaluate_mission()` with synthetic mission dictionaries and verifies expected dispositions. The workflow runs those tests and validates static entrypoint tokens. The CLI gate itself validates the contract, entrypoint text and branch list; it does not require a real current mission/admission receipt from the agent performing the work.

Thus a real agent can ignore or fail to execute the admission procedure and still create a commit; the next CI run may remain green because the repository contract itself is still valid. Both canonical branches were also observed without server-side branch protection, so green CI is detection/qualification, not a hard pre-write enforcement boundary.

## Required correction after the current Codex operational closeout

Do not create a parallel methodology. Harden the existing method with the smallest enforcement seam:

1. Every substantive AI session must first produce a verifiable BOOTSTRAP/ADMISSION receipt from fresh canonical state: project SHA, code SHA, method/router identity, current blocker/decision, existing capability disposition, minimal decisive test, counterexample, durable output and next action.
2. The actual receipt, not a synthetic fixture, must be validated by the existing validator before substantive mutation or completion claim.
3. A blind fresh-agent recovery test must be executed without chat context. F1 can PASS only if the agent reconstructs current authority, heads, blocker, applicable method and next action from canonical state alone.
4. The test suite must distinguish SPEC_PASS from ENFORCEMENT_PASS.
5. After the repository reaches the two-branch target, required checks/rulesets should make method-gate failures preventative where compatible with authorized automation writes.
6. ChatGPT/GitHub connector sessions are not assumed to auto-load AGENTS.md; they must explicitly fetch the canonical bootstrap before Quant-Trade substantive work. Do not assume behavior of one agent surface applies to every AI.

## Stop law

Do not rerun the meta-audit. This is a concrete falsifier of the current method enforcement claim, not a reason to reopen historical archaeology.

NEXT_ACTION=AFTER_CURRENT_CODEX_CLOSEOUT, RECONCILE FRESH STATE THEN HARDEN AI_WORKING_METHOD_V1 WITH REAL-MISSION ADMISSION + BLIND RECOVERY ENFORCEMENT BEFORE CLAIMING F1/METHOD_ENFORCEMENT PASS.
