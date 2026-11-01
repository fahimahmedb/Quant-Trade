# Quant-Trade — AI Working Method V1

STATUS=`ACTIVE_METHOD`
DATE=`2026-11-02`
PURPOSE=`Make every AI advance the same canonical project without restart, parallel rebuild, stale authority or false PASS.`

This remains the single working method for Builder, Reviewer, Research, Operator and coordinating AI. The 2026-11-02 change does not create a second methodology: it makes the existing mission-admission gate executable on real material missions.

## 1. Two-branch law

Only two branches may carry current authority:

- `project/canonical` — objective, current router, decisions, scientific memory, receipts, blockers and next action;
- `code/canonical` — executable product, tests, workflows and deployment/runtime helpers.

Historical information may remain in Git history or evidence, but it is not a third current authority. Branch names, the repository default branch, stale prompts and chat memory are not authority.

## 2. Single bootstrap for every AI

Before substantive action:

1. fetch/reconcile fresh `project/canonical` and `code/canonical`;
2. read `QUANT_NORTH_STAR.md` and this method on `project/canonical`;
3. read `governance/CURRENT_PROJECT_STATE.md`;
4. resolve exact current project/code SHAs and current router identity;
5. inspect only evidence relevant to the current blocker/decision;
6. classify existing capability as `REUSE`, `CONNECT`, `REPAIR`, `BUILD_REQUIRED`, or `UNKNOWN`;
7. perform the real mission admission below before any material mutation or authoritative project decision.

If durable current state proves the requested work is already complete, return `NO_CHANGE_REQUIRED` and continue from the recorded next action.

## 3. Real mission admission gate

A material AI mission is executable only after creating or replacing the single machine-readable receipt:

`code/canonical:.quant/MISSION_ADMISSION.json`

The receipt is an input to enforcement, not documentation. It must contain fresh values for:

- mission identity/type/timestamp;
- `PROJECT_CANONICAL_SHA`;
- admitted `CODE_CANONICAL_SHA`;
- current router identity;
- exact current subject;
- current blocker or decision;
- target F0–F6 gate or recorded blocker;
- existing capability: `REUSE | CONNECT | REPAIR | BUILD_REQUIRED | UNKNOWN`;
- why the work can change the decision;
- minimal decisive test;
- one concrete counterexample;
- durable output required;
- next action after PASS/FAIL/BLOCK;
- Owner-authorization requirement/status;
- active seam and concurrency counts;
- requested action.

Before substantive work, validate the real receipt with the canonical validator on `code/canonical` against the fresh project SHA, admitted code SHA and router identity.

A copied receipt from another mission is invalid. A receipt becomes stale when the project head, code head or router identity it binds moves, unless exact equivalence is explicitly proven. Reconcile and regenerate it; never silently reuse it.

Pure automatic ingestion changes confined to `data/feeds/**` are exempt because they are not AI project missions or project decisions. The exemption does not extend to code, workflow, governance, research-decision or operational-authority mutations.

## 4. Admission → completion binding

Every material authoritative PASS/handoff must bind to the immutable identity `sha256(canonical-json(admission))` and the exact published/tested subject SHA.

A material result with no valid admission link, wrong tested SHA, local-only output or no next action is `NON_AUTHORITATIVE_RESULT`, not PASS.

The hosted `AI Working Method Gate` is post-push detection/qualification. It does not become server-side prevention merely because it is green. Server-side required-check enforcement must be separately demonstrated.

## 5. Progress order

Always prefer:

`REUSE > CONNECT > REPAIR > BUILD`

A new architecture, scheduler, control plane, memory system, framework or agent layer is forbidden unless a concrete current gate cannot be closed with the first three choices.

`UNKNOWN` blocks only the affected action. It does not authorize repository-wide archaeology.

## 6. Concurrency and ownership

- one primary Builder may mutate a capability/seam at a time;
- at most two active decision-changing lanes total;
- an independent Reviewer is read-only on the exact published subject;
- if a canonical head moves before publication, reconcile rather than overwrite;
- a blocked lane is `PARK/BLOCK`, not permission to create substitute architecture;
- no private/local-only SHA is shared authority.

## 7. Work lifecycle

Every material unit follows:

`RECONCILE -> ADMIT -> INSPECT -> CHOOSE(REUSE/CONNECT/REPAIR/BUILD) -> CHALLENGE -> EXECUTE -> TEST -> PERSIST -> VERIFY_REMOTE -> UPDATE_ROUTER/NEXT_ACTION -> STOP`

