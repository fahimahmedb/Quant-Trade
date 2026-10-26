# CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T23:59:00Z
* branch: `@astra/p0-deep-adversarial-pre-t0` (requested single branch; repository handoff documents omit the leading `@`)
* exact code HEAD SHA: `1407bf9ce1ad9de38c4780ab103286a67cbc4681` (this checkpoint is the immediately following documentation-only commit)
* parent/base SHA: continuation handoff `f823a6d133dd8da8d7ed2dc4b6a9b227f37743c5`; phase-6 production correction `0150419c0ed0fd24df2491df8f3b4e51bf037764`; phase-6 red `d737eabee8f502e30852b3594972c5bcbbde2dbd`; audit baseline `8d5dbb41559c4716e94d5290b6ae979a8b96143c`
* t0 status: **NOT DECLARED**
* P0_CONTINUOUS_SERVICE_STATE: **OPEN / NOT_YET_PROVEN_CONTINUOUS**
* defects CONFIRMED OPEN: none from phase 6; deeper campaign remains incomplete and may produce new blockers
* defects CONFIRMED CLOSED:
  - `GLOBAL_MAX_CONCURRENCY_NOT_HELD_FOR_NETWORK_WINDOW` — prior red run 35471064118; production `network_slot()` correction at 0150419; process-shared real-socket discriminant green locally at 1407bf9.
  - `QUALIFYING_MISSING_FINGERPRINT_AUTO_MATERIALIZATION_ATTEMPT` — prior red run 35471064118; qualifying supervisor now fails closed; discriminant green locally.
  - `READINESS_WEAKER_THAN_EXTERNAL_AUTHORITY_AUDIT` — prior red run 35471064118; readiness consumes the audit authority contract; discriminant green locally.
  - `STATUS_ARTIFACT_TEST_INVENTORY_FALSE_GREEN` — promoted after repaired regex/discovery harness reproduced `310 != 371`; status generation now counts discovery in a fresh interpreter and committed STATE reports 371; discriminant green locally.
  - phase-5 six blockers remain green in the phase-6/full local suite.
* hypotheses NOT YET REPRODUCED: restart-limit exhaustion; SIGTERM/systemctl stop-start semantics; supervisor SIGKILL child-death behavior; exact loaded systemd RestartUSec/StartLimitIntervalUSec/KillSignal/TimeoutStopUSec validation; truly concurrent/interrupted materialization; deeper budget/state journal failure ordering; remaining PIT crash boundaries and public/protocol proxy leaks; final evidence binding and target-host rodage.
* red tests: GitHub Actions 35471064118 (3 genuine phase-6 failures plus malformed inventory-test error); repaired inventory test subsequently reproduced the intended `310 != 371` failure locally.
* green tests: `PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase6ProofAndConcurrencyCampaign -v` — 4/4 PASS; `PYTHONPATH=src python3 -m unittest discover -s tests` — 371/371 PASS.
* full-suite status: **GREEN locally at 1407bf9**, 371 tests in 41.163s; exact-head CI not yet obtained.
* CI run id/status: phase-6 red 35471064118 / FAILURE is preserved; exact-head CI for 1407bf9 is **NOT AVAILABLE** because this environment cannot authenticate/push to GitHub (`CONNECT tunnel failed, response 403`; `gh` has no token).
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: `p0_materialized_fingerprint/v2`; `acquisition_critical_fingerprint/v1`; final freeze not performed
* rodage exact artifact/status: NOT RUN on final code/target runtime; no claim about 14 days, weekend, or silence interval
* readiness: phase-6 local discriminant green; final target-runtime readiness NOT ESTABLISHED
* audit: phase-6 local authority/readiness consistency green; final coherent exact-head audit pending
* firewall: prior regressions green in 371-test suite; final broad audit pending
* acquisition-critical files changed since handoff: production correction 0150419 changed budget/collector/supervisor and therefore changes the acquisition fingerprint; 1407bf9 changes tests/status artifacts only.
* next unique action: push 1407bf9 plus this checkpoint to the same remote branch, obtain exact-head CI, then begin the non-duplicative phase-7 campaign with red tests for restart-limit/signal/SIGKILL and exact loaded-systemd policy semantics.
* exact resume commands:
  - `git checkout @astra/p0-deep-adversarial-pre-t0`
  - `git log --oneline f823a6d..HEAD`
  - `PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase6ProofAndConcurrencyCampaign -v`
  - `PYTHONPATH=src python3 -m unittest discover -s tests`
  - `PYTHONPATH=src python3 scripts/status_artifacts.py --check`
  - `git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD`

No merge, no Blue review request, no t0 declaration, and no claim that rodage proves the 14-day window.
