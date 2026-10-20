# Builder CP026 — explicit source availability / freeze clocks

STATUS=IMPLEMENTED_FOCUSED_TESTS_PASS_FULL_QUALIFICATION_PENDING
BASE=5df20be13e462eaa1562c58318ae011023e4886e
HEAD=commit containing this checkpoint
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)
ORACLE_HEAD=d46116b31f3a217fdf418fe08aa2c4820d5d93c0

DONE: existing qualify_source_route always validates availability_start and
freeze_time. Missing/empty/null/invalid-type/naive clocks BLOCK with
AVAILABILITY_CLOCK_INVALID and point_in_time_qualified=False. No implicit UTC.
Explicit offset-aware timestamps still compare as instants, including equality;
canonical raw route metadata and hashes are not normalized or rewritten.
No other source, permission, content, outcome, epoch or authority gate changed.

EVIDENCE: 35 focused tests PASS (four new temporal contract tests, original
producer and economic-readiness tests). Adversarial subcases cover availability
and freeze independently, missing key, invalid scalar/container types, naive
dates/times, explicit offsets, microsecond chronology and end-to-end packages.
Previously empty/null/naive availability yielded READY; now BLOCK without input
mutation or authority changes. Valid complete package remains pre-outcome READY.
Pyflakes and whitespace PASS. Added clocks suite to existing V2 CI.

PREVIOUS PACKAGE: CP024 exact code 7f9886edaf13c81ac58e742662f70b8301e5d658:
675 configured tests PASS, 266 Research OS PASS, 164 local V2 tests PASS;
full local V2 workflow/real read-only GitHub dry-run PASS. Hosted result will
be retained separately; no runtime integration inferred.

ARCHITECTURE_IMPACT: qualified source metadata → frozen experiment package now
requires an established temporal availability boundary for all native families.
Fundamental remains connected as requirements; actual incomplete dossier still
BLOCKED. No scientific result or historical-PIT discovery claim is introduced.

NEXT_BEST_WORK: exact code/full suite/168-test V2 qualification, hosted job
inspection, updated architecture truth and stable Integrator/resume handoff.
Acquisition execution, active Oracle deployment, Site/reboot and Closure 4 are
separate boundaries. Preserve all autonomous Oracle commits and live observer.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
