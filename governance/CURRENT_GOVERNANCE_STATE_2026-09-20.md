# CURRENT GOVERNANCE STATE — 2026-09-20

Purpose: compact current-governance index for Quant. This is a routing/index document, not a replacement for the authorities it cites.

## 0A. REPOSITORY HYGIENE EXECUTION — LATEST

`REPOSITORY_HYGIENE = CLOSED / EXECUTED`

Durable execution handoff:
`handoff/BLUE_REPOSITORY_HYGIENE_EXECUTION_2026-09-20.md`

Current verified namespace state:
- default branch = `blue/master-v2-2026-09-20`;
- live branches = `40`;
- delete batch = `34 / 34 COMPLETE`;
- delete-ready survivors = `0`;
- restaurant branch = `RETAIN_OWNER_REQUEST`;
- open PRs = `0`;
- open issues = `0`.

This cleanup does not alter Gate A v4, P14D, t0, Product integration, target-host readiness or capital authority.

## 0. Authority precedence

1. `QUANT_NORTH_STAR.md` — highest architecture/product authority unless explicitly revised by owner.
2. Current Blue durable governance — `blue/master-v2-2026-09-20`, especially `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`.
3. Exact frozen candidates, contracts, independent audits and hash-addressable evidence relevant to the active decision.
4. Historical branches, checkpoints and chat summaries.

When two sources conflict, later committed durable evidence at the correct authority level wins. Do not transfer proof silently across SHAs.

## 1. Roles

`BLUE / MISSION CONTROL`
- owns project-level decisions;
- decides gates, specifications, integration, deployment progression and capital authorization;
- does not self-certify a Builder correction as independent evidence.

`BUILDER`
- implements a Blue-approved specification;
- stops after durable delivery/handoff;
- does not independently certify its own fix.

`ASTRA / RED TEAM`
- independently attacks/reproduces;
- does not start from Blue's desired conclusion;
- classifies REAL_DEFECT / TEST_DEFECT / MISSING_PROOF / TARGET_HOST_ONLY / NON_ISSUE;
- does not modify the audited production candidate while acting as independent auditor.

General flow:
`finding/challenge → Blue decision → specification → Builder → independent review → Blue decision`.

## 2. Current program state

`CURRENT_BLUE_OWNER = blue/master-v2-2026-09-20`

Resolve live HEAD rather than copying a stale self-reference.

`GATE_A_V3_REPOSITORY_DISPOSITION = PASS` — historical repository-only disposition at the exact audited SHA.

`GATE_A_V3_TARGET_HOST_ELIGIBILITY = REJECTED_BY_NEW_REAL_DEFECT`

`CORRECTIVE_GATE_A_V4_REQUIRED = CLOSED / V4_REPOSITORY_PASS`

Frozen candidate:
`blue/p0-gate-a-v3-frozen-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Independent final audit:
`astra/p0-gate-a-v3-independent-audit-2026-09-20@33995d03c8632e5c3a7b77a12b87366fb06b4d30`

Astra exact-head CI:
`35517935710 = COMPLETED / SUCCESS`

Blue final disposition:
`handoff/BLUE_GATE_A_V3_FINAL_DISPOSITION_2026-09-20.md`

## 3. Current safety/gate state

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION`

`TARGET_HOST_READY = FALSE / GATE_B_NOT_EXECUTED`

