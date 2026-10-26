# BUILDER CP009 — Evidence/acquisition owner projection gap

CHECKPOINT_ID: BUILDER_CP_009_ACQUISITION_OBSERVABILITY_GAP_20261020
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: 56961b2aa9b0f88a2719e867b334a0a7f95acc91
CURRENT_BUILDER_HEAD_DESCRIBED: 56961b2aa9b0f88a2719e867b334a0a7f95acc91
FRESH_OBSERVED_ORACLE_V2_HEAD: 1b80321eb81860586b5645661e34574ed40f968f
AUDIT_HEAD: 67543ff286ff7a81a6705a197b7e557442d62ac2
SAFE_TO_CONTINUE: TRUE

## Objective and scope

Resume CP008, challenge the alleged missing composition before code, and retain
CP16's separation between isolated Builder improvements and Final Integrator
runtime/Site closure. CP12–CP16 and the North Star govern interpretation; CP15
is design intent rather than a mandatory build list.

## Reacquired evidence

The existing clean checkout was switched to the existing Builder rail, without
a worktree, reset, merge or change to autonomous Oracle. CP008 and its bridge
are present at the exact advertised Builder SHA. Oracle's observed history
contains the reported 32b75fa legacy check, followed by a generation-2
EVENT_DOCUMENT-010 claim/research and queue refill. Git history is repository
evidence only; it is not a fresh host, Site, model or reboot attestation.

Inspected exact repository surfaces:

| Rail | HEAD | Relevant capability / limit |
| --- | --- | --- |
| Builder | 56961b2aa9b0f88a2719e867b334a0a7f95acc91 | `edge_observability_v2.py` exposes dossier missing evidence and V2 readiness. Its signature has no producer-readiness/catalog/intent input. CP008's bridge has only test consumers. |
| Oracle V2 | 1b80321eb81860586b5645661e34574ed40f968f | `v2_stage_executor.py` creates candidate/validator/blinding-bound readiness sidecars, without acquisition-intent status. |
| Live Lab canonical | d14b96c6517f6a14a28bf67ab98bcfc71f49a3ec | `live_lab_contract.py` maps existing lane/stage to UI metadata. `platform-native.js` projects worker/session/activity facts; no CP008 intent statuses. |
| Live Lab integration | a48bbb3594036b1a5c323af42a2723c8defcf555 | Native event/snapshot projection, no evidence/acquisition composition. |
| Oracle/Site bridge | 4dd1400452f624ad27bddd96b07a3d6d9abef1da | `live_lab_bridge.py::project_live_event` adds allowlisted stage UI metadata to existing events. It does not read producer readiness or acquisition intents. |

Also inspected `src/quant/edge_lab/dashboard.py`: historical Lab state/queue,
families, decisions and trial accounting are projected, not CP008's V2 intents.
`acquisition_firewall_v1.py::firewall_summary` summarizes content-record
PASS/BLOCK checks; Wave4 builds fixture acquisition plans. Neither composes
producer requirements with the owner edge vector. Source qualification already
owns producer readiness and CP008 owns exact route matching and plan creation.

Falsification search: `git grep` across all five exact trees for bridge names,
`READY_PLAN_ONLY`, `UNRESOLVED_NO_DECLARED_ROUTE`, acquisition-plan and network
authorization fields, followed by semantic inspection of the above consumers.
Only firewall/Wave4 and tests supplied acquisition-plan hits outside Builder.
No equivalent composed projection was found in these inspected trees.

Limit: deployed Site backend/browser state was not inspected. This is a bounded
repository composition gap, not a claim that every possible external owner
surface is absent or that Site transport must be rebuilt.

## Confirmed bounded gap and minimal delta

Missing: an importable owner projection joining explicit producer requirements,
CP008 intent status, firewall plan status/blockers and closed network execution
with the existing dossier evidence vector.

Extend the existing `build_edge_observability_projection` with optional explicit
producer-readiness/catalog inputs. Call the existing CP008 bridge; do not
duplicate its qualification, routing, hashing or firewall policy. Summarize its
output without returning raw locator parameters or source content. Bind exact
readiness/intent hashes. Keep producer readiness separate from V2 validation
readiness so plan readiness cannot promote scientific or experiment readiness.
With no new inputs, preserve the existing projection contract/hash.

Required adversarial evidence: ready-plan, no route, absent adapter, ambiguous
route, forbidden requirement/content, invalid PIT/version, actual firewall
block, exact provenance changes, no input mutation or I/O, closed authority,
no maturity promotion, and rejection of outcome/open-authority inputs.
Report network state as plan-only; do not infer actual proxy/firewall connectivity.

## Changes and validation

- This checkpoint only; no application code or tests changed yet.
- Inspection and read-only Git operations only; code qualification NOT_RUN here.
- No Site, runtime tasks, epoch, sources, adapters or autonomous branch mutated.
- All four authorities FALSE; OUTCOME_ACCESSED FALSE; ECONOMIC_RESULT NOT_OBSERVED.

## Next resume action / handoff

Implement and test only the optional composition in the existing edge module.
Run the Builder V2 workflow checks on the exact implementation commit, including
read-only GitHub dry-run. Persist CP010 with executed evidence, distinguishing
local workflow execution from hosted CI. Final Integrator may later import the
pure capability; runtime wiring and Site publication remain separate work.
