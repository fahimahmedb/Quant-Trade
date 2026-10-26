# Builder CP043 — exact validated identity at the frozen-export boundary

STATUS=AUDIT_BEFORE_CODE
BASE=e8ff9df
ORACLE_HEAD=bc1284f90841a473ee4bb45bbec550bde35253c2
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

CP042: configured 707/707, local V2 209/209 and broader Research OS 266/266 PASS;
all local workflow steps, exact-head qualification, closed policy/claim ceiling
and real GitHub read-only dry run PASS. Hosted qualification pending.
CP038 hosted V2 39504981025 and SEC 39504980971 both SUCCESS; official job pages
show all 13 and 17 steps successful respectively, including archive uploads.

THREE REPRODUCIBLE CONNECTION GAPS:
1. In the canonical pipeline fixture, independently alter export universe, clock,
   horizon or economic_expression while leaving the validated Candidate intact.
   Each still returns READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY. Hash joins exist
   but do not reject contradictory semantic declarations. The fixture itself has
   a partial export expression omitting the Candidate's instrument.
2. Validator metadata/bridge records subject IDs but no explicit candidate_hash.
   Pipeline and worker export gates do not compare the exact validated Candidate
   bytes; the worker also trusts the stored Validator self-hash. Same-generation
   identity alone cannot detect changed Candidate content or an altered sidecar.
3. Capturing the actual V2StageExecutor export from the existing isolated
   claim-restriction test shows export_bundle_hash != canonical_hash(export without
   export_bundle_hash). Four sealed-plane metadata fields are added after hashing.

DISPOSITION=HARDEN. Reuse existing Candidate/Validator/export builders, bridge and
stage executor. Bind semantic export fields to Candidate values. Add explicit
candidate_hash in newly produced Validator metadata; require it at export gates,
verify stored Validator hash, and hash the complete emitted export including
sealed-plane metadata. Old unbound Validator records must not authorize a new
export; do not rewrite historical artifacts. Valid fixture inputs must become
self-consistent using existing Candidate facts, without fabricating new evidence.

CORRECTION: CP001's broad ALREADY_SOLVED future-package classification proves
existing plumbing, not these now-reproduced semantic and exact-content bindings.
This checkpoint narrows that earlier claim. Synthetic interface evidence only;
no Evaluation/outcome access, no actual economic execution or authority change.
Oracle advanced only a wake receipt; no intersecting code changed. Final
Integrator retains runtime/deployment/Site/history and final convergence ownership.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