`GATE_B = NOT_STARTED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`PRODUCT_INTEGRATION = PAUSED`

Gate A PASS must not be promoted into any stronger statement above.

## 4. Active mission

`MISSION = TARGET-HOST GATE B ENTRANCE + HYBRID P0 LIVE QUALIFICATION`

`STATUS = HYBRID_PROMOTED / REPOSITORY_PROOF_CLOSED / GATE_B_AUTHORITY_PACK_CURRENT / GATE_B_NOT_STARTED`

Mission handoff:
`handoff/BLUE_TARGET_HOST_QUALIFICATION_MISSION_2026-09-20.md`

Target-host real-defect disposition:
`handoff/BLUE_TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_2026-09-20.md`

Entrance contract:
`governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md`

Execution runbook:
`governance/TARGET_HOST_P0_RODAGE_RUNBOOK_2026-09-20.md`

Only an operator/agent with real target-host access may claim target-host execution evidence.

Repository-only work may prepare/check specifications but must not claim host proof.

## 5. Gate A residuals carried forward

Disabled-lane direct-poll observation:
`NON_BLOCKING_DESIGN_OBSERVATION_FOR_GATE_A`

Fingerprint/service-manager/invocation pre-seeding concern:
`MISSING_PROOF / TARGET_HOST_ENTRANCE_CONCERN`

Mandatory target-host falsifier:
if unauthorized pre-seeding can occur and the later qualifying audit still reaches `accountable=True`:
`REAL_DEFECT / REOPEN_GATE_A = TRUE`.

## 6. Cleanup governance

Open PRs:
`0`

Open issues:
`0`

Current branch inventory:
`45`

Single operational deletion authority:
`governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md`

Current verified delete-ready state:
- refs = 34 historical execution inputs;
- exact pinned SHA preflight = 34/34;
- physical deletions executed = 34/34;
- delete-ready survivors = 0.

Deletion must use a true branch-delete/delete-ref operation. Never emulate deletion by moving refs.

Divergent falsifier/audit refs and unique Product/recovery/learning/design refs remain preserved until separate retirement decisions.

## 7. Default branch governance

Current repository default:
`blue/master-v2-2026-09-20`

It is stale and non-authoritative.

Review:
`governance/DEFAULT_BRANCH_MIGRATION_REVIEW_2026-09-20.md`

`DEFAULT_BRANCH_REVIEW = COMPLETE`

`DEFAULT_BRANCH_MIGRATION_EXECUTED = TRUE`

Proposed interim default:
`blue/master-v2-2026-09-20`

Migration must use an actual repository-admin default-branch mutation and be verified afterward. Do not emulate it with ref movement.

## 8. Product authorities — paused

Canonical Forward:
`parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`

Canonical Economic:
`parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Product integration topology reference:
`blue/integration-readiness-2026-09-20`

These are not active integration authority while `PRODUCT_INTEGRATION = PAUSED`.

Preserve unique Product capabilities until explicit mapping decisions:
- Evidence/PIT identity;
- Research Factory core;
- product-side SEC census;
- relevant Forward recorder/live-smoke semantics;
- alternate Economic evidence until semantic supersession is recorded.

## 9. Scientific/economic governance

The terminal objective remains real long-run net wealth growth after real frictions.

Scientific validity, target-host continuity, economic readiness and capital authorization are distinct proof domains.

A green CI is execution evidence only.

`NO_TRADE` may be economically optimal.

No strategy, model, feature, risk metric, activity level, agent count or code volume is itself a terminal success criterion.

## 10. What the next conversation should do

First:
- read North Star;
- read Blue Master state;
- read this index;
- verify live Blue HEAD and current repository deltas.

