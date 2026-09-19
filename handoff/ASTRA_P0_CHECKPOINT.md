CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T21:14:30Z
* branch: astra/p0-deep-adversarial-pre-t0
* exact HEAD SHA: 3001db6afc07951b0da7c0d0004d8b6afd7b1f03 (documentation head above phase-5 red-test SHA a59fb8d26707da84db9ed9eb71021f26e5e794f0; this checkpoint is the immediately following documentation-only commit)
* parent/base SHA: phase-5 red head a59fb8d26707da84db9ed9eb71021f26e5e794f0; phase-4 green code head b7b4502c37aa34d012413c7f7b8672ecabba9ced; audit baseline 8d5dbb41559c4716e94d5290b6ae979a8b96143c; Blue c1a955316055aaf6c1b28853e21ed07e36e55f6a
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN:
  - AUTOMATIC_RESTART_EXTERNAL_WITNESS_MISSING — BLOCKS_CAPTURE_INTEGRITY. Automatic cause can be accepted with launch event but no prior external CHILD_EXIT_OBSERVED witness.
  - DEPLOYMENT_AUTHORITY_CONSUMPTION_UNBOUND — BLOCKS_CAPTURE_INTEGRITY. DEPLOYMENT_RESTART can audit clean without the durable consumed authority ledger.
  - EFFECTIVE_SYSTEMD_POLICY_MISMATCH_ACCEPTED — BLOCKS_CAPTURE_INTEGRITY. Loaded systemd Restart=no is accepted when fragment bytes equal repository unit.
  - BLUE_T0_WINDOW_NOT_PLUMBED_TO_OPERATOR_CLI — BLOCKS_CAPTURE_INTEGRITY. sec-audit rejects --window-start, so the production operator path cannot invoke the phase-4 window contract.
  - SIGHUP_CLEANLY_STOPS_QUALIFYING_SERVICE — BLOCKS_CAPTURE_INTEGRITY. Qualifying supervisor handles SIGHUP as clean stop and returns 0, defeating Restart=on-failure.
  - EXACT_VERIFICATION_SHA_NOT_ENFORCED — BLOCKS_CAPTURE_INTEGRITY. verify_p0 --check --sha reports a SHA mismatch only as a note and exits 0 when tree digest matches.
* defects CONFIRMED CLOSED: all phase-1/2/3 findings plus phase-4 UNSOLICITED_ZERO_CHILD_EXIT_STOPS_CONTINUOUS_SERVICE; TRUNCATED_TASK_ID_COLLISION_DROPS_DISTINCT_FILING; QUALIFYING_AUDIT_LACKS_EXTERNAL_LIFECYCLE_AUTHORITY; AUDIT_WINDOW_NOT_BOUND_TO_BLUE_T0. Phase-4 green evidence: run 35469270137 at b7b4502c, full suite 361 PASS, SEC P0 PASS, V1 35/35 PASS; workflow failed only stale verification artifact.
* hypotheses NOT YET REPRODUCED: STATUS_ARTIFACT_TEST_INVENTORY_FALSE_GREEN (CI freshness step passes while committed STATE.md still says 310 tests and exact full suite now discovers 367); global max_concurrency=1 enforcement across truly parallel SEC consumers; deeper PIT state/journal/disk-full crash matrix; concurrent/interrupted materialization; target-host effective loaded unit; additional indirect firewall leaks; final exact rodage/runtime binding.
* tests rouges ajoutés: Phase5AuthorityBindingCampaign at a59fb8d26707da84db9ed9eb71021f26e5e794f0. Exact CI run 35469598503: 367 tests, 6 failures, exactly the six discriminants above.
* tests verts obtenus: phase-5 NONE yet. Phase-4 remains green as documented.
* full-suite status: RED on exact phase-5 head a59fb8d26707da84db9ed9eb71021f26e5e794f0: 367 tests, 6 failures.
* CI run id/status: 35469598503 / FAILURE, full suite red at six phase-5 discriminants. Phase-4 run 35469270137 green through full/SEC/V1, stale-verification failure only.
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1; final freeze not performed
* rodage status + exact artifact: NOT RUN on final code
* readiness status: NOT ESTABLISHED on actual target service
* audit status: phase-5 lifecycle authority and CLI binding blockers confirmed open
* firewall status: prior firewall suite remains green through phase-4; final broad audit pending
* fichiers acquisition-critical modifiés: phase-5 red commit modifies tests only. Candidate fixes must touch audit.py, supervisor launcher, scripts/quant.py, scripts/verify_p0.py and possibly workflow/evidence surfaces.
* prochaine action unique: close the six confirmed phase-5 defects with minimal production changes, retain discriminating tests, and obtain exact-head green before opening the next PIT/evidence campaign.
* commandes exactes nécessaires pour reproduire/reprendre:
  git clone --branch astra/p0-deep-adversarial-pre-t0 https://github.com/fahimahmedb/Quant-Trade.git
  cd Quant-Trade
  git checkout a59fb8d26707da84db9ed9eb71021f26e5e794f0
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase5AuthorityBindingCampaign -v
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD

No merge, no Blue review request, no t0 declaration, no 14-day claim.
