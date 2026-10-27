# CP02 retrospective integrity audit

FACT: Audit compares CP02 a06fa2d7c79f6b562101e15f555cb56bb1d025fe with fixed W2 ebc72b9fd14f91420c37e0b7607f9bfb584a289a and executes probes against resume HEAD 40c590189e1389502d179e63f6e0925df8513d2c. No tracked or product file was edited. Synthetic test data only; no production objects, outcomes, proposals, roots or exposure were mutated.

## Retention decision

RECOMMENDATION: Retain four CP02 guards individually as RETAIN_SAFETY_CRITICAL. They protect existing universal safety invariants through small local validation additions across three existing V2 files, without new mutation owner, ledger, schema or architecture. None is required to make UST execute; universal retention exception is the justification. Retention is based on direct differential witnesses, not source branch recency or sunk cost. Current C0 gap means the resulting target is nevertheless NOT_QUALIFIED unless separately resolved under lawful scope.

## CP02-TRIAL-PROPOSAL — RETAIN_SAFETY_CRITICAL

FACT: Generic run_pre_outcome_pipeline checks labels and validator candidate hash, but never joins candidate subject/hash to generated_proposals. Native manual source binding exists at W2 v2_stage_executor.py:138-147 and is narrower coverage.

FACT: W2 accepts generated_proposals=[{id:UNATTRIBUTED_SYNTHETIC}], target rejects TRIAL_PROPOSAL_BINDING_MISMATCH. Exact seam: v2_core.py:282-307 + v2_pipeline.py:73 + native helper reuse. Test: `tests.test_research_os_trial_proposal_export_binding`.

INFERENCE: Attribution cannot be manufactured by copying trial IDs; generic export path must preserve subject/proposal relation. Native refactor is equivalent reuse, not new protection.

## CP02-MODEL-ADMISSION — RETAIN_SAFETY_CRITICAL

FACT: W2 assert_model_allowed checks only Python membership; None in [None] admits unattributable identity. W2 pure pipeline does not call model policy admission for recorded generator or validator. v2_state store model admission covers its own actor only.

FACT: W2 accepts out-of-policy recorded trial model and direct null membership; target rejects MODEL_OUTSIDE_EPOCH_POLICY / MODEL_INVALID_IDENTIFIER:model_identity. Exact seam: v2_core.py:126-127,180-183 + v2_pipeline.py:77-78. Test: `tests.test_research_os_epoch_model_admission`.

INFERENCE: Recorded actor identities must remain attributable and policy bound. Frozen allowed model list and existing epoch remain owners.

## CP02-TRIAL-EPOCH-WINDOW — RETAIN_SAFETY_CRITICAL

FACT: W2 native executor checks current now against window, but generic and native lineages do not verify persisted trial.generated_at membership. Valid hash permits a trial from before epoch.

FACT: W2 accepts generated_at=2026-10-19T00:00:00Z before research_window start; target rejects TRIAL_OUTSIDE_EPOCH_RESEARCH_WINDOW. Exact seam: v2_core.py:165-177 + v2_pipeline.py:74 + v2_stage_executor.py:140-143. Test: `tests.test_research_os_trial_epoch_window`.

INFERENCE: Preserve half-open epoch membership without changing existing epoch or trial identity owners; independent native rehashed-trial attacks executed.

## CP02-SERIALIZABLE-OUTCOME — RETAIN_SAFETY_CRITICAL

FACT: Both W2 recursive membranes traverse list but not tuple although canonical JSON treats both as arrays. Tuple can hide forbidden synthetic outcome field while JSON roundtrip exposes same content.

FACT: W2 accepts export.review_context=({outcome:SYNTHETIC_MARKER},); target rejects OUTCOME_DATA_VISIBLE_TO_RESEARCH before export. Exact seam: v2_core.py:351 and v2_pipeline.py:42 list/tuple traversal. Test: `tests.test_research_os_serializable_outcome_membrane`.

INFERENCE: Equivalent serializable inputs require equal fail-closed disposition; same pre-outcome owner, two tiny recursive-branch edits.

## CP02-C0-REUSE-ASSESSMENT — SEPARATE_MISSION_REQUIRED

FACT: Preserved C0 kernel counts structural primary-source reconstruction as independent confirmation despite explicit semantic review NOT_PROVEN. Public C2 adapter delegates unchanged, then propagates count into adjudication.

FACT: /tmp/oneshot_c0_current_attack.py test fails 1 != 0 on exact target; validates structural PASS and explicit NOT_PROVEN before count assertion.. Exact seam: scientific_adjudication.py:269-274 delegates _scientific_adjudication_c0.py:419-431, final count propagation:612-614. Test: `/tmp/oneshot_c0_current_attack.py`.

INFERENCE: Current applicable failure blocks qualification; prior blanket C0 KEEP equivalence conclusion requires correction. Latest C0 selected semantic counting repair is evidence, not ownership authority.

## Direct proof and execution evidence

