# Builder CP040 — coherent attributable scientific declarations

STATUS=IMPLEMENTED_FOCUSED_PASS_BROADER_QUALIFICATION_PENDING
BASE=87e34a8
ORACLE_HEAD=ade4cd0 (no intersecting source changes)
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

DONE: reuse build_validator_result and the canonical identifier helper. Validator
subject/actor IDs must be identified strings. A PASS cannot coexist with a
nonempty epistemic_blockers list, including null/false entries. Existing COMPLETE
decision requirements, blocker-list validation, conservative BLOCK behavior and
infrastructure-failure/scientific-decision separation remain intact.
classify_model_pit now requires a literal boolean source_pit declaration;
truthy strings/integers/containers cannot become SOURCE_PIT=PASS. Valid SOURCE_PIT
and MODEL_PIT classifications remain distinct, without a hindsight upgrade.

EVIDENCE: 36 focused core/pipeline/worker/adversarial tests PASS; four new tests
exercise direct and complete pre-outcome export-path rejection, attribution,
boolean typing and valid BLOCK/error states. Existing valid Validator fixture
hash remains 45bb2e3c401ae635867bb9b89825bda5cdd6e0624c3cd9bf5304a5fed903aeb4.
Pyflakes and whitespace checks PASS. New suite included in hosted V2 workflow.
Configured/full Research OS qualification and inventory generation follow.

ARCHITECTURE: Candidate → Validator → frozen-export metadata rejects contradictory
scientific admission. This proves interface invariants, not actual independence,
runtime integration, scientific validity or economic test authority.

NEXT: audit technical Evaluation reverse-receipt payload admission: current
validator accepts extra free-text fields and structured export references.
Reproduce and checkpoint before code; preserve Integrator ownership of runtime,
Site, global history and final convergence. No actual Evaluation access.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
