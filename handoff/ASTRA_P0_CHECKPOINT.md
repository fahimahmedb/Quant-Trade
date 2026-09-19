CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T18:52:30Z
* branch: astra/p0-deep-adversarial-pre-t0
* exact HEAD SHA: fd16fbd2df4378bcb27e9feb05170d9047e5f11f (phase-3 green code head; this checkpoint is a subsequent documentation-only commit)
* parent/base SHA: parent f9c0c71b9ba233ccd93f906bf0df120f58071965; phase-3 red head c2edb2993b1ab044bbd9bc3cd80be6c7fd1b66f1; audit baseline 8d5dbb41559c4716e94d5290b6ae979a8b96143c; Blue c1a955316055aaf6c1b28853e21ed07e36e55f6a
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN: none from phase-1 through phase-3 discriminating suites. Overall deep audit remains INCOMPLETE; hypotheses below are not CLOSED.
* defects CONFIRMED CLOSED:
  - phase-1: FUTURE_DUE_MISCLASSIFIED_AS_FUTURE_EVIDENCE; NULL_DUE_ERASES_EXPECTED_WORK; CYCLIC_SUPERSESSION_FALSE_PASS; MISSING_OBSERVED_TIME_NOT_VALIDATED; INFINITE_GRACE_FALSE_PASS; CORRUPT_EVIDENCE_NO_AUDIT_VERDICT; MATERIALIZATION_MISMATCH_NOT_DURABLE; RESTART_REWRITES_OPEN_OBLIGATION; SOCKET_TRICKLE_EXCEEDS_TOTAL_DEADLINE.
  - phase-2: REQUEST_EVENT_ORDER_ACCEPTED; COLLECTOR_STATE_HISTORY_REBOOTSTRAP; READINESS_FALSE_POSITIVE_WITHOUT_CAPTURE; PUBLIC_SNAPSHOT_ACTIVITY_PROXY; SHARED_EVENT_CAPTURE_PROXY; PARTIAL_PAGINATION_TASK_LOSS; RECONCILIATION_PERMANENT_4XX_HOT_LOOP; TERMINAL_SUCCESS_NO_SUCCESSOR_OBLIGATION; MATERIALIZED_COMMIT_METADATA_UNBOUND; MUTATING_CLI_SINGLE_WRITER_BYPASS; HISTORICAL_ARTIFACT_PROXY_REPUBLICATION.
  - phase-3: FORGED_CHILD_LIFECYCLE_ENV_BUYS_QUALIFYING_READINESS; FUTURE_LAST_POLL_SUPPRESSES_DUE_ACQUISITION; VERIFICATION_DIGEST_OMITS_SYSTEMD_UNIT.
* hypotheses NOT YET REPRODUCED: unsolicited child exit code 0 can stop continuous service cleanly; scheduler/lifecycle audit is not explicitly bounded to future Blue t0 and may count pre-t0 evidence/interventions; historical lifecycle journal may lack append-only external supervisor launch/exit authority; truncated task-id collision may drop distinct filing tasks; remaining supervisor SIGTERM/SIGINT/SIGHUP/abrupt-death/restart-limit cases; target-host effective systemd unit; deeper PIT/request-budget crash matrix; concurrent/interrupted materialization; additional indirect firewall leaks; exact final commit/tree/fingerprint/runtime/service-definition binding; final exact-head rodage.
* tests rouges ajoutés: phase-3 Phase3AuthorityAndBindingCampaign at 1e11b221b69a33e9b303865724a648416194d49f. Exact discriminating red run 35461894468 on c2edb2993b1ab044bbd9bc3cd80be6c7fd1b66f1: 350 tests, exactly 3 failures.
* tests verts obtenus: exact-head run 35462209546 on fd16fbd2df4378bcb27e9feb05170d9047e5f11f: full suite 350/350 PASS; SEC P0 lane PASS; V1 demo 35/35 PASS. The verification-artifact step alone remains red because final verification was intentionally not regenerated after acquisition-critical changes.
* full-suite status: PASS on exact code head fd16fbd2df4378bcb27e9feb05170d9047e5f11f, run 35462209546.
* CI run id/status: 35462209546 / FAILURE overall solely at stale verification-artifact gate; all executable test/schema/status/demo gates passed.
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1; final freeze not performed
* rodage status + exact artifact: NOT RUN on fd16fbd2df4378bcb27e9feb05170d9047e5f11f; historical artifacts have no current proof authority
* readiness status: NOT ESTABLISHED on actual target service
* audit status: phase-1/2/3 discriminants green; deep adversarial campaign INCOMPLETE
* firewall status: current phase-2 public-surface regressions green; final broad firewall audit still required
* fichiers acquisition-critical modifiés in phase-3: src/quant/dataplane/sec/collector.py; scripts/verify_p0.py
* prochaine action unique: add discriminating red tests for remaining lifecycle/window/task-identity failure scenarios, obtain an exact-head CI red, then correct only reproduced blockers
* commandes exactes nécessaires pour reproduire/reprendre:
  git clone --branch astra/p0-deep-adversarial-pre-t0 https://github.com/fahimahmedb/Quant-Trade.git
  cd Quant-Trade
  git checkout fd16fbd2df4378bcb27e9feb05170d9047e5f11f
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0 -v
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  PYTHONPATH=src python3 -m unittest tests.test_sec_form4_capture tests.test_p0_adversarial -v
  python3 scripts/status_artifacts.py --check
  PYTHONPATH=src python3 scripts/verify_p0.py --check --sha fd16fbd2df4378bcb27e9feb05170d9047e5f11f
  git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD

Red evidence phase-3: run 35461894468. Green executable evidence phase-3: run 35462209546. Verification artifact intentionally remains stale until acquisition-critical code is frozen. No new branch, no merge, no Blue review request, no t0 declaration, no 14-day claim.
