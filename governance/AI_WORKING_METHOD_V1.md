# Quant-Trade — AI Working Method V1

STATUS=`ACTIVE_METHOD`
DATE=`2026-11-01`
PURPOSE=`Make every AI advance the same canonical project without restart, parallel rebuild, stale authority or false PASS.`

This method applies to every Builder, Reviewer, Research, Operator or coordinating AI once the repository converges to the two canonical branches. It is also the migration target while historical refs still exist.

## 1. Two-branch law

Only two branches may carry current authority:

- `project/canonical` — project objective, current router, decisions, scientific memory, receipts, blockers, next action;
- `code/canonical` — executable product, tests, workflows, deployment/runtime helpers.

Historical information may remain in Git history or durable evidence, but it must not become a third current authority.

After final migration, creation of any additional branch is a policy failure unless the Owner explicitly changes this contract.

## 2. Single bootstrap for every AI

Before substantive action:

1. fetch/reconcile fresh `project/canonical` and `code/canonical`;
2. read `QUANT_NORTH_STAR.md` and this method on `project/canonical`;
3. read `governance/CURRENT_PROJECT_STATE.md` on `project/canonical`;
4. resolve the exact current `code/canonical` SHA;
5. inspect only evidence relevant to the current blocker/decision;
6. classify existing capability as `REUSE`, `CONNECT`, `REPAIR`, `BUILD_REQUIRED`, or `UNKNOWN`;
7. do not act from chat memory, an old prompt, default-branch history, branch names or a stale local checkout.

If durable current state proves the requested work is already complete, return `NO_CHANGE_REQUIRED` and continue from the current next action.

## 3. Mission admission gate

A material mission is executable only when it can state compactly:

- `CURRENT_SUBJECT` — exact SHA/runtime/scientific object;
- `CURRENT_BLOCKER_OR_DECISION`;
- `WHY_THIS_WORK_CAN_CHANGE_THE_DECISION`;
- `EXISTING_CAPABILITY` — REUSE/CONNECT/REPAIR/BUILD_REQUIRED/UNKNOWN;
- `MINIMAL_DECISIVE_TEST`;
- `COUNTEREXAMPLE` — one concrete way the proposed action could be wrong;
- `DURABLE_OUTPUT_REQUIRED`;
- `NEXT_ACTION_AFTER_PASS_FAIL_BLOCK`;
- `OWNER_AUTHORIZATION_REQUIRED`.

If the work cannot change a current decision, close a finish gate, prevent a demonstrated regression, or collect evidence required for one of those, disposition it `PARK` or `NO_CHANGE_REQUIRED`.

## 4. Progress order

Always prefer:

`REUSE > CONNECT > REPAIR > BUILD`

A new architecture, scheduler, control plane, memory system, framework or agent layer is forbidden unless a concrete current finish gate cannot be closed with the first three choices.

`UNKNOWN` blocks only the affected action. It does not authorize a repository-wide audit.

## 5. Concurrency and ownership

- one primary Builder may mutate a given capability/seam at a time;
- one independent Reviewer may challenge the exact published subject read-only;
- total active decision-changing lanes should be <= 2;
- a blocked lane is `PARK/BLOCK`; it must not trigger an unrelated substitute architecture;
- when `code/canonical` moves while another agent is working, the older agent must reconcile before publishing and may not overwrite newer canonical work;
- no agent may use a private/local-only SHA as shared authority.

## 6. Work lifecycle

Every material unit follows:

`RECONCILE -> INSPECT -> CHOOSE(REUSE/CONNECT/REPAIR/BUILD) -> CHALLENGE -> EXECUTE -> TEST -> PERSIST -> VERIFY_REMOTE -> UPDATE_ROUTER/NEXT_ACTION -> STOP`

Construction, test, qualification, integration, activation, use and end-to-end proof are separate states. Never infer a later state from an earlier one.

A PASS requires the decisive bytes/state to be remotely recoverable. `LOCAL_ONLY_PASS` is invalid.

A test/review/CI run for SHA A cannot qualify SHA B unless equivalence is explicitly proven.

## 7. Review law

A new independent review is justified only by at least one of:

- a new exact subject;
- new evidence;
- a new counterexample class;
- a previously unavailable primary object;
- an imminent irreversible boundary.

Otherwise the correct result is `NO_CHANGE_REQUIRED`.

