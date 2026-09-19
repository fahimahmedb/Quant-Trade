CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T21:44:30Z
* branch: astra/p0-deep-adversarial-pre-t0
* exact HEAD SHA: d737eabee8f502e30852b3594972c5bcbbde2dbd (phase-6 tests-only head; this checkpoint is the immediately following documentation-only commit)
* parent/base SHA: phase-6 parent a82f749463f797a3352549dbc2581004c569f25e; phase-5 production fix eefd544dd9ad2a2b545362cb21d6402f7c733624; phase-5 red head a59fb8d26707da84db9ed9eb71021f26e5e794f0; phase-4 green code head b7b4502c37aa34d012413c7f7b8672ecabba9ced; audit baseline 8d5dbb41559c4716e94d5290b6ae979a8b96143c; Blue c1a955316055aaf6c1b28853e21ed07e36e55f6a
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN:
  - Phase-5 six blockers were red-proven at run 35469598503 and have candidate production fixes in eefd544dd9ad2a2b545362cb21d6402f7c733624:
    AUTOMATIC_RESTART_EXTERNAL_WITNESS_MISSING;
    DEPLOYMENT_AUTHORITY_CONSUMPTION_UNBOUND;
    EFFECTIVE_SYSTEMD_POLICY_MISMATCH_ACCEPTED;
    BLUE_T0_WINDOW_NOT_PLUMBED_TO_OPERATOR_CLI;
    SIGHUP_CLEANLY_STOPS_QUALIFYING_SERVICE;
    EXACT_VERIFICATION_SHA_NOT_ENFORCED.
    They are NOT yet promoted CLOSED in this checkpoint because the final exact-head green workflow has not completed.
  - Final exact runtime/materialized fingerprint/readiness/rodage/evidence binding remains open by construction.
* defects CONFIRMED CLOSED:
  - all phase-1/2/3 findings from prior checkpoints;
  - phase-4 four defects: UNSOLICITED_ZERO_CHILD_EXIT_STOPS_CONTINUOUS_SERVICE; TRUNCATED_TASK_ID_COLLISION_DROPS_DISTINCT_FILING; QUALIFYING_AUDIT_LACKS_EXTERNAL_LIFECYCLE_AUTHORITY; AUDIT_WINDOW_NOT_BOUND_TO_BLUE_T0. Red run 35462679187; green code run 35469270137 passed full suite 361, SEC P0 and V1 before failing only stale verification artifact.
* hypotheses NOT YET REPRODUCED / phase-6:
  - STATUS_ARTIFACT_TEST_INVENTORY_FALSE_GREEN;
  - GLOBAL_MAX_CONCURRENCY_ONE_NOT_HELD_OVER_NETWORK_WINDOW;
  - QUALIFYING_LAUNCH_AUTO_CREATES_MISSING_MATERIALIZATION;
  - READINESS_AND_AUDIT_USE_DIFFERENT_DEPLOYMENT_AUTHORITY;
  - plus remaining target-host effective-unit proof, deeper PIT/interrupted write boundaries not already covered, additional firewall proxies, final exact rodage/runtime binding.
* tests rouges ajoutés:
  - phase-5 Phase5AuthorityBindingCampaign at a59fb8d26707da84db9ed9eb71021f26e5e794f0, run 35469598503: exactly 6 failures.
  - phase-6 Phase6ProofAndConcurrencyCampaign at d737eabee8f502e30852b3594972c5bcbbde2dbd. Run 35471064118 currently IN_PROGRESS; no phase-6 finding may be promoted until this exact run reaches the new tests.
* tests verts obtenus:
  - phase-4 exact green as above.
  - phase-5 repair lineage: eefd544d introduced production fixes; 4d9b89b repaired test helper scoping; a82f749 mirrored the newly fingerprint-critical workflow into temp-repo fingerprint fixtures. Run 35470924225 on a82f749 has passed Status artifact freshness, Full unit suite and SEC P0 lane suite; V1 is still in progress at checkpoint time. This is strong but not yet final exact-head certification.
* full-suite status: GREEN on a82f749463f797a3352549dbc2581004c569f25e (run 35470924225 full suite step success). Phase-6 head d737eabe full suite is IN_PROGRESS in run 35471064118.
* CI run id/status:
  - 35469598503: phase-5 RED, six discriminants.
  - 35470532302: eefd candidate failed due test-fixture scoping errors, not production findings.
  - 35470736441: 4d9 repair passed most suite but failed fingerprint temp mirrors missing the newly fingerprinted workflow.
  - 35470924225: a82 repair IN_PROGRESS; full + SEC P0 green, V1 in progress.
  - 35471064118: d737 phase-6 exact-head IN_PROGRESS.
* active fingerprint: NOT MEASURED IN ACTUAL TARGET SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE ON FINAL TARGET STATE
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1; final freeze not performed
* rodage status + exact artifact: NOT RUN on final code/head; historical rodage artifacts are superseded and have no current authority
* readiness status: NOT ESTABLISHED on actual target service
* audit status: phase-4 closed; phase-5 candidate fixes under final CI; phase-6 new falsification in progress
* firewall status: prior firewall regressions green through phase-4 and phase-5 repair suites; final broad audit not yet closed
* fichiers acquisition-critical modifiés since phase-5 red:
  - src/quant/dataplane/sec/audit.py
  - deploy/quant_sec_supervisor.py
  - scripts/quant.py
  - scripts/verify_p0.py
  - src/quant/dataplane/sec/fingerprint.py
  - .github/workflows/sec-p0-pre-t0-gate.yml
  - tests/test_sec_form4_capture.py fixtures
  Phase-6 d737 itself adds tests only.
* prochaine action unique: inspect exact-head run 35471064118. Promote only phase-6 tests that actually fail to CONFIRMED OPEN. If phase-5 discriminants and existing suites are green on current lineage, mark those six phase-5 blockers CLOSED with red→green references, then fix only reproduced phase-6 defects. Do NOT start final rodage until code/fingerprint-critical membership is frozen and all class 1–3 blockers are closed.
* commandes exactes nécessaires pour reproduire/reprendre:
  git clone --branch astra/p0-deep-adversarial-pre-t0 https://github.com/fahimahmedb/Quant-Trade.git
  cd Quant-Trade
  git checkout d737eabee8f502e30852b3594972c5bcbbde2dbd
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase5AuthorityBindingCampaign -v
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase6ProofAndConcurrencyCampaign -v
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  python3 scripts/demo_quant_system.py
  git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD

Codex handoff rule: repository is authority; do not inherit uncommitted/local state; do not create another branch; continue only astra/p0-deep-adversarial-pre-t0; checkpoint after every materially significant step; no Blue review until final exit criteria; t0 remains NOT DECLARED; P0_CONTINUOUS_SERVICE_STATE remains OPEN / NOT_YET_PROVEN_CONTINUOUS; no 14-day claim.
