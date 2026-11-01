# AGENTS.md — Quant-Trade canonical project contract

This is the single bootstrap for every AI working on Quant-Trade: Builder, Reviewer, Research, Operator or coordinator. Do not rely on chat history.

## Mandatory bootstrap

Before substantive work:

1. fetch/reconcile fresh `project/canonical` and `code/canonical`;
2. read `QUANT_NORTH_STAR.md`;
3. read `governance/AI_WORKING_METHOD_V1.md` and its machine contract `governance/AI_WORKING_METHOD_V1.json`;
4. read `governance/CURRENT_PROJECT_STATE.md`;
5. resolve exact current project/code SHAs and current router identity;
6. inspect only evidence needed for the current blocker/decision or F0–F6 gate;
7. classify existing capability `REUSE | CONNECT | REPAIR | BUILD_REQUIRED | UNKNOWN`;
8. for every material AI mission, create/replace and validate `code/canonical:.quant/MISSION_ADMISSION.json` before substantive mutation or authoritative project decision.

The receipt must bind fresh canonical identities, exact mission/subject, blocker/decision, target gate, capability disposition, decisive test, counterexample, durable output, next action, Owner-authority status and active seam/concurrency. A copied or stale receipt is invalid. If either canonical head or router identity moves, reconcile and regenerate instead of silently reusing the receipt.

Do not use the repository default branch, old Blue/V1/V2 handoffs, `NEXT_BUILD_MISSION.md`, historical branches, stale prompts, local checkout state or chat memory as current authority.

## Authority split

- `project/canonical` owns objective, current router, decisions, scientific memory, evidence/receipts, blockers and next action.
- `code/canonical` owns executable product, tests, workflows and deployment/runtime helpers.

No third branch is current authority. Historical objects are evidence only unless the current router explicitly reopens them.

## Work law

`REUSE > CONNECT > REPAIR > BUILD`

A material mission is admitted only when it can change a current decision, close/protect an F0–F6 gate, prevent a demonstrated regression or collect required evidence. Otherwise return `PARK` or `NO_CHANGE_REQUIRED`.

`UNKNOWN` blocks only the affected action. It does not authorize global archaeology.

## Concurrency and continuation

- one mutating Builder per capability/seam;
- at most two active decision-changing lanes;
- independent Reviewer read-only on the exact published subject;
- reconcile if either canonical head moves before publishing;
- local/private work is never shared authority or PASS;
- after every material interruption persist exact subject, completed work, tests actually executed, changed decision, blockers/unknowns and one bounded next action.

A material PASS/handoff must reference the immutable identity of its validated admission receipt and the exact published/tested subject. Missing admission, wrong SHA or local-only output makes the result non-authoritative.

A fresh AI must resume from GitHub durable state without reconstructing a conversation.

## Evidence law

Built, tested, qualified, integrated, promoted, active, used and end-to-end proven are separate states.

- CI/review for SHA A does not qualify SHA B;
- remotely recoverable bytes/state are required before durable PASS/handoff;
- reviewer without exact candidate/evidence returns `BLOCK_EVIDENCE` or `UNKNOWN`;
- hosted CI is post-push detection/qualification unless a required server-side check is separately proven;
- hosted CI does not prove deployment, runtime use or E2E operation.

## Scientific and authority invariants

Never fabricate evidence or data. Preserve exact identity, PIT/causal timing, provenance, frozen scientific exposure accounting, negative scientific memory, restart/idempotency semantics and fail-closed authority.

Code/tests/governance do not grant economic experiment, prospective observation, production deployment, real-capital or live-trading authority.

## Capitalization law

- general durable working rule -> `governance/AI_WORKING_METHOD_V1.md/json`;
- current project fact / critical path -> `governance/CURRENT_PROJECT_STATE.md`;
- objective / finish meaning -> `QUANT_NORTH_STAR.md`;
- detailed audits/program drafts -> historical evidence only unless a current canonical surface promotes a decision-changing delta.

`governance/POST_OPERATIONAL_RESUME_PROGRAM_2026-11-02.md` is non-authoritative historical/prepared evidence and is NOT a mandatory bootstrap file.

## Finish line

The finite engineering/autonomy finish definition is F0–F6 in `governance/AI_WORKING_METHOD_V1.md`.

Every material task must identify which current finish gate or recorded blocker it changes. Do not keep engineering open merely because profitable alpha is unknown; economic value, real capital and live trading are separate authorities.

## Reporting

Every material completion states exact subject/branch/SHA, evidence changed, tests actually executed/results, admission identity, claim ceiling, durable project-state update when decision-changing, blockers/unknowns and one next bounded action.

Final rule:

`CLOSE THE NEXT REAL GATE. REUSE BEFORE BUILD. PUBLISH BEFORE HANDOFF. TEST THE EXACT SUBJECT. PRESERVE THE NEXT ACTION.`
