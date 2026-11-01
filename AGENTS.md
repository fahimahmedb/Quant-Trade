# AGENTS.md — Quant-Trade code/canonical agent entrypoint

This branch is the executable product authority. It is NOT the project/governance authority.

## Mandatory bootstrap

Before substantive work, fetch/reconcile both canonical branches and read, in this order:

1. `project/canonical:QUANT_NORTH_STAR.md`
2. `project/canonical:governance/AI_WORKING_METHOD_V1.md`
3. `project/canonical:governance/CURRENT_PROJECT_STATE.md`
4. the exact current `code/canonical` SHA and only the evidence needed for the current decision.

Machine-readable method contract:
`project/canonical:governance/AI_WORKING_METHOD_V1.json`.

For every material AI mission, before substantive mutation:

- create or replace `.quant/MISSION_ADMISSION.json` from fresh canonical state;
- bind the exact fresh `project/canonical` SHA, admitted `code/canonical` base SHA, current router blob identity, mission identity, blocker/decision, F0–F6 gate or recorded blocker, capability disposition, decisive test, counterexample, durable output, next action, Owner-authority status and active-seam/concurrency count;
- validate that real receipt with `scripts/validate_ai_working_method.py --admission ...` against the fresh identities;
- if either canonical head or router identity moves before publication, reconcile and regenerate the admission instead of reusing it;
- include a matching `Mission-ID: <mission_id>` commit trailer for a material code change.

A copied/stale receipt is not admission. Material code/workflow changes that do not update the receipt are non-authoritative and the canonical method workflow must reject them. Pure `data/feeds/**` ingestion updates are exempt because they are not AI project missions.

Do not route current work through old Blue handoffs, the repository default branch, historical `NEXT_BUILD_MISSION.md`, stale issues/prompts, or chat memory. Those may be evidence only.

## Authority split

- `project/canonical` owns objective, current router, decisions, scientific memory, receipts, blockers and next action.
- `code/canonical` owns executable code, tests, workflows and deployment/runtime helpers.

No third branch may become current authority. After final migration, extra branch creation is a policy failure unless Owner authority explicitly changes the contract.

## Work rule

Follow:

`REUSE > CONNECT > REPAIR > BUILD`

For a material mission, prove:

- exact current subject;
- current blocker/decision;
- how the work can change that decision or close/protect an F0–F6 finish gate;
- existing capability disposition;
- minimal decisive test;
- one concrete counterexample;
- durable output required;
- next action after PASS/FAIL/BLOCK;
- whether Owner authorization is required.

If the mission cannot change a current decision, close a finish gate, prevent a demonstrated regression or collect required evidence, return `PARK` or `NO_CHANGE_REQUIRED`.

## Concurrency

- one mutating Builder per capability/seam;
- at most two active decision-changing lanes total;
- independent Reviewer is read-only on the exact published subject;
- if `code/canonical` moves, reconcile before publishing; never overwrite newer canonical work;
- a blocked lane is PARK/BLOCK, not permission to build substitute architecture.

## Evidence law

Built, tested, qualified, integrated, promoted, active, used and end-to-end proven are different states.

- local-only work is never PASS;
- CI/review for SHA A does not qualify SHA B;
- reviewer without exact candidate/evidence returns BLOCK_EVIDENCE/UNKNOWN;
- publish exact remotely recoverable bytes/state before handoff or completion claim;
- preserve one bounded next action after every material interruption.

A material PASS/handoff must be bound to the validated admission identity. The AI Working Method Gate performs post-push exact-SHA validation; that is detection/qualification, not server-side prevention unless GitHub required-check enforcement is separately proven.

## Scientific / operational boundaries

Never simplify away exact identity, causal/PIT provenance, frozen scientific exposure, negative memory, fail-closed authority, or the distinction between hosted CI and actual deployment/use/E2E proof.

A code PASS grants no economic experiment, prospective observation, production deployment, real-capital or live-trading authority.

## Finish line

The bounded engineering/autonomy finish contract is F0–F6 in `governance/AI_WORKING_METHOD_V1.md` on `project/canonical`.

Every proposed material task must identify which finish gate or current blocker it changes. Do not expand architecture merely to create activity.

## Reporting

A completion report must state:

- exact branch + SHA;
- what changed;
- tests actually executed and results;
- admission identity for any material mutation;
- claim ceiling;
- durable project-state update if decision-changing;
- blockers/unknowns;
- next bounded action.

Final rule:

`CLOSE THE NEXT REAL GATE. REUSE BEFORE BUILD. PUBLISH BEFORE HANDOFF. TEST THE EXACT SUBJECT. PRESERVE THE NEXT ACTION.`
