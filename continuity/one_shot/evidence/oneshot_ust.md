# PRIMARY UST forensic witness

FACT: Primary object is `FLOW-UST-PRIMARY-DEALER-AUCTION-001:G1`. Exact frozen protocol is `7b843ddd551c6770c0ff5941cf5cb1ffb74b8452:research/research_os/artifacts/FLOW-UST-PRIMARY-DEALER-AUCTION-001/frozen-economic-screen-v1.json`; exact post-freeze checkpoint is `ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7:research/research_os/architecture/work_receipts/ECON_TEST_FLOW_UST_AUCTION_CP2_POST_FREEZE.json`. Metadata-only comparison proves protocol bytes unchanged through post-freeze and W2. The protocol's `hypothesis_blob_sha=ba92efb4475db4883dc3dfb9f0cd979ba7a6de03` equals the original frozen hypothesis Git blob. Source byte hashes and sizes are in `/tmp/oneshot_ust.json`.

## Finding

`UST_FORENSIC_STATUS=AUTHORITY_UNRESOLVED`

`CURRENT_PROTECTED_ACTION_STATUS=DENIED`

`CURRENT_LAWFUL_NEXT_STATE=READ_ONLY_FORENSIC_AUTHORITY_BLOCK`

`CONTINUATION_OBLIGATION_STATUS=UNKNOWN_NOT_PROVEN_AS_DURABLE_OPERATIONAL_OBLIGATION`

FACT: The current one-shot expressly denies production research mutation, economic experiment, prospective observation, capital and live trading. It authorizes read-only metadata inspection and isolated replay. No historical scoped grant overrides this current action-specific denial. Historical applicability remains unresolved; this report does not normalize the contradictory historical representations by treating an unknown as either revocation or current authorization.

INFERENCE: The forensic question closes truthfully with an authority block on protected action and preservation of UNKNOWN historical execution/obligation. It requires no product repair and no new child task. A truthful block is not economic execution, scientific rejection, null result or evidence of scheduler failure.

## Facts proved from primary immutable artifacts

- The original producer task (`research/research_os/tasks/FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-002.json` at W2) is COMPLETE, returns `FROZEN_HYPOTHESIS_NO_HANDOFF_AUTHORITY`, and explicitly says its task did not authorize downstream creation. This establishes a historical ceiling for that producer task, not a current production creation grant.
- The validation task (`research/research_os/tasks/VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001.json` at post-freeze/W2) is COMPLETE. Its allowed actions are documentary inspection, PIT reconstructability and one EvidenceAssessment. Candidate returns, retuning, capital and orders are forbidden. Its authority is `INDEPENDENT_DOCUMENTARY_VALIDATION_ONLY`. Its completion references the assessment, not a durable execution task or receipt.
- The independent assessment (`research/research_os/assessments/VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001.json` at post-freeze) recommends `PASS_TO_TEST_DESIGN_BOUNDED` and restricts the validated claim to a dated dealer participation expectation and pre-announced supply event. It explicitly does not validate inventory magnitude, concession, reversal, alpha, profitability or capacity. Its outcome/price-return access fields are false at that point. `integration_handoff_created=true` and `next_stage=FREEZE_BOUNDED_ECONOMIC_TEST_PROTOCOL` do not themselves prove a queued economic task.
- CP1 (`7b843ddd:research/research_os/architecture/work_receipts/ECON_TEST_FLOW_UST_AUCTION_CP1_20261019.json`) records conversation-owner authorization for independent validation, design, a bounded economic experiment after all gates, substitution and conditional observation. Its policy explicitly closes outcome access until validation/PIT/expression/cost-capacity/multiplicity/trial-accounting/freeze gates pass. This is historical documentary evidence, not a new mission grant.
- The frozen protocol fixes one 10-year nominal auction family, 2010–2025 sample, official sources, butterfly transform, one primary one-sided mean endpoint, alpha 0.05 and a 0.25 bp materiality floor. Secondary endpoints cannot rescue primary failure. Lines 56–61 distinguish a mechanism screen from later tradable P&L research; it must not be promoted to a profitability protocol. Lines 62–64 record post-commit authorization prose and no observed outcome at freeze.
- CP2 lines 12–17 record `AUTHORIZED_OUTCOME_ACQUISITION_AND_EXECUTION_OF_FROZEN_SCREEN`, scoped conversation-owner authorization and an intended autonomous continuation. The line is documentary intent, not a canonical scheduler task, lease, execution receipt or resolved operational grant.
- W2 (`ebc72b9fd14f91420c37e0b7607f9bfb584a289a:research/research_os/runtime/CONTROL_PLANE.json`) requires follow-up task creation only where the current task explicitly allows, and has global economic/prospective/capital/live flags false. Its routing list has no dedicated economic execution stage. No exact precedence/revocation/effective-time rule resolving CP1/CP2 versus these flags was found in inspected artifacts.
- No task-specific receipt is present in `research/research_os/receipts/VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001` in the inspected frozen/post-freeze/W2 trees. UST execution/result was not recovered in these inspected trees. This is scoped absence, not proof no private/other historical execution occurred.

