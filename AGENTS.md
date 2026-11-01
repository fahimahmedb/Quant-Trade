# AGENTS.md — Quant-Trade canonical project contract

This is the single bootstrap for every AI working on Quant-Trade. It applies to Builders, Reviewers, Research agents, Operators and coordinators without relying on chat history.

## Mandatory bootstrap

Before substantive work:

1. fetch/reconcile fresh `project/canonical` and `code/canonical`;
2. read `QUANT_NORTH_STAR.md` on `project/canonical`;
3. read `governance/AI_WORKING_METHOD_V1.md` on `project/canonical`;
4. read `governance/CURRENT_PROJECT_STATE.md` on `project/canonical`;
5. resolve the exact current `code/canonical` SHA;
6. inspect only evidence needed for the current blocker/decision or F0–F6 finish gate.

Machine-readable method: `governance/AI_WORKING_METHOD_V1.json`.

Do not use the repository default branch, old Blue/V1/V2 handoffs, `NEXT_BUILD_MISSION.md`, historical branch names, stale prompts, local checkout state or chat memory as current authority.

## Authority split

- `project/canonical` owns objective, current project router, decisions, scientific memory, evidence/receipts, blockers and next action.
- `code/canonical` owns executable product, tests, workflows and deployment/runtime helpers.

No third branch is current authority. Historical objects are evidence only unless the current router explicitly reopens them.

## Work law

Follow:

`REUSE > CONNECT > REPAIR > BUILD`

A material mission is admitted only when it can change a current decision, close/protect an F0–F6 finish gate, prevent a demonstrated regression, or collect evidence required for one of those. Otherwise return `PARK` or `NO_CHANGE_REQUIRED`.

Use the exact mission admission fields and stop laws in `governance/AI_WORKING_METHOD_V1.md`; do not create a competing methodology.

`UNKNOWN` blocks only the affected action. It does not authorize global archaeology.

## Concurrency and continuation

- one mutating Builder per capability/seam;
- at most two active decision-changing lanes;
- independent Reviewer is read-only on the exact published subject;
- reconcile if either canonical head moves before publishing;
- local/private work is never shared authority or PASS;
- after every material interruption persist exact subject, completed work, tests actually executed, changed decision, blockers/unknowns and one bounded next action.

A fresh AI must resume from GitHub durable state without reconstructing a conversation.

## Evidence law

Built, tested, qualified, integrated, promoted, active, used and end-to-end proven are separate states.

- a test/review/CI run for SHA A does not qualify SHA B;
- remotely recoverable bytes/state are required before durable PASS/handoff;
- reviewer without the exact candidate/evidence returns `BLOCK_EVIDENCE` or `UNKNOWN`;
- hosted CI does not prove deployment, runtime use or E2E operation.

## Scientific and authority invariants

Never fabricate evidence or data. Preserve exact identity, PIT/causal timing, provenance, frozen scientific protocol/exposure accounting, negative scientific memory, restart/idempotency semantics and fail-closed authority.

Unless a later explicit Owner decision changes them, code/tests/governance do not grant economic experiment, prospective observation, production deployment, real-capital or live-trading authority.

Scientific failure, engineering failure, environment/access BLOCK and insufficient evidence are different outcomes.

## Roles

Builder: reuse/connect/repair/build executable capability and exact tests.

Reviewer: try to falsify the exact published subject; do not mutate it.

Research: produce falsifiable hypotheses and preserve full selection/exposure/negative memory under current authority.

Operator: prove deployment/runtime state from the actual authorized environment; do not extend repository claims into host claims.

Coordinator: preserve one current router, bounded WIP and durable continuation; do not create extra process layers.

## Finish line

The finite engineering/autonomy finish definition is F0–F6 in `governance/AI_WORKING_METHOD_V1.md`.

Every material task must identify which current finish gate or recorded blocker it changes. Do not keep engineering open because profitable alpha is unknown: economic value, real capital and live trading are separate later authorities.

## Reporting

Every material completion states:

- exact subject/branch/SHA;
- evidence changed;
- tests actually executed and results;
- claim ceiling;
- durable project-state update when decision-changing;
- blockers/unknowns;
- one next bounded action.

Final rule:

`CLOSE THE NEXT REAL GATE. REUSE BEFORE BUILD. PUBLISH BEFORE HANDOFF. TEST THE EXACT SUBJECT. PRESERVE THE NEXT ACTION.`