Then:
- treat Gate A v4 repository correction as CLOSED/PASS only for exact candidate `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- verify the live independent fault-matrix review branch and receive its final evidence before hybrid-method promotion;
- keep fixed P14D authoritative until an explicit Blue superseding amendment commit exists;
- keep the prepared Gate-B/t0 operator pack non-executable until hybrid promotion and explicit Blue activation;
- preserve the failed v3 target-host evidence as historical REAL_DEFECT evidence and never rematerialize/re-authorize v3 to make it appear clean;
- do not start Product integration without explicit Blue decision;
- do not declare target-host readiness, Gate B, t0, Gate C, P14D replacement or capital authorization by implication.

## 11. Current governance verdict

`GOVERNANCE_AUTHORITY = CLEAR`

`DURABLE_MEMORY = ESTABLISHED`

`ROLE_SEPARATION = ESTABLISHED`

`GATE_DISCIPLINE = ESTABLISHED`

`BRANCH_CLEANUP = EXECUTED / CLOSED`

`DEFAULT_BRANCH_MIGRATION = EXECUTED / VERIFIED`

`ACTIVE_FRONTIER = GATE_B_ACTIVATION_PREPARATION + TARGET_HOST_ENTRANCE`

Corrective Builder dispatch:
- branch: `builder/p0-effective-unit-digest-stability-v4-2026-09-20`;
- exact implementation baseline: `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`;
- mission contract commit: `b3fc705f082ce1fee7d415211ce42829c96cdbfc`;
- implementation commit: `0bdd397d7409b01529c1f958c68781499679a95e`;
- selected delivery candidate: `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- frozen ref: `blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- implementation-head workflow: `35535347844 = COMPLETED / SUCCESS`;
- selected-delivery workflow: `35536353538 = COMPLETED / SUCCESS`;
- mission file: `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_MISSION_2026-09-20.md`;
- final handoff: `handoff/BUILDER_P0_EFFECTIVE_UNIT_DIGEST_STABILITY_V4_HANDOFF_2026-09-20.md`;
- Blue reception: `PASS_FOR_INDEPENDENT_ASTRA_REVIEW`;
- independent audit branch: `astra/p0-gate-a-v4-independent-audit-2026-09-20`;
- Astra mission commit: `b636a04b6f8f7786679907d01a4fa22bdfc4e329`;
- status: `FROZEN / INDEPENDENT_AUDIT_DISPATCHED`.


## 12. Target-host event — 2026-09-20

Real target-host execution against frozen Gate A v3 candidate `2da079d8ad75c69eb3fc2990c512735cb4bdc02b` produced a reproducible acquisition-critical fingerprint instability.

Durable Blue finding:
`handoff/BLUE_TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_2026-09-20.md`

Restricted target-host artifact binding:
- artifact: `TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_INSTABILITY_20260920T195825Z.json`;
- SHA-256: `sha256:cb402bb3151a59708c6e3b6406323fe8671680b0e2785c9bb92ff47064639442`;
- materialized effective-unit digest: `sha256:33d166b68a337947f7737ae659b386df88545867012ce88d0b30bcdbcf070b3d`;
- post-invocation effective-unit digest: `sha256:c6394ef740c3f66c35e2920ebd4f21d27ff1417d11be5ab93b457f0f7e355c22`;
- `DIGEST_STABLE = False`;
- `CLASSIFICATION = REAL_DEFECT`;
- `TARGET_HOST_ENTRANCE = FAIL / NO_T0`.

The defect is in the frozen implementation's canonicalization of `systemctl show ExecStart`: mutable execution observations are included in the effective-unit digest. The loaded unit bytes and frozen semantic checks otherwise matched.

The historical repository-only Gate A v3 PASS remains attributable only to its prior proof domain. The v3 candidate is no longer eligible for target-host entrance. A corrected candidate requires Builder implementation, exact-head CI, independent review and a new Blue disposition. No proof transfers silently across SHA.


## 13. P14D parallel governance workstream

The fixed rule remains authoritative until explicitly superseded:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

However, Blue's P14D challenge is an ACTIVE governance-method workstream, not out-of-scope reference material.

Method authority input:
`blue/long-horizon-research-2026-09-20@7e0fae86834db7f46ecea5755faf0ac544245399`

Exact-head CI:
`35480999341 = COMPLETED / SUCCESS`

Technical recommendation:
`REPLACE_FIXED_DURATION_WITH_HYBRID_EVIDENCE_CONTRACT`

The candidate hybrid method is:
- accelerated/fault-compressed repository proof;
- destructive target-host entrance proof;
- explicit prospective t0;
- event-based live source window spanning ordinary overnight silence + full weekend + reopen/reconciliation;
- final retrospective audit.

The amendment draft remains non-authoritative. Final Red Team review and an explicit Blue amendment are required before t0.

Material calendar-compression tests are present in the later frozen v3 lineage, so this workstream is not merely abandoned branch-local prose.

The newly observed target-host effective-unit-digest defect is additional evidence for the value of deliberate target-host challenge over passive calendar waiting, but it does not by itself authorize replacing P14D.


## 14. Organizational audit / cleanup execution

Durable audit:
`governance/BLUE_ORGANIZATIONAL_AUDIT_2026-09-20.md`

Execution runbook:
`governance/REPOSITORY_HYGIENE_EXECUTION_RUNBOOK_2026-09-20.md`

Verified during audit:
- 72 live branches;
- registry covers 72/72 live branches;
- 34 delete-ready refs remain exact at pinned SHA, unprotected and non-default;
- 0 open PRs;
- 0 open issues after closing stale historical Phase-0 issue #2;
- repository rulesets = 0;
- stale default branch is 339 commits behind current Blue / 0 ahead;
- default migration remains reviewed but not executed;
- physical branch deletions remain 0.

The server/admin clone is explicitly a second operational role distinct from the P0 qualifying runtime: repository cleanup may be executed from the development clone without mutating `/opt/quant` or `/var/lib/quant-p0`.

Entry-point repairs completed:
- `README.md` now exposes the current governance restart surface;
- `AGENTS.md` routes agents through current Blue governance before runtime snapshots;
- `NEXT_BUILD_MISSION.md` is now a router rather than a stale frozen mission;
- stale issue #2 closed with historical record preserved.


## 15. Gate A v4 reception and independent audit dispatch

Blue reception:
`handoff/BLUE_GATE_A_V4_RECEPTION_2026-09-20.md`

Selected candidate:
`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Builder code-fix SHA:
`0bdd397d7409b01529c1f958c68781499679a95e`