FACT: `/tmp/oneshot_cp02_runs/w2_gap_probes.log` records valid baseline plus all five attacked cases ACCEPTED in a temporary archive of exact W2. `/tmp/oneshot_cp02_runs/target_gap_probes.log` records valid baseline accepted and all five attacked cases REJECTED on target. `/tmp/oneshot_cp02_probe.py` is the reproducible probe. No new fixtures or tests were imported into product execution. Those probes use the already strengthened synthetic CP02 fixture for both W2 and target, controlling for fixture content.

FACT: Focused retained and current-invariant tests ran 61 cases: 60 pass; one stale golden fails. The old clean-blinded test expects receipt `01fa1c77d95dbe81b9366264629a9e0bdcf24eefc03835a04796cbfc509c30ec`, but CP02 intentionally attributed P1 with hypothesis_id+generation_id+candidate_hash, changing trial and receipt hashes to `48ec56afa0be00bcd198c38a37b49c89f2b0d00d05b7f055346e887f7b2480e8`. Exact W2 implementation with old W2 fixture emits old hash; same exact W2 implementation with CP02 fixture emits new hash. `/tmp/oneshot_cp02_runs/receipt_golden_proof.log`. Classification STALE_FIXTURE; permitted test correction does not authorize any product change.

FACT: Commands, environment, HEAD, start/end, result and log references are in `/tmp/oneshot_cp02_runs/TEST_RUNS.json`. The first unrecorded quick exploratory 18-case unittest pass was repeated within the fully recorded 61-case run. These are audit-stage results, not final exact-head qualification.

## Current C0 hostile failure: scientific consequence and limits

FACT: The source attack is exact immutable latest C0 `6dc84f35e80aec709e67e3d5d3ce0cdcfaee3bcf:tests/test_mega_c0_scientific_adjudication.py:305-309`, with complete composed result assertion at lines353-362. Challenger `642b551985f499b37286c3bc21b89c57294f63ca:architecture-review/14_SCIENTIFIC_QUALITY_AND_DENOMINATORS.md` independently documents it. Both were treated as attack pointers, not semantic authority.

FACT: Target's own `tests/test_wave2_c2_scientific_adjudication.py:145-154` fixture explicitly declares `cognitive_scope=DETERMINISTIC_STRUCTURAL_CHECKS_ONLY` and `semantic_diverse_review=NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED`. Target public adapter `bind_independence_ref` delegates unchanged to the preserved historical kernel, which computes count 1 solely from structural flags and PRIMARY_SOURCE_RECONSTRUCTION. `validate_independence_ref` accepts this and composed adjudication retains count 1. Target outer C2 adapter appends claim ceiling but leaves count 1 untouched. `/tmp/oneshot_c0_current_attack.py` reproduces using target fixtures and fails expected zero; full ref and composed output are captured in `/tmp/oneshot_cp02_runs/c0_current_attack.log`.

INFERENCE: This is CURRENT_INVARIANT, not stale fixture or superseded contract: explicitly unproven semantic review cannot establish an independent scientific confirmation. Structural PASS remains meaningful and need not change; only confirmation count is overstated. The fact that target C2 adapters preserve claim ceiling/economic UNKNOWN does not erase the exposed count. It breaches scientific-independence/evidence-accounting truth without requiring any production use. Historical confirmation counts cannot be silently treated as established scientific independence.

FACT: Probe created no real EconomicIdentity and observed no outcome; adjudication says `economic_identity_created=false`, all authority false, economic_result NOT_OBSERVED, profitability UNKNOWN. There is no evidence that a production object was falsely promoted. Failure is in current callable contract, not proof of actual economic harm. Product code repair was not performed; separate mission or truthful stopped verdict remains appropriate.

## Frozen review evidence use

FACT: Owner Recovery f503b5f070bda6a61824d139ba8bb7b026892ebe README says AUDIT_COMPLETENESS=INCOMPLETE and immutable append-only preservation. Owner delta e97bb3834f2c1a1b3de3a5719c1e94b416c52d2e DELTA_REGISTER D09 requests selected subject/model/time/independence controls, not wholesale files. Challenger 642b551:14 explicitly notes W2 native manual source binding and existing model admission; this audit agrees and supplies generic-route and time-vs-generation differential evidence missing from mere helper absence.

## Applicable attack scope

FACT: Existing target PIT, epoch blinding, evaluation membrane, native lineage and C2 adjudication tests were included in the 61-case run. Current C0 source attack was selected because it directly protects scientific independence in retained unchanged W2 C0, not because newer source is a convergence target. H/V/Q broad product integration was not attempted; branch-wide failures cannot authorize a repair. No exact L source was recovered by this audit, so no L attack was used. UNKNOWN protected-invariant failures must block final qualification; no UNKNOWN was converted into a pass.

RECOMMENDATION: Final bound continuity cannot be QUALIFIED while C0 current semantic-confirmation failure remains unresolved. Preserve this evidence and require a separately scoped minimal counting repair plus exact-head tests; do not port C0 wholesale or change kernel identity to hide the failure.
