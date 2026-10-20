# Builder CP044 — exact validated content through frozen export

STATUS=IMPLEMENTED_FOCUSED_PASS_BROADER_QUALIFICATION_PENDING
BASE=590bf75
ORACLE_HEAD=bc1284f90841a473ee4bb45bbec550bde35253c2
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

DONE: reuse existing Validator bridge and export gates. Newly produced Validator
metadata includes candidate_hash. Shared assert_validator_candidate_binding checks
subject IDs, exact Candidate hash, the Validator contract and its own canonical
hash. Pipeline and worker claim-restriction gate use it; the worker rejects a
missing/foreign/corrupt/contradictory Validator before invoking the base stage.
Old metadata is preserved, but cannot authorize a new export without the binding.

Pipeline export fields universe/clock/horizon/economic_expression now join exact
Candidate facts. AUTO/missing/None use those existing facts; explicit mismatches
block instead of being silently replaced. Worker export semantics already used
Candidate values and are retained. Four sealed-plane fields move inside the
builder input so the emitted export's complete canonical hash is correct.

EVIDENCE: 55 focused core/bridge/pipeline/worker/adversarial tests PASS. Five new
tests cover semantic substitution, AUTO equivalence and input immutability,
same-generation changed content, new bridge binding and actual worker preflight
rejection without export. Existing worker positive test now verifies the entire
emitted bundle hash, including sealed metadata. Pyflakes/whitespace PASS; tests
included in hosted workflow. Broader suites/inventory/hosted checks follow.

FIXTURE MIGRATION: add the hash of the already-existing Candidate to Validator
and retain its already-declared equity instrument in export economic_expression.
No new source fact or economic readiness inferred. Candidate hash unchanged;
Validator hash intentionally becomes
3298ec7ea354f5f760fe30593fe1289d68bfb64c5e87c0f2da8e81ae12dd2f23
because metadata gains the binding. CP040's legacy golden hash is still tested
for the original unextended payload. Historical receipts/artifacts not rewritten.

ARCHITECTURE: Candidate → independent-validation metadata → future frozen export
preserves content and economic meaning. This proves engineering admission and
hash consistency, not actual Validator independence, scientific validity,
runtime integration or economic test authorization. No Evaluation access/export
transport/observation/trading activated. Integrator retains convergence ownership.

NEXT: exact 712 configured / 214 V2 / 266 broader Research OS qualification.
Reassess structural portfolio unknown-value semantics: unresolved semantic nulls
currently can be mistaken for matching known payer/mechanism/clock evidence.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