Selected candidate exact-head CI:
`35536353538 = COMPLETED / SUCCESS`

A later Builder documentation-only commit `b10cde0dd193714346abdfe87afb841482e9b7c8` records that CI result but is not the audited candidate. Blue intentionally cuts the documentation/CI recursion at the already-CI-green declared delivery SHA `4d06bdbf...`.

Independent audit:
- branch: `astra/p0-gate-a-v4-independent-audit-2026-09-20`;
- created exactly from `4d06bdbf...`;
- mission: `handoff/ASTRA_GATE_A_V4_MISSION_2026-09-20.md`;
- mission commit: `b636a04b6f8f7786679907d01a4fa22bdfc4e329`.

No Gate A v4 PASS, target-host readiness, t0 or P14D amendment is implied.


## 16. Owner retention override — restaurant branch

`RESTAURANT_BRANCH_RETENTION = KEEP`

Branch:
`claude/restaurant-stock-management-mvp-6oq43e@e083cc70e3f4c2ce31ea04f4fc43be35e9549ab0`

This branch was explicitly removed from the physical-delete batch by owner request on 2026-09-20.

Current physical-delete batch size:
`34`


## 17. P14D final Red Team / active parallel work — 2026-09-21

Durable Red Team:
`governance/BLUE_P14D_FINAL_RED_TEAM_2026-09-21.md`

Prepared amendment candidate:
`governance/BLUE_P14D_HYBRID_AMENDMENT_CANDIDATE_V2_2026-09-21.md`

Current method disposition:
- `FIXED_P14D_UNIQUE_SPECIFIC_ACCEPTANCE_PROPERTY = NONE_FOUND`;
- `RAW_ELAPSED_TIME_RESIDUAL_VALUE = REAL_BUT_UNCALIBRATED`;
- hybrid qualification is recommended for the enumerated P0 properties, while passive-time residual value is preserved through post-qualification surveillance rather than an arbitrary pre-qualification minimum;
- `P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED` until the promotion gates close.

Red Team hardening added:
- `T0_BINDING_MODE = PRECOMMITTED_NEXT_AUTHORIZED_QUALIFYING_LAUNCH` is the recommended anti-selection binding;
- the next single launch event is precommitted before outcomes; its externally attributable UTC timestamp becomes t0;
- ambiguous, missing, duplicate or wrongly bound launch provenance => `NO_T0`;
- after successful Gate D, `P0_POST_QUALIFICATION_SURVEILLANCE = ACTIVE` should preserve the residual value of real elapsed exposure and allow new defects to reopen current eligibility.

Promotion blockers remain:
1. Gate-A fault-matrix closure with no unresolved repository blocker;
2. final independent Gate A v4 review plus Blue disposition;
3. exact candidate/evidence lineage binding;
4. atomic supersession of stale fixed-P14D current checkpoints.

### ACTIVE_PARALLEL_WORK

