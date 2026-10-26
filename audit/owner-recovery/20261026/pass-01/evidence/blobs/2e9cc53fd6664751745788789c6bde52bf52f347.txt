CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T21:04:30Z
* branch: astra/p0-deep-adversarial-pre-t0
* exact HEAD SHA: b7b4502c37aa34d012413c7f7b8672ecabba9ced (phase-4 candidate fix head; this checkpoint is the immediately following documentation-only commit)
* parent/base SHA: parent 0d2fb019e3656da086e69f42c1c89cfaed96d668; phase-4 red head 33ccd64a701301894a2e32a801853977f5f61c11; audit baseline 8d5dbb41559c4716e94d5290b6ae979a8b96143c; Blue c1a955316055aaf6c1b28853e21ed07e36e55f6a
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN: UNSOLICITED_ZERO_CHILD_EXIT_STOPS_CONTINUOUS_SERVICE; TRUNCATED_TASK_ID_COLLISION_DROPS_DISTINCT_FILING; QUALIFYING_AUDIT_LACKS_EXTERNAL_LIFECYCLE_AUTHORITY; AUDIT_WINDOW_NOT_BOUND_TO_BLUE_T0. All remain OPEN until exact-head green evidence.
* defects CONFIRMED CLOSED: all phase-1/2/3 findings from prior checkpoints. No phase-4 CLOSED claim yet.
* hypotheses NOT YET REPRODUCED: external automatic-restart witness binding details; supervisor SIGTERM/SIGHUP/SIGKILL/restart-limit exhaustion; target-host effective loaded unit; deeper PIT/request-budget crash matrix; concurrent/interrupted materialization; additional indirect firewall leaks; exact final evidence binding and rodage.
* tests rouges ajoutés: unchanged phase-4 discriminants at 33ccd64a701301894a2e32a801853977f5f61c11; exact red run 35462679187.
* tests verts obtenus: phase-1/2/3 remain green. Phase-4 candidate code has CI run 35469270137 in progress.
* full-suite status: PENDING on b7b4502c37aa34d012413c7f7b8672ecabba9ced
* CI run id/status: 35469270137 / IN_PROGRESS
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1; final freeze not performed
* rodage status + exact artifact: NOT RUN on current code
* readiness status: NOT ESTABLISHED on actual target service
* audit status: candidate fixes pushed; green not yet established
* firewall status: prior public-surface regressions remain green; final broad firewall audit pending
* fichiers acquisition-critical modifiés: src/quant/dataplane/sec/audit.py; src/quant/dataplane/sec/collector.py; deploy/quant_sec_supervisor.py. Test fixture updated in tests/test_sec_form4_capture.py.
* prochaine action unique: inspect exact-head run 35469270137. If phase-4 discriminants/full suite are green, move these four findings to CLOSED and immediately begin phase-5 lifecycle/PIT/evidence-binding falsification; otherwise diagnose only the concrete regression.
* commandes exactes nécessaires pour reproduire/reprendre:
  git clone --branch astra/p0-deep-adversarial-pre-t0 https://github.com/fahimahmedb/Quant-Trade.git
  cd Quant-Trade
  git checkout b7b4502c37aa34d012413c7f7b8672ecabba9ced
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase4LifecycleAndWindowCampaign tests.test_astra_pre_t0.Phase4AuditWindowCampaign -v
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD

Implementation summary on b7b4502c:
- qualifying child exit code 0 is treated as unexpected service failure unless the supervisor itself is stopping;
- external supervisor writes append-only CHILD_LAUNCH_AUTHORIZED / CHILD_EXIT_OBSERVED records;
- audit can be explicitly bounded by Blue-supplied window_start and excludes pre-window lifecycle interventions while preserving obligations due inside the window;
- qualifying audit binds child lifecycle to the external supervisor ledger;
- queue acknowledgement removes by full identity_digest, never the truncated diagnostic task_id.

No merge, no Blue review request, no t0 declaration, no 14-day claim.