## Review inputs are evidence, not authority

FACT: Frozen Owner Recovery `f503b5f070bda6a61824d139ba8bb7b026892ebe`, `audit/owner-recovery/20261026/pass-01/reports/17_AUTHORITY_MAP.md` and contradiction CT06 preserve the scoped grant and global denial and state the missing normalized scope/revocation rule. Orphan register labels UST a strong inference and explicitly limits its search to reachable documentary paths/private host unavailable.

FACT: Frozen architecture delta `e97bb3834f2c1a1b3de3a5719c1e94b416c52d2e`, `audit/owner-recovery/20261026/architecture-delta-01/DELTA_ARCHITECTURAL_MINIMAL.md` lines 23–24 notes existing handoff/atomic publication and missing expected UST execution with contradictory authority. Lines 37–50 recommend continuation accountability only for dispositions that actually require continuation; they do not grant operational authority.

FACT: Frozen independent challenger `642b551985f499b37286c3bc21b89c57294f63ca:architecture-review/05_POSITIVE_CONTINUATION_ANALYSIS.md`, section “UST: discriminate the competing explanations”, explicitly states scheduler defect NOT PROVEN, active authority scope UNKNOWN, compatible UST executor not proved, and a mechanism screen must not become a profitability protocol. Its more ambitious missing-materialization diagnosis is an inference. The current mission requires proving the operational obligation first, which these artifacts do not do.

## CP05 audit and correction

`CP05_DISPOSITION=KEEP_EVIDENCE_ONLY`

FACT: CP05 (`eae8eaef0cdf56ba195d1afa94431e113bdaea3a`) changed only `continuity/05_UST_DISPOSITION.md` and `continuity/evidence/UST_RECOVERY_ARTIFACT.json`. No product module is needed for the forensic disposition.

FACT: The recovery JSON declares `artifact_kind=RECOVERY_ARTIFACT`, `original_historical_receipt=false`, `historical_task_fabricated=false`. Its `declared_obligation.OBLIGATION_ID=UST-G1-FROZEN-SCREEN-EXECUTION` and closure were newly reconstructed by CP05. Their existence does not prove a corresponding historical operational obligation or durable production block existed. The historical markdown's “expected continuation obligation” and “silent_orphaning=false” are too broad if read as historical facts.

RECOMMENDATION: Keep original CP05 evidence immutable and append a correction wrapper/event with `RECOVERY_ARTIFACT=TRUE`, `AUTHORITATIVE_HISTORICAL_STATE=FALSE`, `CURRENT_MISSION_FORENSIC_DISPOSITION=AUTHORITY_UNRESOLVED`, `HISTORICAL_OPERATIONAL_OBLIGATION=UNKNOWN_NOT_PROVEN`, and `HISTORICAL_SILENT_ORPHANING=UNKNOWN`. The original ID is a recovery-artifact identifier only. The authoritative current action is the mission's denied protected action, not a production BLOCK mutation. The recovery wrapper belongs to operational/control audit history, not qualified Scientific Memory.

## Preserved boundaries and unknowns

FACT: No source endpoint was fetched, no protected UST outcome was opened, no production object was created or mutated, no outcome endpoint/decision rule was changed, and no authority was expanded by this audit. Only frozen metadata, control contracts and review text were read.

UNKNOWN: Complete historical exposure/trial denominator; private human/model knowledge; unrecorded host execution; current normatively applicable historic grant scope; whether any durable task obligation existed for frozen-screen execution; compatible qualified UST executor/source availability. Protocol attempt counts are historical declarations, not a newly proven complete denominator.

RECOMMENDATION: Any future protected execution mission must first resolve action-specific authority scope, precedence, effective dates and revocation, then establish the exact claim/readiness and compatible executor without retuning frozen endpoints or resetting lineage/exposure. This mission needs evidence closure only. Do not force a child task, fabricate historical task state or patch a scheduler based on this witness.
