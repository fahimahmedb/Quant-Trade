# Builder CP046 — preserve unknown structural evidence

STATUS=IMPLEMENTED_FOCUSED_PASS_BROADER_QUALIFICATION_PENDING
BASE=ba606bf
ORACLE_HEAD=bc1284f90841a473ee4bb45bbec550bde35253c2
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

DONE: harden existing portfolio_v2 evidence-presence helper using canonical V2
semantic nulls plus existing portfolio unknowns. Whitespace/case variants,
booleans, nonfinite floats and wholly unknown containers do not count as known.
Unknown tags cannot inflate Jaccard overlap. Genuine finite numeric declarations
including zero/large integers, raw known values and field provenance survive.
No portfolio model, memory veto, scheduler, evidence store or capital action added.

EVIDENCE: four new adversarial tests plus seven existing structural identity/
portfolio tests PASS. Missing payer/mechanism/clock now yields UNKNOWN, no same-
exposure review and UNKNOWN novelty. Known positive pair and actual native
Fundamental projection retain both prechange CP045 golden hashes exactly.
Inputs remain immutable. Correlation UNAVAILABLE, contribution NOT_ESTIMATED,
return_series_consumed=False and all six portfolio authorities False are checked.
Pyflakes/whitespace PASS. New tests and existing seven now included in hosted V2
workflow. Broader Research OS 266/266 PASS; official inventory/other checks follow.

ARCHITECTURE: Economic Identity → structural Portfolio Map distinguishes shared
evidence from shared absence of evidence. This qualifies structural metadata
semantics only; no empirical correlation, diversification or marginal value is
inferred. No native misclassification or runtime deployment is claimed.

NEXT: configured 716 / V2 225 / broader 266 qualification and exact-head hosted
proof. Reassess the whole-system frontier using current Oracle receipts and
existing acquisition/authority/Integrator boundaries. Preserve all actual Oracle
state and historical artifacts; no Closure 4 or runtime/Site changes.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
