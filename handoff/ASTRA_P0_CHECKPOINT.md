# CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T23:59:00Z
* branch: `@astra/p0-deep-adversarial-pre-t0` (requested single branch; repository handoff documents omit the leading `@`)
* VERIFIED_CODE_SHA: `b42ae73a805cc8a137561239c60fe917daf83c7b`
* documentation-only correction: this checkpoint update is committed after `VERIFIED_CODE_SHA`; its commit SHA is not the code SHA tested by run 35472851297
* parent/base SHA: continuation handoff `f823a6d133dd8da8d7ed2dc4b6a9b227f37743c5`; phase-6 production correction `0150419c0ed0fd24df2491df8f3b4e51bf037764`; phase-6 red `d737eabee8f502e30852b3594972c5bcbbde2dbd`; audit baseline `8d5dbb41559c4716e94d5290b6ae979a8b96143c`
* t0 status: **NOT DECLARED**
* P0_CONTINUOUS_SERVICE_STATE: **OPEN / NOT_YET_PROVEN_CONTINUOUS**
* defects CONFIRMED OPEN: none from phase 6; deeper campaign remains incomplete and may produce new blockers
* defects CONFIRMED CLOSED:
  - `GLOBAL_MAX_CONCURRENCY_NOT_HELD_FOR_NETWORK_WINDOW` — prior red run 35471064118; production `network_slot()` correction at 0150419; process-shared real-socket discriminant green at verified code SHA `b42ae73a805cc8a137561239c60fe917daf83c7b`.
  - `QUALIFYING_MISSING_FINGERPRINT_AUTO_MATERIALIZATION_ATTEMPT` — prior red run 35471064118; qualifying supervisor now fails closed; discriminant green locally.
  - `READINESS_WEAKER_THAN_EXTERNAL_AUTHORITY_AUDIT` — prior red run 35471064118; readiness consumes the audit authority contract; discriminant green locally.
  - `STATUS_ARTIFACT_TEST_INVENTORY_FALSE_GREEN` — promoted after repaired regex/discovery harness reproduced `310 != 371`; status generation now counts discovery in a fresh interpreter and committed STATE reports 371; discriminant green locally.
  - phase-5 six blockers remain green in the phase-6/full local suite.
* hypotheses NOT YET REPRODUCED: restart-limit exhaustion; SIGTERM/systemctl stop-start semantics; supervisor SIGKILL child-death behavior; exact loaded systemd RestartUSec/StartLimitIntervalUSec/KillSignal/TimeoutStopUSec validation; truly concurrent/interrupted materialization; deeper budget/state journal failure ordering; remaining PIT crash boundaries and public/protocol proxy leaks; final evidence binding and target-host rodage.
* red tests: GitHub Actions 35471064118 (3 genuine phase-6 failures plus malformed inventory-test error); repaired inventory test subsequently reproduced the intended `310 != 371` failure locally.
* green tests: `PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase6ProofAndConcurrencyCampaign -v` — 4/4 PASS; `PYTHONPATH=src python3 -m unittest discover -s tests` — 371/371 PASS.
* full-suite status: **371/371 PASS** at VERIFIED_CODE_SHA `b42ae73a805cc8a137561239c60fe917daf83c7b`.
* EXACT_HEAD_CI_RUN: `35472851297`
* EXACT_HEAD_CI_STATUS: **COMPLETED / SUCCESS**
* exact-head CI evidence at VERIFIED_CODE_SHA `b42ae73a805cc8a137561239c60fe917daf83c7b`:
  - 371/371 full suite: **PASS**
  - SEC P0 lane: **PASS**
  - V1 end-to-end: **PASS**
  - exact-head verification artifact generation/upload: **PASS**
  - clean working tree: **PASS**
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: `p0_materialized_fingerprint/v2`; `acquisition_critical_fingerprint/v1`; final freeze not performed
* final rodage exact artifact/status: **NOT YET RUN** on final code/target runtime
* 14-day continuity: **NOT PROVEN**; no claim is made about the required weekend or silence interval
* readiness: phase-6 local discriminant green; final target-runtime readiness NOT ESTABLISHED
* audit: phase-6 local authority/readiness consistency green; final coherent exact-head audit pending
* firewall: prior regressions green in 371-test suite; final broad audit pending
* acquisition-critical files changed since handoff: production correction 0150419 changed budget/collector/supervisor and therefore changes the acquisition fingerprint; VERIFIED_CODE_SHA `b42ae73a805cc8a137561239c60fe917daf83c7b` includes the phase-6 tests/status-artifact correction.
* next unique action: merge disposition for PR #18 after this documentation-only correction; do not infer that this documentation commit was the code tested by exact-head run 35472851297.
* exact resume commands:
  - `git checkout @astra/p0-deep-adversarial-pre-t0`
  - `git log --oneline f823a6d..HEAD`
  - `PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase6ProofAndConcurrencyCampaign -v`
  - `PYTHONPATH=src python3 -m unittest discover -s tests`
  - `PYTHONPATH=src python3 scripts/status_artifacts.py --check`
  - `git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD`

No merge, no Blue review request, no t0 declaration, and no claim that rodage proves the 14-day window.
