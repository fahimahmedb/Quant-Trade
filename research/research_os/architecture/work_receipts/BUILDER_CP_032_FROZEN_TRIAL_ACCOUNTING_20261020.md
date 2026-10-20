# Builder CP032 — freeze/replay trial-accounting consistency

STATUS=IMPLEMENTED_FOCUSED_TESTS_PASS_BROADER_QUALIFICATION_PENDING
BASE=f527c0109a4ed255f09ad20c529211bcfae0935a
HEAD=commit containing this checkpoint
ORACLE_HEAD=53a23ccea016c7e98d390cc5536e8258c95106a9
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

DONE: reused existing frozen runner; finite nonnegative trial estimates or
UNKNOWN required at both freeze and replay. Valid legacy hash integrity cannot
make a NaN/Infinity freeze admissible. Rebinding also rejects these old invalid
plans through replay. No cap invented for finite integers, no trial estimate
fabricated, no economic execution. Validator remains independently implemented.

EVIDENCE: 16 focused tests PASS, including original frozen-runner suite and three
new tests with adversarial subcases. Tests cover invalid types/non-finite values,
hash-valid legacy invalid plans, direct replay/rebinding, UNKNOWN, zero, fractional
and arbitrarily large finite integers. Original legacy-plan fingerprint test
unchanged. Pyflakes/whitespace PASS; suites added to V2 CI. Full/hosted proof pending.

FOUND / NEXT_BEST_WORK: direct metadata reproductions also show replay accepts
a different plan's self-consistent receipt, a missing receipt for a frozen plan,
or a rehashed receipt declaring live_trading_authorized=True. Actual policies
and authorities were never changed. Receipt self-integrity is checked, but not
complete plan linkage or all four receipt authority fields. Harden that existing
receipt boundary next, preserving legacy plans without the frozen extension.

ARCHITECTURE_IMPACT: exact experiment freeze → reproducible replay now agrees
with the independent Validator about scientifically valid multiplicity metadata.
CP030 remains earlier qualification, not completion of this autonomous mission.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
