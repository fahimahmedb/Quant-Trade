# Builder CP025 — source availability → PIT qualification false positive

STATUS=REPRODUCED_BEFORE_CODE
BASE=7f9886e (full identity through Git parent)
HEAD=parent of this audit checkpoint
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

FOUND: qualify_source_route checks the presence of availability_start but only
parses it when truthy. Empty/null values therefore return PASS and
point_in_time_qualified=True. Its parser silently assigns UTC to naive clocks.
Three exact reproductions using the complete existing metadata fixture, changing
only route availability_start to empty, null or naive timestamp and updating the
declared manifest hash, all yield READY_FOR_AUTHORIZED_ECONOMIC_TEST. No market
outcomes or economic execution are involved. Prior source helper history has a
single inherited implementation (724e4c0), not a missing alternative qualifier.

DECISION=HARDEN source temporal contract. Always validate availability and freeze
clocks; require explicit timezone-aware ISO timestamps, no UTC inference. Invalid
types/missing/empty/naive clocks must produce machine-readable BLOCK with PIT
false. Preserve valid offset-equivalent timestamps, chronology comparison,
canonical route hashes, permission/content gates and existing qualification API.

ARCHITECTURE_IMPACT: qualified evidence → producer/frozen experiment must not
claim PIT when its availability clock was never established. This applies to
all four families; Fundamental's new projection does not authorize source use.

PREVIOUS PACKAGE: CP024 implementation is committed/pushed; full/V2/hosted
qualification is running on exact code, separately from this next patch.
NEXT_BEST_WORK: adversarial qualifier + end-to-end readiness tests, exact offset
equivalence/chronology proof, then full regression and new source checkpoint.
No source acquisition, runtime/Site change or authority expansion.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
