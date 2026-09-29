# Rangement proposé (non exécuté)

Statut : **PROPOSÉ**. Aucun fichier n'a été déplacé. Cette liste classe chaque document de `governance/` et `handoff/`, ainsi que les documents racine, sur la branche `blue/master-v2-2026-09-20` (commit bd061dc).

- **Action proposée** : déplacer les lignes SUPERSEDED et HISTORICAL vers `archive/<même chemin>` avec `git mv`, qui conserve l'historique. Réécrire ensuite les liens `governance/X` et `handoff/X` restants en `archive/...`. Rien n'est supprimé.
- **Garde-fou vérifié** : aucun fichier listé ici n'est référencé par le code, les tests, la CI ou les scripts. Les fichiers `.json` et `.py` lus par le code (`handoff/*.json`, schéma Gate B, fixtures, script discriminant) restent tous en place.
- **Méthode** : 3 classements indépendants (sous-agents), avec la règle « en cas de doute, LIVE ». La liste est donc conservatrice.

## SUPERSEDED (58)

| Fichier | Raison |
|---|---|
| `governance/BLUE_ANTIGRAVITY_HIGH_VALUE_PRODUCT_PRESTAGE_2026-09-21.md` | Prestage allocation; replaced by BLUE_FIRST_VERTICAL_ONE_BIG_BUILD_FROZEN_SPEC_2026-09-21.md |
| `governance/BLUE_CLAUDE_POST_P0_VERTICAL_BUILD_PREP_2026-09-21.md` | Build prep; replaced by BLUE_FIRST_VERTICAL_ONE_BIG_BUILD_FROZEN_SPEC_2026-09-21.md |
| `governance/BLUE_D05_D07_GOVERNANCE_PACKET_2026-09-15.md` | Status superseded by BLUE_D05_D09_ROUTE_B_CHECKPOINT_2026-09-17.md |
| `governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_CANDIDATE_2026-09-21.md` | Candidate; replaced by BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md |
| `governance/BLUE_GATE_B_F5_ROUTE1_HOST_EVIDENCE_CLOSURE_2026-09-21.md` | Closure mission; result in BLUE_GATE_B_F5_ROUTE1_RECEPTION_2026-09-21.md |
| `governance/BLUE_GATE_B_F5_ROUTE1_HOST_FEASIBILITY_SPEC_2026-09-21.md` | Feasibility spec closed; result in BLUE_GATE_B_F5_ROUTE1_RECEPTION_2026-09-21.md |
| `governance/BLUE_GATE_B_PARALLEL_PREPARATION_DISPATCH_2026-09-21.md` | Closed dispatch; state now in CURRENT_GOVERNANCE_STATE_2026-09-20.md |
| `governance/BLUE_GATE_B_TO_T0_ENTRANCE_BINDING_SPEC_2026-09-21.md` | Pre-hybrid P14D binding; replaced by TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md |
| `governance/BLUE_HYBRID_P0_ATOMIC_PROMOTION_TRANSACTION_PLAN_2026-09-21.md` | Promotion done; see P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md |
| `governance/BLUE_HYBRID_P0_PRE_PROMOTION_EVIDENCE_BINDER_2026-09-21.md` | Promotion done; see P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md |
| `governance/BLUE_HYBRID_PROMOTION_ATOMIC_DRY_RUN_2026-09-21.md` | Dry run; promotion executed per BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md |
| `governance/BLUE_HYBRID_PROMOTION_FINAL_CONSISTENCY_PRECHECK_2026-09-21.md` | Precheck; promotion executed per BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md |
| `governance/BLUE_P0_POST_ASTRA_GREEN_EXECUTION_CONTROL_PLAN_2026-09-21.md` | Replaced by BLUE_GATE_B_FINAL_ACTIVATION_CONVERGENCE_PACK_2026-09-21.md |
| `governance/BLUE_P14D_HYBRID_AMENDMENT_CANDIDATE_V2_2026-09-21.md` | Candidate; replaced by P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md |
| `governance/BLUE_POST_P0_VERTICAL_SHADOW_LOOP_PRESTAGE_PLAN_2026-09-21.md` | Replaced by BLUE_FIRST_VERTICAL_ONE_BIG_BUILD_FROZEN_SPEC_2026-09-21.md |
| `governance/BLUE_ROUTE_B_NONOVERLAP_THINNING_COMMON_TARGET_CHECKPOINT_ADDENDUM_2026-09-18.md` | Thinning replaced by BLUE_ROUTE_B_PHASE_COMPLETE_PERSISTENCE_CHECKPOINT_ADDENDUM_2026-09-18.md |
| `governance/BLUE_ROUTE_B_PHASE_COMPLETE_PERSISTENCE_CHECKPOINT_ADDENDUM_2026-09-18.md` | Phase retired by BLUE_ROUTE_B_DIRECT_FULL_SUPPORT_SINGLE_UCB_CHECKPOINT_ADDENDUM_2026-09-18.md |
| `governance/BLUE_ROUTE_B_Q_DOMAIN_STABILITY_UNDERPOWERED_CHECKPOINT_ADDENDUM_2026-09-17.md` | q-domain replaced by BLUE_ROUTE_B_LIQUIDITY_BREACH_FREQUENCY_CHECKPOINT_ADDENDUM_2026-09-17.md |
| `governance/BLUE_TARGET_HOST_RUNBOOK_RECONCILIATION_PLAN_2026-09-21.md` | Reconciled into TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md |
| `governance/BLUE_WORK_ALLOCATION_PRE_GREEN_TO_ECONOMIC_LOOP_2026-09-21.md` | Allocation replaced by CURRENT_GOVERNANCE_STATE_2026-09-20.md rails |
| `governance/BRANCH_AUTHORITY_REGISTRY_2026-09-20.md` | Replaced by BRANCH_AUTHORITY_REGISTRY_2026-09-21.md |
| `governance/BRANCH_AUTHORITY_REGISTRY_2026-09-21.md` | Current branch routing in GITHUB_BRANCH_HYGIENE_2026-09-21.md |
| `governance/D05A_D09_NONOVERLAP_THINNING_COMMON_CALIBRATION_TARGET_CONTRACT_2026-09-18.md` | Thinning retired by D05A_D09_DIRECT_FULL_SUPPORT_SINGLE_ROBUST_UCB_SIMPLIFICATION_AMENDMENT_2026-09-18.md |
| `governance/D05A_D09_PHASE_COMPLETE_ENSEMBLE_AND_PERSISTENCE_MATERIALITY_AMENDMENT_2026-09-18.md` | Phase decomposition retired by D05A_D09_DIRECT_FULL_SUPPORT_..._2026-09-18.md |
| `governance/D05A_D09_Q_DOMAIN_VALUE_STABILITY_AND_UNDERPOWERED_PROTOCOL_AMENDMENT_2026-09-17.md` | q-selection retired by D05A_D09_LIQUIDITY_BREACH_FREQUENCY_AND_Q_SELECTION_RETIREMENT_AMENDMENT |
| `governance/D08_EXTERNAL_LOWER_BOUND_TRANSPORT_CONTRACT.md` | Self-marked superseded; Route A retired by BLUE_POWER_ROUTE_B_DECISION_2026-09-17.md |
| `governance/D08_POWER_FLOOR_OUTCOME_TRANSFORM_BOUNDARY.md` | Self-marked superseded; Route A retired by BLUE_POWER_ROUTE_B_DECISION_2026-09-17.md |
| `governance/D09_MEUE_POWER_FLOOR_DERIVATION_DEPENDENCY.md` | Replaced by D09_ECONOMIC_CORE_EC1 and D09_ROUTE_B_COMMON_CORE_REMAINDER |
| `governance/P0_T0_PRECOMMIT_TEMPLATE_CANDIDATE_2026-09-21.md` | Candidate promoted to P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md |
| `governance/POST_GATE_A_BRANCH_DELETE_BATCH_2026-09-20.md` | Consolidated into BRANCH_DELETE_READY_INDEX_2026-09-20.md (executed) |
| `governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_CANDIDATE_2026-09-21.md` | Promoted to TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md |
| `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_CANDIDATE_2026-09-21.json` | v2 candidate replaced by TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json |
| `governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_CANDIDATE_2026-09-21.md` | Promoted to TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md |
| `governance/TARGET_HOST_P0_RODAGE_RUNBOOK_2026-09-20.md` | Stale V3 runbook; replaced by TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md |
| `governance/TARGET_HOST_RODAGE_ENTRANCE_CONTRACT_2026-09-20.md` | Stale V3 contract; replaced by TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md |
| `governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_CANDIDATE_2026-09-21.md` | Promoted to TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md |
| `handoff/BLUE_ANTIGRAVITY_AUXILIARY_PRECHECK_DISPATCH_2026-09-21.md` | Superseded by BLUE_ANTIGRAVITY_ALLOCATION_UPDATE_2026-09-21.md |
| `handoff/BLUE_ASTRA_F11_RECEPTION_PENDING_EXACT_HEAD_CI_2026-09-21.md` | Superseded by BLUE_FINAL_F11_REPOSITORY_CLOSURE_2026-09-21.md |
| `handoff/BLUE_ASTRA_HYBRID_FAULT_MATRIX_FINAL_RECEPTION_PREPARED_2026-09-21.md` | Pending-CI prep; superseded by BLUE_ASTRA_RESTART_BURST_FINAL_RECEPTION + hybrid promotion |
| `handoff/BLUE_ASTRA_RESTART_BURST_FINAL_RECEPTION_TEMPLATE_2026-09-21.md` | Template; superseded by BLUE_ASTRA_RESTART_BURST_FINAL_RECEPTION_2026-09-21.md |
| `handoff/BLUE_CLAUDE_POST_P0_VERTICAL_BUILD_PREP_RECEPTION_2026-09-21.md` | Build prep; superseded by BLUE_FIRST_VERTICAL_BUILDER_RECEPTION_2026-09-21.md |
| `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-21.md` | Superseded by BLUE_CONTEXT_REACQUISITION_F11 and BLUE_PROJECT_REACQUISITION_2026-09-21 |
| `handoff/BLUE_F11_BUILDER_RECEPTION_PENDING_PARENT_PATH_2026-09-21.md` | Superseded by BLUE_FINAL_F11_REPOSITORY_CLOSURE_2026-09-21.md |
| `handoff/BLUE_GATE_A_V3_FINAL_DISPOSITION_2026-09-20.md` | Superseded by BLUE_GATE_A_V4_FINAL_INDEPENDENT_RECEPTION_2026-09-21.md |
| `handoff/BLUE_GATE_A_V3_POST_ASTRA_RECEPTION_2026-09-20.md` | Superseded by BLUE_GATE_A_V3_FINAL_DISPOSITION (itself replaced by v4) |
| `handoff/BLUE_GATE_A_V4_BUILDER_RECEPTION_PENDING_2026-09-20.md` | Superseded by BLUE_GATE_A_V4_RECEPTION_2026-09-20.md |
| `handoff/BLUE_GATE_A_V4_RECEPTION_2026-09-20.md` | Superseded by BLUE_GATE_A_V4_FINAL_INDEPENDENT_RECEPTION_2026-09-21.md |
| `handoff/BLUE_GATE_B_F11_PASS_FOR_INDEPENDENT_ASTRA_RECHECK_2026-09-21.md` | Superseded by BLUE_FINAL_F11_REPOSITORY_CLOSURE_2026-09-21.md |
| `handoff/BLUE_GATE_B_RUN_AUTHORITY_ASTRA_RECEPTION_2026-09-21.md` | Blockers repaired; superseded by BLUE_GATE_B_RUN_AUTHORITY_REPAIR_INTEGRATION_RECEPTION |
| `handoff/BLUE_MASTER_CONSOLIDATION_2026-09-20.md` | Superseded by BLUE_MASTER_ORCHESTRATOR then BLUE_MASTER_V2_STATE |
| `handoff/BLUE_MASTER_ORCHESTRATOR_2026-09-20.md` | Superseded by BLUE_MASTER_V2_STATE_2026-09-20.md |
| `handoff/BLUE_MASTER_PROJECT_CHECKPOINT_2026-09-20.md` | Superseded by BLUE_MASTER_V2_STATE_2026-09-20.md |
| `handoff/BLUE_NEW_CONVERSATION_RESUME_PROMPT_2026-09-21.md` | Stale override; superseded by BLUE_PROJECT_REACQUISITION_2026-09-21 + CURRENT_GOVERNANCE_STATE |
| `handoff/BLUE_RESTART_BURST_PROOF_REPAIR_RECEPTION_2026-09-21.md` | Preliminary; superseded by BLUE_ASTRA_RESTART_BURST_FINAL_RECEPTION_2026-09-21.md |
| `handoff/BLUE_S11_METHODS_CHALLENGE_DISPATCH_2026-09-21.md` | Superseded by BLUE_S11_METHODS_CHALLENGE_RECEPTION_2026-09-21.md |
| `handoff/BLUE_TARGET_HOST_QUALIFICATION_MISSION_2026-09-20.md` | v3-based mission; superseded by BLUE_TARGET_HOST_READ_ONLY_REBIND_RECEPTION_2026-09-21.md |
| `handoff/BLUE_TARGET_HOST_READ_ONLY_REBIND_ACCESS_BLOCKER_RECEPTION_2026-09-21.md` | Superseded by BLUE_TARGET_HOST_READ_ONLY_REBIND_RECEPTION_2026-09-21.md |
| `handoff/QUANT_BLUE_HANDOFF_2026-09-15.md` | Early conversation memory; superseded by BLUE_MASTER_V2_STATE_2026-09-20.md |