Construction, test, qualification, integration, activation, use and end-to-end proof are separate states. A test/review/CI run for SHA A cannot qualify SHA B unless equivalence is explicitly proven.

## 8. Review law

A new independent review is justified only by at least one of:

- a new exact subject;
- new evidence;
- a new counterexample class;
- a previously unavailable primary object;
- an imminent irreversible boundary.

Otherwise return `NO_CHANGE_REQUIRED`. A reviewer without the exact candidate/evidence returns `BLOCK_EVIDENCE` or `UNKNOWN`.

## 9. Durable continuation

At every material interruption preserve in canonical durable state:

- exact current subject;
- work actually completed;
- tests actually executed and result;
- decisions changed;
- blockers/unknowns;
- one bounded next action;
- reopening condition for PARKed work.

A fresh AI must be able to resume from repository state without reconstructing the chat.

Detailed audits remain historical evidence. General working rules belong here; current facts/critical path belong in `CURRENT_PROJECT_STATE.md`; objective/finish meaning belongs in `QUANT_NORTH_STAR.md`. Do not grow a parallel mandatory bootstrap stack.

## 10. Scientific and authority boundaries

Never simplify away exact identity, PIT/causal timing/provenance, frozen scientific protocol/exposure accounting, negative scientific memory, restart/idempotency semantics or fail-closed authority.

Code/tests/CI do not grant economic experiment, prospective observation, production deployment, real-capital or live-trading authority.

## 11. Bounded finish line

`QUANT_SYSTEM_V1_FINISHED` requires every required F0–F6 gate to be PASS on current canonical authority:

- `F0_TWO_BRANCH_AUTHORITY` — only intended canonical authority remains, with residual external/admin exceptions bounded and non-authoritative;
- `F1_RECOVERABLE_CANONICAL_STATE` — a genuinely fresh repository-only agent/session recovers objective, authority, fresh heads, router/blocker, next action, method, already-complete work and correct REUSE/CONNECT/REPAIR/BUILD disposition without chat context or parallel methodology;
- `F2_EXACT_HEAD_ENGINEERING_QUALIFICATION` — exact current code head passes required canonical regression/challenge suite;
- `F3_REAL_VM_MULTI_WAKE` — intended authenticated host proves at least two automatic wakes including real Codex result consumption;
- `F4_GLOBAL_MISSION_CONTINUATION` — after terminal bounded task state, system selects the next legitimate unmet mission or durable NOOP/PARK without human task substitution;
- `F5_IDENTITY_CONSERVING_E2E` — bounded non-economic/synthetic-safe witness preserves identity across the canonical path and recovery cases;
- `F6_OPERATIONAL_HANDOFF` — no P0 engineering/autonomy blocker remains and ordinary future work does not require another architecture campaign.

`QUANT_SYSTEM_V1_FINISHED` does not mean profitable edge, real-capital authorization or live-trading authorization.

## 12. Direction test

Before work starts ask:

1. Which F0–F6 gate does this close, falsify or protect?
2. If none, which current blocker/decision does it change?
3. Is equivalent capability already present?
4. What is the smallest decisive test?
5. What evidence would make us stop?

If 1 and 2 are both empty, do not do the task.

## 13. Required anti-regression behavior

The real admission interface and its tests must fail closed for at least:

- stale project/code/router identity;
- copied/unrelated receipt;
- missing exact subject or blocker/decision;
- BUILD when REUSE/CONNECT/REPAIR is established;
- duplicate review without new decision-changing input;
- local-only PASS;
- unjustified global stop from a local blocker;
- WIP or same-seam concurrent-Builder violation;
- missing required Owner authority;
- missing next action;
- wrong-SHA completion;
- false project finish while any required F0–F6 gate is OPEN/BLOCK/UNKNOWN;
- head movement after admission without reconciliation.

Distinguish `TEST_PLANNED`, `TEST_EXECUTED` and `TEST_PASSED`.

## 14. Stop law

Stop a work unit when the decision is resolved, the required gate is proven/falsified, a bounded blocker is established, additional evidence cannot change the conclusion, or the work is correctly PARKed.

Do not continue merely to make the report larger.

## Final operating rule

`CLOSE THE NEXT REAL GATE. REUSE BEFORE BUILD. PUBLISH BEFORE HANDOFF. TEST THE EXACT SUBJECT. PRESERVE THE NEXT ACTION. STOP WHEN THE DECISION CANNOT CHANGE.`
