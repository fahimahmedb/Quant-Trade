# Builder CP041 — Research/Evaluation admission audit before code

STATUS=REPRODUCED_HARDEN_EXISTING_INTERFACES
BASE=6e286cd11817deffd7ab1affb539ff7329b8b32c
ORACLE_HEAD=ade4cd0
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

CP040: 699 configured / 201 V2 / 266 broader Research OS tests PASS. All local
workflow steps PASS, including exact-head qualification and real read-only
GitHub entrypoint. First full-suite run caught the stale 695 inventory while its
official generator was still running; after generator completion, the unchanged
699-test suite passed. No assertion was weakened. Hosted qualification pending.

REVERSE REPRO: validate_reverse_message accepts the canonical receipt augmented
with evaluation_summary free text, and accepts build_evaluation_ingest_receipt
with a dictionary as export_bundle_hash. Existing outcome-key blacklist cannot
close these payload paths. Receipts are neither structurally nor self-hash checked.
ORACLE_V2_CORE_SPEC explicitly permits only technical ingest receipts for the
exact frozen bundle; it forbids outcome-derived completion/blocker/retry signals.

PIPELINE REPRO: run_pre_outcome_pipeline accepts the string "false" for each of
validator_independence_qualified, feedback_lineage_qualified and
bounded_orchestration_qualified. It also accepts SOURCE_PIT=FAIL and a contradictory
SOURCE_AND_MODEL_PIT label paired with MODEL_PIT=NOT_PROVABLE. In each case it
returns READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY. qualify_v2_core itself correctly
requires literal True; its adapter coerces declarations through bool().

DISPOSITION=HARDEN, no new gateway/queue/store. Require canonical technical receipt
shape, SHA-256 references, intact receipt hash and optional expected-bundle
comparison; connect expected-bundle checking in the deterministic pipeline.
Reuse classify_model_pit to check canonical leakage classification, require source
PIT for export, and pass proof booleans unchanged to the existing strict qualifier.

LIMITS: synthetic metadata only. No actual Evaluation/outcome access, reverse
transport activation or economic execution. Shape/hash checks do not establish
sender authenticity or eliminate timing channels. Runtime principal separation,
deployed evidence and final convergence remain Final Integrator scope.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