## HISTORICAL (31)

| Fichier | Raison |
|---|---|
| `governance/BLUE_ASTRA_RESTART_BURST_TARGETED_RECHECK_SPEC_2026-09-21.md` | Closed recheck; hybrid P0 qualification now promoted |
| `governance/BLUE_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_REPAIR_SPEC_2026-09-21.md` | F1 repair closed; recorded in BLUE_GATE_B_F1_LANEA_RECEPTION_2026-09-21.md |
| `governance/BLUE_GATE_B_F11_BRANCH_RECONCILIATION_PARENT_PATH_CHALLENGE_2026-09-21.md` | F11 closed per CURRENT_GOVERNANCE_STATE do-not-reopen list |
| `governance/BLUE_GATE_B_F11_LOCK_IDENTITY_REPAIR_SPEC_2026-09-21.md` | F11 repository defect CLOSED per CURRENT_GOVERNANCE_STATE |
| `governance/BLUE_GATE_B_F1_LANEA_RECEPTION_2026-09-21.md` | Closed F1 reception record; F1 closed in CURRENT_GOVERNANCE_STATE |
| `governance/BLUE_GATE_B_F5_ROUTE1_RECEPTION_2026-09-21.md` | Closed F5 reception record; F5 CLOSED, do-not-reopen |
| `governance/BLUE_HYBRID_PROPERTY_COVERAGE_RECONCILIATION_2026-09-21.md` | Pre-promotion reconciliation; hybrid V1 now in force |
| `governance/BLUE_ORGANIZATIONAL_AUDIT_2026-09-20.md` | Completed audit; routing now in CURRENT_GOVERNANCE_STATE |
| `governance/BLUE_P14D_FINAL_RED_TEAM_2026-09-21.md` | P14D red team; P14D superseded by hybrid amendment |
| `governance/BLUE_P14D_HYBRID_PROMOTION_CHECKLIST_2026-09-21.md` | Promotion COMPLETE; closed record |
| `governance/BLUE_REPOSITORY_HYGIENE_AUDIT_2026-09-21.md` | Completed audit; hygiene now in GITHUB_BRANCH_HYGIENE_2026-09-21.md |
| `governance/BLUE_RESTART_BURST_PROOF_REPAIR_SPEC_2026-09-21.md` | Closed repair; hybrid P0 qualification promoted |
| `governance/BRANCH_CLEANUP_PLAN_2026-09-20.md` | Executed cleanup plan; closed record |
| `governance/BRANCH_DELETE_BATCH_2026-09-20.md` | Executed delete batch; closed record |
| `governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md` | Executed/closed deletion manifest; current hygiene in GITHUB_BRANCH_HYGIENE_2026-09-21.md |
| `governance/DEFAULT_BRANCH_MIGRATION_REVIEW_2026-09-20.md` | Default-branch migration executed/verified; no current use |
| `governance/OPEN_PR_DISPOSITION_2026-09-20.md` | Gate A v3-era PR snapshot; branch state now in GITHUB_BRANCH_HYGIENE |
| `governance/P0_GATE_A_EVIDENCE_INDEX_2026-09-20.md` | Gate A v2/v3 forensic index; Gate A V4 PASS closed |
| `governance/POST_GATE_A_PROOF_REF_REVIEW_2026-09-20.md` | Closed ref classification review; deletions executed |
| `governance/REPOSITORY_HYGIENE_EXECUTION_RUNBOOK_2026-09-20.md` | Runbook executed/complete; no current use |
| `handoff/ASTRA_GATE_A_V3_MISSION_2026-09-20.md` | Gate A v3 Astra audit mission; v3 closed, replaced by v4 |
| `handoff/ASTRA_P0_CHECKPOINT.md` | 2026-09-19 pre-t0 Astra checkpoint, pre-V4; closed record |
| `handoff/ASTRA_PRE_T0_FINDINGS.md` | Intermediate pre-t0 falsification record; defects fixed long ago |
| `handoff/BLUE_ANTIGRAVITY_ALLOCATION_UPDATE_2026-09-21.md` | Antigravity allocation decision; lane work delivered and closed |
| `handoff/BLUE_CHECKPOINT_2026-09-18_P0_CONTINUITY.md` | 2026-09-18 P0 continuity checkpoint; replaced by master V2 state |
| `handoff/BLUE_GATE_A_V3_RECEPTION_2026-09-20.md` | Gate A v3 builder reception; v3 replaced by v4 |
| `handoff/BLUE_GOVERNANCE_REFERENCE_REPAIR_2026-09-20.md` | One-off missing-path repair record, closed |
| `handoff/BLUE_REPOSITORY_HYGIENE_EXECUTION_2026-09-20.md` | Completed branch cleanup record; closed |
| `handoff/BLUE_TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_2026-09-20.md` | v3 target-host defect; fixed by Gate A v4 |
| `handoff/CODEX_P0_CONTINUATION.md` | Old Codex handoff for astra pre-t0 branch; closed |
| `V1_RED_TEAM_REPORT.md` | Closed V1 red-team review record; no references |