`BLUE_NOW = FINAL_P14D_METHOD_CLOSURE + AMENDMENT_READINESS + GATE_B/t0_ENTRANCE_PREPARATION`

`BUILDER_NOW = HYBRID_QUALIFICATION_EVIDENCE / FAULT_MATRIX_CONTINUATION`

Durable predecessor Builder checkpoint:
`builder/p0-hybrid-qualification-harness-2026-09-20@d4d446c412258b2a9e4792cdcd9e2442ef24b615` with exact-head run `35541420721 = SUCCESS`.

Any later Codex continuation is counted only after its branch/SHA/evidence appears durably on GitHub.

`ASTRA_NOW = INDEPENDENT_GATE_A_V4_AUDIT`

Current audit branch at this checkpoint:
`astra/p0-gate-a-v4-independent-audit-2026-09-20@b636a04b6f8f7786679907d01a4fa22bdfc4e329`.

`DO_NOT_WAIT_FOR_OTHER_LANES_WHEN_WORK_IS_INDEPENDENT = TRUE`

No lane may infer completion from another lane's green CI or chat claim.


## 18. Gate A v4 independent audit closed — 2026-09-21

Independent Astra final HEAD:
`afe25984b0ddd261fda143d858106c3c71e45149`

Frozen candidate audited:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Exact-head workflows:
- Astra independent audit `35545297473 = COMPLETED / SUCCESS`;
- SEC P0 pre-t0 gate `35545297451 = COMPLETED / SUCCESS`.

Independent verdict:
`AUDIT_GATE_A_V4 = PASS_REPOSITORY_CORRECTION`.

Blue reception:
`handoff/BLUE_GATE_A_V4_FINAL_INDEPENDENT_RECEPTION_2026-09-21.md`.

Blue repository disposition:
`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`.

Accepted non-blocking audit findings:
- one over-named Builder lifecycle test = `TEST_DEFECT / NON_BLOCKING`, independently compensated by Astra A8 + existing authority tests;
- five parser representation limitations = `NON_ISSUE / HYPOTHETICAL_FUTURE_UNIT_LIMITATION` for the exact frozen current unit.

Still not established:
- `TARGET_HOST_READY`;
- Gate B;
- t0;
- P14D hybrid promotion;
- Product integration;
- real-capital authority.

The remaining pre-promotion repository blocker is the separate final Gate-A hybrid fault matrix.


## 19. Current frontier override — 2026-09-21

This section is the latest routing override for any stale historical language above.

Exact V4 candidate:
`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`.

Repository disposition:
`GATE_A_V4_REPOSITORY_DISPOSITION = PASS`.

Independent V4 audit:
`astra/p0-gate-a-v4-independent-audit-2026-09-20@afe25984b0ddd261fda143d858106c3c71e45149`.

Exact-head audit runs:
- `35545297473 = SUCCESS`;
- `35545297451 = SUCCESS`.

Codex fault-matrix package:
- delivery `686f77a383fb0e8c7ecd1b4a737585bedb544701`;
- final checkpoint `e5c4c720e758cd8ab3f0e04faf541b26e204be16`;
- exact-head runs `35544777822 = SUCCESS`, `35545784230 = SUCCESS`;
- Blue reception = `PASS_FOR_INDEPENDENT_REVIEW`.

Independent fault-matrix review branch:
`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`.

Mission dispatch SHA:
`2f6c134f1202c6e22943638379be4e3435ecded0`.

Current blocker:
`FINAL_INDEPENDENT_FAULT_MATRIX_REVIEW = OPEN`.

Exact V4 repository identity already bound:
- Git tree `4d15ef6f471213ee6ab56337b555d2906ef9bf16`;
- verified input-tree digest `sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`;
- exact-head verification artifact id `10612758620`;
- artifact archive digest `sha256:06c690203d589e389847cd345809480da2b99254fe7fd7f38b82c6bf5d54659a`.

