CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T18:58:30Z
* branch: astra/p0-deep-adversarial-pre-t0
* exact HEAD SHA: 33ccd64a701301894a2e32a801853977f5f61c11 (phase-4 red test head; this checkpoint is a subsequent documentation-only commit)
* parent/base SHA: parent 8fb8b75101f89dbca6e14e05e2f56b77baa6ba9d; phase-3 green code head fd16fbd2df4378bcb27e9feb05170d9047e5f11f; audit baseline 8d5dbb41559c4716e94d5290b6ae979a8b96143c; Blue c1a955316055aaf6c1b28853e21ed07e36e55f6a
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN:
  - UNSOLICITED_ZERO_CHILD_EXIT_STOPS_CONTINUOUS_SERVICE — BLOCKS_CAPTURE_INTEGRITY. In qualifying mode, a child that terminates unexpectedly with exit code 0 makes the external supervisor return 0; systemd Restart=on-failure therefore need not restart the dead acquisition service.
  - TRUNCATED_TASK_ID_COLLISION_DROPS_DISTINCT_FILING — BLOCKS_CAPTURE_INTEGRITY. Two distinct full filing identity digests sharing the first 16 hex characters get the same truncated task_id; acknowledging one causes _drop_task() to delete both queued tasks.
  - QUALIFYING_AUDIT_LACKS_EXTERNAL_LIFECYCLE_AUTHORITY — BLOCKS_CAPTURE_INTEGRITY. audit_observation_window accepts qualifying child lifecycle journal records without any append-only external supervisor launch/exit evidence.
  - AUDIT_WINDOW_NOT_BOUND_TO_BLUE_T0 — BLOCKS_CAPTURE_INTEGRITY. The retrospective audit has no externally supplied t0/window_start and therefore derives duration/interventions from the whole journal history, allowing pre-t0 history to contaminate or inflate the qualifying window.
* defects CONFIRMED CLOSED: all phase-1, phase-2 and phase-3 findings from prior checkpoints remain closed; no phase-4 finding is closed yet.
* hypotheses NOT YET REPRODUCED: automatic-restart witness binding details inside the future external supervisor ledger; signal/abrupt supervisor death/restart-limit exhaustion matrix beyond current tests; target-host effective loaded unit; deeper PIT/request-budget crash matrix; concurrent/interrupted materialization; additional indirect firewall leaks; exact final evidence binding/rodage.
* tests rouges ajoutés: Phase4LifecycleAndWindowCampaign + Phase4AuditWindowCampaign in tests/test_astra_pre_t0.py at 33ccd64a701301894a2e32a801853977f5f61c11.
* tests verts obtenus: phase-1/2/3 remain green. No phase-4 green claim.
* full-suite status: FAIL on exact head 33ccd64a701301894a2e32a801853977f5f61c11: GitHub Actions run 35462679187, 361 tests, 3 failures + 1 error exactly corresponding to the four phase-4 discriminants.
* CI run id/status: 35462679187 / FAILURE after status/schema pre-gates passed and full suite reached all phase-4 tests.
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1; final freeze not performed
* rodage status + exact artifact: NOT RUN on current code; historical artifacts have no current proof authority
* readiness status: NOT ESTABLISHED on actual target service
* audit status: phase-4 FAIL with four confirmed blockers open
* firewall status: phase-2 public-surface regressions remain green; final broad firewall audit still required
* fichiers acquisition-critical modifiés: none in phase-4 red commit; tests only
* prochaine action unique: minimally close the four reproduced phase-4 defects: append-only external supervisor launch/exit ledger + audit binding, externally supplied audit window_start, collision-safe task identity, and nonzero supervisor failure for unsolicited qualifying child exit; keep red tests discriminating
* commandes exactes nécessaires pour reproduire/reprendre:
  git clone --branch astra/p0-deep-adversarial-pre-t0 https://github.com/fahimahmedb/Quant-Trade.git
  cd Quant-Trade
  git checkout 33ccd64a701301894a2e32a801853977f5f61c11
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase4LifecycleAndWindowCampaign tests.test_astra_pre_t0.Phase4AuditWindowCampaign -v
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD

Exact red evidence: run 35462679187. No new branch, no merge, no Blue review request, no t0 declaration, no 14-day claim.