## LIVE (126) : conservés en place

Ce sont les contrats et specs du rail sûr en vigueur, l'autorité courante, les documents produit, et tout ce que lisent le code, les tests ou la CI.

## Incohérences relevées, hors déplacement

- **Ordre de lecture divergent** : `README.md` et `AGENTS.md` citent d'abord `BLUE_CONTEXT_REACQUISITION_F11_2026-09-21`, alors que `CLAUDE.md` et `CLAUDE_CURRENT_MISSION.md` citent la version du 2026-09-20. Il faut les unifier sur `BLUE_PROJECT_REACQUISITION_2026-09-21`, le plus récent.
- **`CODEX.md`** répète largement `AGENTS.md`. On peut l'archiver si Codex n'est plus utilisé comme builder.
- **`CLAUDE_CURRENT_MISSION.md`** et **`NEXT_BUILD_MISSION.md`** sont deux routeurs de mission. Réduire le premier à un simple pointeur.
- **`RUNTIME.md`** (design) et **`RUNTIME_RUNBOOK.md`** (commandes) se recouvrent. On peut fusionner le design dans le runbook.
- **Branches** : le dépôt en a 92. Le nettoyage des branches suit `governance/GITHUB_BRANCH_HYGIENE_2026-09-21.md`. C'est une suppression irréversible : elle reste au propriétaire.