Prepared but NON-AUTHORITATIVE operator pack:
- `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_CANDIDATE_2026-09-21.md`;
- `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_CANDIDATE_2026-09-21.md`;
- `governance/P0_T0_PRECOMMIT_TEMPLATE_CANDIDATE_2026-09-21.md`;
- Red Team review `governance/BLUE_GATE_B_T0_OPERATOR_PACK_ADVERSARIAL_REVIEW_2026-09-21.md`.

Current safety state:
- `P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`;
- `TARGET_HOST_READY = FALSE`;
- `GATE_B = NOT_STARTED`;
- `t0 = NOT_DECLARED`;
- `PRODUCT_INTEGRATION = PAUSED`;
- `REAL_CAPITAL_AUTHORIZED = FALSE`.


## 20. Current routing override — context/hygiene reacquisition 2026-09-21

This is the latest routing section and supersedes stale ACTIVE/OPEN wording above.

Current restart checkpoint:
`handoff/BLUE_CONTEXT_REACQUISITION_2026-09-21.md`.

Current hygiene audit:
`governance/BLUE_REPOSITORY_HYGIENE_AUDIT_2026-09-21.md`.

Current branch registry:
`governance/BRANCH_AUTHORITY_REGISTRY_2026-09-21.md`.

Repository facts at this audit:
- default branch = `blue/master-v2-2026-09-20`;
- live branches = `45`;
- open PRs = `0`;
- open issues = `0`;
- protected branches = `0`;
- repository rulesets = `0`;
- prior 34-ref delete batch remains intact;
- deleted refs reappeared = `0`.

Current exact P0 state:
- frozen V4 candidate = `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`;
- `GATE_A_V4_REPOSITORY_DISPOSITION = PASS`;
- final fault-matrix independent review =
  `astra/p0-hybrid-fault-matrix-independent-review-2026-09-21@c6be804e99e409ab36a455f09ea2fccbe3d88252`;
- `ASTRA_FAULT_MATRIX = BLOCKED_MISSING_PROOF`;
- production `REAL_DEFECT = 0`;
- unresolved repository `MISSING_PROOF = 1`;
- blocking row = `restart_burst_limit`.

Current active Builder mission:
`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`.

Prepared mission SHA:
`6f0ca1d858d6937dc8199cc1690dce049ddb79a6`.

Blue repair contract:
`governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md`.

Prepared targeted independent recheck:
`governance/BLUE_ASTRA_RESTART_BURST_TARGETED_RECHECK_SPEC_2026-09-21.md`.

Prepared final consistency precheck:
`governance/BLUE_HYBRID_PROMOTION_FINAL_CONSISTENCY_PRECHECK_2026-09-21.md`.

Current next sequence:
Builder delivery + exact-head CI -> Blue reception -> targeted Astra recheck -> Blue final fault-matrix disposition -> final consistency review -> possible hybrid promotion.

No new branch deletion is authorized during this proof-repair cycle.

Safety remains:
- `P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`;
- `P14D_PROMOTION_READY = FALSE`;
- `TARGET_HOST_READY = FALSE`;
- `GATE_B_MUTATION_AUTHORIZED = FALSE`;
- `GATE_B = NOT_STARTED`;
- `t0 = NOT_DECLARED`;
- `PRODUCT_INTEGRATION = PAUSED`;
- `REAL_CAPITAL_AUTHORIZED = FALSE`.


## W. RESTART-BURST BUILDER DELIVERY OBSERVED — 2026-09-21

Builder proof-repair branch now has an exact delivery:
`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21@1fa82a75485661bf9bbb3de10b925126397dfec5`.

Blue scope/design inspection:
- proof/evidence/handoff paths only;
- `PRODUCTION_CODE_CHANGED = FALSE`;
- independent oracle = literal `EXPECTED_RESTART_BURST_LIMIT = 5` with Blue provenance;
- M1 launcher-only 5->4 = RED;
- M2 unit-only 5->4 = RED;
- M3 launcher+unit simultaneous 5->4 = RED;
- matrix = 19 rows / 15 existing / 4 new / 0 missing / 0 real defects.

Blue reception:
`handoff/BLUE_RESTART_BURST_PROOF_REPAIR_RECEPTION_2026-09-21.md`.

Current reception state:
`PRELIMINARY_PASS / PENDING_EXACT_HEAD_CI`.

