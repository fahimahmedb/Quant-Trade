# Builder CP031 — continue autonomous loop / frozen runner accounting gap

STATUS=REPRODUCED_BEFORE_CODE
BASE=dec2fb804ef11a8d92f7c087d28e65f94387871a
ORACLE_HEAD=53a23ccea016c7e98d390cc5536e8258c95106a9
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

CP030 closed a qualification boundary, not the open-ended Owner mission.
Continue autonomous investigation rather than treating that checkpoint as
mission completion. Fresh branches and clean Builder checkout verified.

FOUND: CP021 rejects non-finite KNOWN trial estimates in the independent
Validator, but direct DryRunExperimentRunner.plan still accepts effective_trials
NaN or +Infinity and emits READY_FOR_REPRODUCIBLE_DRY_RUN / frozen capability READY
with no blockers. Reproduced using its existing metadata-only fixture. Thus the
frozen-protocol boundary disagrees with downstream validation and can persist
invalid multiplicity metadata independently of that composition.

HISTORY: existing runner port 724e4c0; its file is unchanged between current
Builder and fresh Oracle. Reuse the runner, do not build another experiment path.
DECISION=HARDEN finite numeric effective-trial validation at freeze. Preserve
UNKNOWN, valid nonnegative estimates, immutable bindings, deterministic replay,
legacy dry-run fingerprints, source/authority gates and scientific meaning.

NEXT_BEST_WORK: adversarial direct runner tests + original frozen-protocol suite,
then exact full/V2 qualification and CP032. No experiment execution or deployment.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