A reviewer without the exact candidate/evidence must return `BLOCK_EVIDENCE` or `UNKNOWN`, not semantic PASS/FAIL.

## 8. Durable continuation

At every material interruption, durable state must preserve:

- exact current subject;
- work actually completed;
- tests actually executed and result;
- decisions changed;
- blockers/unknowns;
- one bounded next action;
- reopening condition for PARKed work.

A fresh AI must be able to resume from repository state without reconstructing the chat.

## 9. Scientific and authority boundaries

Never simplify away:

- exact subject/SHA identity;
- PIT/causal timing and provenance;
- frozen scientific protocol/exposure accounting;
- negative scientific memory;
- fail-closed authority;
- distinction between hosted qualification, deployment, runtime use and E2E proof.

Unless later explicitly changed by Owner authority:

- economic experiment, prospective observation, production deployment, real capital and live trading remain separately gated;
- a code/test PASS grants none of them.

## 10. Bounded finish line — prevent endless architecture

The engineering/autonomy project is considered `QUANT_SYSTEM_V1_FINISHED` only when all applicable gates below are proven on current canonical authority:

### F0 — TWO_BRANCH_AUTHORITY
Only `project/canonical` and `code/canonical` remain as current branches; no known live consumer depends on historical branch names.

### F1 — RECOVERABLE_CANONICAL_STATE
A fresh agent can identify objective, authority, current exact code head, blocker and next action from `project/canonical` alone; code and project entrypoints agree.

### F2 — EXACT_HEAD_ENGINEERING_QUALIFICATION
Current `code/canonical` exact head passes the required canonical regression/challenge suite. Tests are bound to that exact SHA.

### F3 — REAL_VM_MULTI_WAKE
On the authenticated intended host, at least two consecutive automatic wakes occur without Owner relaunch/routing, including one real Codex dispatch/result causally consumed by the following decision.

### F4 — GLOBAL_MISSION_CONTINUATION
After a bounded task reaches DONE/PARK/BLOCK, the running system autonomously selects the next legitimate unmet mission or produces a correct durable NOOP/PARK without human task substitution.

### F5 — IDENTITY_CONSERVING_E2E
A bounded non-economic/synthetic-safe witness proves one identity-conserving chain across the canonical research/control path, including durable result/memory and restart/duplicate/stale-head recovery. This proves mechanics, not alpha.

### F6 — OPERATIONAL_HANDOFF
No P0 engineering/autonomy blocker remains; normal future work is predominantly scientific/economic use of the system. A new architecture campaign is not required for ordinary operation.

`QUANT_SYSTEM_V1_FINISHED` does NOT mean profitable edge, real-capital authorization or live-trading authorization. Those are separate scientific/economic decisions. This distinction prevents an unknowable alpha target from keeping engineering permanently open.

## 11. Direction test for every proposed task

Before work starts ask:

1. Which F0–F6 gate does this close, falsify, or protect?
2. If none, which currently recorded blocker/decision does it change?
3. Is equivalent capability already present?
4. What is the smallest decisive test?
5. What concrete evidence would make us stop?

If 1 and 2 are both empty, do not do the task.

## 12. Anti-regression tests

The repository must maintain executable tests for the known failure modes:

- stale subject cannot be treated as authority;
- local-only work cannot be PASS;
- wrong-SHA CI/review cannot qualify current code;
- BUILD is rejected when REUSE/CONNECT/REPAIR is established;
- review without new evidence/counterexample becomes NO_CHANGE_REQUIRED;
- one external block cannot global-stop independent progress;
- irreversible action without required Owner authority is BLOCK;
- every durable checkpoint has a next action;
- WIP/concurrent mutation limits are enforced;
- project cannot be declared finished while any F0–F6 gate is unproven;
- after two-branch migration, extra remote branch creation is a failing gate.

## 13. Stop law

Stop a work unit when:

- the decision is resolved;
- the required gate is proven/falsified;
- a bounded blocker is established;
- more evidence cannot change the conclusion;
- or the work is correctly PARKed.

Do not continue merely to make the report larger.

## Final operating rule

`CLOSE THE NEXT REAL GATE. REUSE BEFORE BUILD. PUBLISH BEFORE HANDOFF. TEST THE EXACT SUBJECT. PRESERVE THE NEXT ACTION. STOP WHEN THE DECISION CANNOT CHANGE.`