Exact-head CI:
`35549017908 = IN_PROGRESS` at last observation.

Do not dispatch the targeted Astra recheck until this exact-head run is
`COMPLETED / SUCCESS` and branch HEAD remains exactly `1fa82a75485661bf9bbb3de10b925126397dfec5`.


## X. TARGETED ASTRA RECHECK PRESTAGED — 2026-09-21

Owner authorized reversible anticipation while Builder exact-head CI remains in progress.

Prestaged Astra branch:
`astra/p0-restart-burst-proof-recheck-2026-09-21`.

Audit input base:
`1fa82a75485661bf9bbb3de10b925126397dfec5`.

Mission-only prestage commit:
`b922a108ddf906ff9a2a0c6f3c9800b76b754631`.

This is NOT audit evidence yet.

Activation condition:
`Builder run 35549017908 = COMPLETED / SUCCESS` and Builder branch still points to `1fa82a75485661bf9bbb3de10b925126397dfec5`.

If CI fails or Builder HEAD moves, abandon/rebase this prestage. No PASS or promotion may use it.


## 18. HYBRID PROMOTION — CURRENT AUTHORITY OVERRIDE — 2026-09-21

Exact closure:
- Builder repair `1fa82a75485661bf9bbb3de10b925126397dfec5`, CI `35549017908 = SUCCESS`;
- Astra targeted `61facacdcdc499bd3e6680644c75c97fcff22656`, CI `35551073229 = SUCCESS`;
- Astra verdict `PASS_REPOSITORY_EVIDENCE`;
- Blue reception `0f4d6227c129a53793fb186db6a618d2a453e3ee`;
- final consistency `PASS`.

Current method:
`governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md`

Current state:
```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
P14D_GOVERNANCE_STATUS = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION
GATE_A_V4_REPOSITORY_DISPOSITION = PASS
FINAL_INDEPENDENT_FAULT_MATRIX_REVIEW = PASS
UNRESOLVED_REPOSITORY_MISSING_PROOF = 0
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Next: seal one concrete Gate-B activation artifact. The authority pack alone does not authorize mutation.

## 20. LATEST ROUTING OVERRIDE — F11 FRONTIER — 2026-09-21

This section supersedes stale active-frontier language above.

Latest durable restart surface:

`handoff/BLUE_CONTEXT_REACQUISITION_F11_2026-09-21.md`

Current Blue predecessor verified before this override:

`51981f490a4d51b969ab5694c9480a417c7f0418`

Exact-head CI:

`35603155680 = COMPLETED / SUCCESS`

Gate-B run-authority integrated candidate:

`blue/gate-b-run-authority-repair-integration-2026-09-21@644da76eb0227be275b8e3448118dac0cc7096ca`

Independent Astra final recheck:

`astra/gate-b-run-authority-mechanisms-recheck-2026-09-21@41c3f291f46b7b5849bdb702c09ccefbeecde691`

Final verdict:

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECT_LOCK_PATH_IDENTITY`

A1-A10 are independently GREEN after repair. The remaining repository blocker is:

`F11 = REAL_DEFECT / LOCK_PATH_IDENTITY`

No second repository blocker was independently established by the final Astra handoff.

Antigravity Product prestage is complete:

`parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21@568eea1e028302e14f96a06eb2515bb89aa73ad4`

`ANTIGRAVITY_VERTICAL_PRESTAGE = READY_FOR_BLUE_REVIEW`

It is accepted as planning input only. Product integration remains paused.

Current project state:

