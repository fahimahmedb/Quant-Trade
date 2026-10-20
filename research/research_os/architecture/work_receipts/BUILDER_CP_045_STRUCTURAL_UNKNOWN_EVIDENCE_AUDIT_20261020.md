# Builder CP045 — semantic nulls are not shared exposure evidence

STATUS=AUDIT_BEFORE_CODE
BASE=d6557df
ORACLE_HEAD=bc1284f90841a473ee4bb45bbec550bde35253c2
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

CP044 QUALIFICATION: configured 712/712, V2 214/214, broader Research OS 266/266
PASS. All local workflow steps PASS, including policy/ceiling, exact-head
qualification and real read-only GitHub entrypoint. Hosted qualification pending.

REPRO: structural_pair on two synthetic identities whose payer, mechanism and
timing_clock all equal UNRESOLVED, NOT_YET_MEASURABLE, NOT_APPLICABLE, whitespace
or False returns HIGH_STRUCTURAL_OVERLAP_REVIEW and same_exposure_review_required
True. UNKNOWN correctly stays UNKNOWN. Equality of missing evidence must not
become proof of shared economic exposure. Nonempty containers containing only
semantic nulls also count as known, and Jaccard includes placeholder tags.

HISTORY: existing portfolio_v2 was ported in 724e4c0; seven existing economic
identity/portfolio readiness tests cover genuine known overlap/distinction,
literal UNKNOWN, non-economic limits, provenance and native immutability. Reuse
that implementation and tests. No empirical model or second portfolio engine.

DISPOSITION=HARDEN. Reuse canonical V2 semantic null vocabulary plus existing
portfolio unknowns; disregard whitespace/case variants, booleans, nonfinite
floats and containers with no known values. Exclude unknown tag entries from
Jaccard. Preserve real finite numeric declarations, known structure/provenance,
raw input bytes and UNKNOWN novelty/UNAVAILABLE correlation/NOT_ESTIMATED value.

PRECHANGE GOLDENS: native Apple Fundamental structural projection
0a8566d6c0c603ead49afe7a666b038a8f66243f56e2e2b63cbfbf789aa423c7;
fully known positive structural pair
0c788583ae3c7f561ffd665227152b69733f8b46611496bc3e53f67f7c66deb4.
No native misclassification is claimed from the synthetic reproduction. No
negative memory or runtime artifacts will be rewritten. Integrator scope retained.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
