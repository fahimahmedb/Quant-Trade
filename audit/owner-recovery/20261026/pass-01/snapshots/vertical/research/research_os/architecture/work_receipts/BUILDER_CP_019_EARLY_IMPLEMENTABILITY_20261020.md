# Builder CP019 — early implementability declaration hardening

STATUS=IMPLEMENTED_TARGETED_TESTS_PASS
BASE=60301c076593741c85c2d5c6d35eb4c950f7538f
HEAD=commit containing this checkpoint
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)
ORACLE_HEAD=21bec213b756d7ca0338849eba0e47e300d5b325

DONE: adapted existing implementability_depth._known, whose lone implementation
was inherited through historical port 724e4c0. No replacement interface.
Boolean declarations, non-finite float values and explicit UNKNOWN/UNAVAILABLE/
UNSPECIFIED/NOT_ESTIMATED scalar placeholders cannot satisfy exact expression
requirements. Existing universe/instrument and exit/horizon alternatives remain
valid. Container semantics are unchanged; this is declaration-presence
hardening, not proof that arbitrary declared prose is economically usable.

EVIDENCE: reproduced entry_clock=False → PASS before code. Three new adversarial
tests cover every required expression field with boolean/non-finite values,
clock placeholders and valid alternatives, no candidate mutation and unchanged
authority. 26 focused tests PASS, including original implementability and
economic-readiness integration suites. Added new and original implementability
suites to the existing V2 hosted workflow. Official status inventory regenerated.

BROADER QUALIFICATION DISCOVERY: research/research_os/tests initially ran 266
tests with three errors, one failure and one skip because this checkout lacked
the pinned legacy ledger. Followed the existing CI materialization contract:
fetched exact commit 183ad65ff260b903a16548ce37948f54d47a9ec8, verified blob
ba9b165aaf96956776672df51233bb9bf1e6cbc9, preflight PASS (20 records), reran:
266 tests PASS, no skips. No tests weakened. Temporary materialization was
removed from checkout and retained under /workspace/.setup for local reuse;
no historical results were modified, reclassified or imported into research state.

CURRENT_ARCHITECTURE_IMPACT:
- Consumed evidence → search: CP017 rejects renaming as novelty.
- Source selection → producer/resumed worker: CP018 verifies matching bindings.
- Producer → early implementability: invalid declarations now block cheaply.
- Existing pinned historical memory and deterministic core spine reused.
- All other CP016 statuses remain bounded by their recorded evidence.

NEXT_BEST_WORK: qualify stable exact code across full configured suite, V2
workflow, actual read-only GitHub dry-run and hosted CI. Then assess the remaining
negative-sidecar→search connection against genuine bound artifacts, preserving
the Integrator's historical reconciliation and deployment scope.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