```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
GATE_A_V4_REPOSITORY_DISPOSITION = PASS
F11_REPAIR_REQUIRED = TRUE
PASS_REPOSITORY_EVIDENCE = FALSE
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Next action:

`BLUE -> DISPATCH_BOUNDED_F11_REPAIR`

Recommended future repair branch:

`builder/gate-b-f11-lock-identity-repair-2026-09-21`

That branch does not yet exist at this override.

Required flow:

`Blue dispatch -> Builder F11 repair -> exact-head green CI -> Blue integration -> independent Astra F11 + A1-A10 non-regression recheck -> only then possible return to Gate-B activation`.

Do not reopen F1, F5, V4 materialization prestage, or A1-A10 by default.

## 21. F11 BUILDER RECEPTION OVERRIDE — PARENT-PATH CLOSURE REQUIRED

Latest Blue checkpoint:

`handoff/BLUE_F11_BUILDER_RECEPTION_PENDING_PARENT_PATH_2026-09-21.md`

Builder final handoff currently observed:

`builder/gate-b-lock-path-identity-repair-2026-09-21@6ec12cd73de24b4a789d6abe9e292d8b616e3da1`

Implementation checkpoint:

`ed51cc4251f556482eca18e396cc1c0d932879fb`

CI:

`35608538693 = COMPLETED / SUCCESS`

Handoff-head CI:

`35610033532 = IN_PROGRESS` at this override.

Blue does not yet authorize Astra.

Reason:

`F11_PARENT_PATH_IDENTITY_CHALLENGE = OPEN`

Required repository-local discriminants:

- F11-P1 whole-parent-path replacement during a live Registry critical section;
- F11-P2 no mutation by rejected replacement-parent contender;
- F11-P3 deterministic recovery/fail-closed post-condition.

Current routing:

```text
BUILDER_F11_HANDOFF_RECEIVED = TRUE
BUILDER_F11_ACCEPTED_FOR_ASTRA = FALSE
ASTRA_F11_RECHECK_AUTHORIZED = FALSE
RETURN_CONTROL_TO = BUILDER_F11_PARENT_PATH_CLOSURE
PASS_REPOSITORY_EVIDENCE = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

Antigravity Product prestage remains complete and parked.


## LATEST ROUTING OVERRIDE — 2026-09-21 / TWO-RAIL CONVERGENCE

This section supersedes older routing/frontier language in this file where inconsistent.

Authoritative current reacquisition checkpoint:

`handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md`

Creation commit:

`c248f23cae8d579261a3f43c6aca78463eccae92`

Current global safety:

```text
GATE_A_V4_REPOSITORY_DISPOSITION = PASS
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Current active frontier is exactly two rails:

### Rail A — F11 / Gate-B critical path

Final Builder:

`builder/gate-b-lock-path-identity-repair-2026-09-21@e600295b2aa7056e8176e0286f9d67f5c65b1c11`

Exact-head CI:

`35617257622 = COMPLETED / SUCCESS`

Blue final integration candidate:

`blue/gate-b-f11-final-integration-2026-09-21@4f26c1f015efb8c3530aeba8b3f87a81b0361a3f`

Current integration CI at this checkpoint:

`35619545254 = IN_PROGRESS`

Therefore:

```text
PASS_FOR_INDEPENDENT_ASTRA_RECHECK = PENDING_EXACT_HEAD_CI
ASTRA_F11_RECHECK_AUTHORIZED = FALSE
```

The intended Astra branch does not yet exist durably and must be created only by Blue
after exact-head integration CI success.

### Rail B — Product/Economic pre-big-build

Build-prep received:

`parallel/claude-post-p0-vertical-build-prep-2026-09-21@ce8b1ffe1e09d58162d96f52bea3b10aac1fb6ec`

Adversarial challenge received:

`claude/confident-mendel-h4qqo4@9e6431dedaa621d58218f6ffb09ed1300de1bd1b`

Blue consolidated correction authority:

`governance/BLUE_POST_P0_VERTICAL_PREBIGBUILD_CORRECTION_SPEC_2026-09-21.md`

Current remaining prerequisite:

`REAL_RESEARCH_TO_FROZEN_EFFECT_ESTIMATE = MISSING_SCIENTIFIC_OUTPUT_CONTRACT`

Active science-prestage branch:

`parallel/claude-research-frozen-effect-estimate-prestage-2026-09-21@866e6c1e96ab7460a7cd6464ead922e710ce7b0b`

Do not dispatch Product implementation until the scientific contract is received and
Blue freezes one final vertical-loop build specification.

Next Product implementation policy:

`ONE LARGE BOUNDED BUILD`, not several small competing Builders.

For all exact sequencing, read:
`handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md`.
