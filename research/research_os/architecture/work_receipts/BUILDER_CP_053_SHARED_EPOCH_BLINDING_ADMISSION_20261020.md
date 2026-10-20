# CP053 — consistent epoch/blinding admission, including independent qualification

STATUS=IMPLEMENTED_FOCUSED_AND_BROADER_PASS_FULL_QUALIFICATION_PENDING
BASE=7b217d7
ORACLE_OBSERVED=c7eaeff9670e759493f1f56017a07119c8c1be45 (new wake receipts only)
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

REUSE/HARDEN: extract the existing native clean/explicit-blinding admission law
into assert_epoch_blinding. _active_epoch now applies it before any stage work,
with no implicit BLINDED default for missing actors. V2StateStore inherits that
same law through its existing _active_epoch call; remove the redundant predicate.
Native refusal reason V2_EPOCH_CONTAMINATED is retained. Pipeline uses the same
helper and cannot qualify a BROKEN/unknown epoch despite separate BLINDED labels.

DEPTH EVIDENCE: four new adversarial tests cover dirty/unknown declarations before
export, missing/unknown/viewed actor state before the base stage, and an actual
temporary Git worker wake that rejects synthetic contamination before any new
claim/commit/model call. The synthetic Owner state change is a fixture Git commit;
the normal bounded worker store correctly refuses writes to its epoch policy.
No real epoch, outcome or authority was touched.

VALID GOLDEN: deterministic clean/blinded fixture receipt remains exactly
01fa1c77d95dbe81b9366264629a9e0bdcf24eefc03835a04796cbfc509c30ec.
Inputs unchanged. Seventeen focused tests and 268 broader Research OS tests PASS;
pyflakes/whitespace PASS. Official STATE generator now targets 734 configured
tests. V2 workflow includes the new suite (243 Python core tests), plus composed
metadata/JS gates. Full/local/hosted qualification follows.

CLAIM LIMIT: native V2StateStore already protected its normal path. This closes
independent-adapter/direct-stage drift; it is not proof of new operational
activation or actual human blinding. No records are retroactively relabeled.

NEXT: complete exact composition qualification; continue CP12 Evidence Store
disposition where a concrete raw-byte preservation/replay connection can be reused
without a second orchestration authority or unprovided network capture.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
DEPLOYMENT_PERFORMED=FALSE
