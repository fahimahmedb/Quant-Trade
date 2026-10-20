# Builder CP036 — attributed epoch/trial/candidate identities

STATUS=IMPLEMENTED_FOCUSED_TESTS_PASS_FULL_QUALIFICATION_PENDING
BASE=9b1718d80939a5d8e9238519adcb103713f6c84f
HEAD=commit containing this checkpoint
ORACLE_HEAD=fb236c284c1ace9aaf154bab0e832712477c6db9
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

FOUND: mutually equal null epoch/trial/candidate/Validator references also passed
the whole deterministic pipeline before this patch. Existing joins correctly
check equality, but equality between nulls does not establish attribution.

DONE: explicit principal IDs at epoch, research trial and candidate construction
must be nonblank strings outside existing semantic-null states. No IDs invented
or normalized; valid historical/opaque textual IDs and all valid hashes preserved.
Nullable root parent/ancestry fields and family-specific research unknowns remain
supported. Existing pipeline cross-reference checks reused; no second registry.

EVIDENCE: 36 focused core/pipeline/worker tests PASS, including four new tests
with null/type/blank/sentinel subcases, whole-pipeline null-reference rejection,
nullable root ancestry, unknown Fundamental extension fields and raw ID preservation.
Golden hashes captured before the patch prove unchanged valid epoch, trial and
all four family outputs. Test fixture class imported through its module to avoid
duplicate unittest discovery. Pyflakes/whitespace PASS. New suite added to V2 CI.

ARCHITECTURE_IMPACT: canonical research core → attributed scientific lineage
cannot produce an apparently qualified but unidentified epoch/trial/candidate.
Scientific evidence may remain unknown; its canonical subject must be identified.
No mutation of existing artifacts, epoch/policy, runtime/Site or authority.

NEXT_BEST_WORK: full configured/Research OS/194-test V2 qualification, exact hosted
proof, then whole-system reassessment. CP034 exact code already passed 688
configured and 190 V2 tests plus real read-only GitHub dry-run; that proof is
distinct from this new core change and is not reused as its qualification.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
