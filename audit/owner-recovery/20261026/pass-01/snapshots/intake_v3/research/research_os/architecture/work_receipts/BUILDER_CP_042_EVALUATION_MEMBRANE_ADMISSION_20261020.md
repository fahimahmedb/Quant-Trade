# Builder CP042 — strict technical receipts and explicit pipeline proofs

STATUS=IMPLEMENTED_FOCUSED_PASS_BROADER_QUALIFICATION_PENDING
BASE=2bd8c2e
ORACLE_HEAD=ade4cd0
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

DONE: existing reverse-message validator admits exactly the four canonical
technical receipt fields, three fixed technical message codes, literal ingest
event type, lowercase SHA-256 export reference and correct canonical receipt hash.
It rejects unknown free-text fields even when rehashed, structured references,
missing fields and altered metadata. Optional expected_export_bundle_hash binds
a receiving caller to its own export. The deterministic pipeline supplies that
expected reference; a valid foreign receipt cannot acknowledge its bundle.

The existing strict qualifier now receives raw proof flags for independence,
feedback lineage and bounded orchestration, without bool() coercion. Pipeline
leakage declarations must agree with classify_model_pit; SOURCE_PIT=FAIL cannot
export. MODEL_PIT=NOT_PROVABLE/AFTER_CUTOFF remains explicitly classified and does
not become a claim of historically blinded discovery. No runtime authority opens.

EVIDENCE: 44 focused core/pipeline/worker/adversarial tests PASS, eight new tests
including a self-hash-valid foreign receipt injected into the complete pipeline.
Existing reverse test now uses an actual hex digest placeholder rather than x*64;
its original forbidden-message assertion remains. Pyflakes/whitespace PASS.
Technical receipt shape documented in ORACLE_V2_CORE_SPEC; workflow includes tests.
Official status inventory generation and broader qualification follow.

LIMITS: synthetic metadata, no transport/store/process isolation qualification.
Payload admission does not authenticate a sender or eliminate timing channels.
Flags are evidence declarations, not measurements of independent validation.
Actual Evaluation, economic execution, observation, capital and trading remain
sealed. Final Integrator retains Site/runtime/history/convergence ownership.

NEXT: exact 707 configured / 209 V2 and 266 broader tests, hosted qualification.
Then audit Candidate → export semantic binding: current pipeline hashes the
Candidate but accepts divergent universe/clock/horizon/economic_expression in
the export. Reproduce and checkpoint before touching that connection.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
