CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T14:47:30Z
* branch: astra/p0-deep-adversarial-pre-t0
* exact HEAD SHA: 99358df8e32aef02ace778535c92f2d6fbc64cff (code/test head; this checkpoint is the immediately following documentation-only commit)
* parent/base SHA: code parent chain starts at 14aacccc34e394770a6c344b0101be665d7438c2; phase-1 code head ccc17f2c8f8e5b59d3b560ff53f36533b89a2856; audit baseline 8d5dbb41559c4716e94d5290b6ae979a8b96143c; Blue c1a955316055aaf6c1b28853e21ed07e36e55f6a
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN:
  - REQUEST_EVENT_ORDER_ACCEPTED — BLOCKS_CAPTURE_INTEGRITY. Red: test_request_intent_order_is_authority_not_just_event_counts, CI run 35448899020 at 14aacccc.
  - COLLECTOR_STATE_HISTORY_REBOOTSTRAP — BLOCKS_PIT_RECONSTRUCTABILITY. Red: deleting collector state and its commit ledger after a poll allowed fresh state despite acquisition history.
  - READINESS_FALSE_POSITIVE_WITHOUT_CAPTURE — BLOCKS_CAPTURE_INTEGRITY. Red: qualifying lifecycle + materialization + scheduler, no request, readiness true.
  - PUBLIC_SNAPSHOT_ACTIVITY_PROXY — BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL. Red: snapshot recent events exposed byte_length/raw object/discovery object proxies.
  - SHARED_EVENT_CAPTURE_PROXY — BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL. Red: shared EventLog contained one sec_raw_capture row per acquisition plus discovery result metadata.
  - PARTIAL_PAGINATION_TASK_LOSS — BLOCKS_CAPTURE_INTEGRITY. Red: successful first discovery page followed by 503 left pending_tasks empty.
  - RECONCILIATION_PERMANENT_4XX_HOT_LOOP — BLOCKS_CAPTURE_INTEGRITY. Red: 404 left zero cooldown.
  - TERMINAL_SUCCESS_NO_SUCCESSOR_OBLIGATION — BLOCKS_CAPTURE_INTEGRITY. Red: request resolved the only obligation, then one-hour stop still audited accountable=true.
  - MATERIALIZED_COMMIT_METADATA_UNBOUND — BLOCKS_CAPTURE_INTEGRITY. Red: top-level git_commit could be changed while materialization validation returned no error.
  - MUTATING_CLI_SINGLE_WRITER_BYPASS — BLOCKS_CAPTURE_INTEGRITY. Red: sec-disable succeeded while collector_service.lock was held and constructed/mutated state.
  - HISTORICAL_ARTIFACT_PROXY_REPUBLICATION — BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL. Red: four current handoff JSON artifacts republished historical activity/count/timing proxies.
  All eleven were durably reproduced by exact-head CI run 35448899020: 347 tests, 14 failures (four failures are artifact instances of one defect).
* defects CONFIRMED CLOSED:
  - Phase-1 only: FUTURE_DUE_MISCLASSIFIED_AS_FUTURE_EVIDENCE; NULL_DUE_ERASES_EXPECTED_WORK; CYCLIC_SUPERSESSION_FALSE_PASS; MISSING_OBSERVED_TIME_NOT_VALIDATED; INFINITE_GRACE_FALSE_PASS; CORRUPT_EVIDENCE_NO_AUDIT_VERDICT; MATERIALIZATION_MISMATCH_NOT_DURABLE; RESTART_REWRITES_OPEN_OBLIGATION; SOCKET_TRICKLE_EXCEEDS_TOTAL_DEADLINE. See handoff/ASTRA_PRE_T0_FINDINGS.md for red/green provenance.
  - NONE of the phase-2 defects above is CLOSED yet. Fixes are pushed but await exact-head green reproduction.
* hypotheses NOT YET REPRODUCED: durable deployment-authority laundering/forgery boundary; supervisor signal matrix (SIGTERM/SIGHUP/SIGKILL and restart-limit exhaustion); target-host effective systemd unit; request/budget crash ordering beyond the request-intent order defect; full PIT kill matrix at raw/envelope/state boundaries; clock-skew/future timestamps across supervisor state; concurrent materialization and interrupted freeze; exact final evidence binding and rodage.
* tests rouges ajoutés: tests/test_astra_pre_t0.py phase-1 red commit 35731abb479677888f4c2f4638b2cedf23f08343; phase-2 tests at c452438da4bcf98f496fe2d6a977bc415de839c7. Durable phase-2 red execution: run 35448899020 at 14aacccc34e394770a6c344b0101be665d7438c2 after STATE.md inventory refresh.
* tests verts obtenus: phase-1 13/13 and full suite 336 PASS LOCAL documented at ccc17f2c. Phase-2 green: NOT YET ESTABLISHED.
* full-suite status: RED on prior checkpoint head 4f928e47126ed2cbe214d7d504856b00fe15b29d, run 35449542201: 347 tests, 6 failures + 4 errors. Candidate regression fixes are now at 99358df8e32aef02ace778535c92f2d6fbc64cff; exact-head green is PENDING.
* CI run id/status: phase-2 original red reproduction 35448899020 FAILURE at 14aacccc; first corrected run 35449542201 FAILURE at 4f928e47 (6 failures + 4 errors); exact 99358df8 CI pending.
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1; final freeze not performed
* rodage status + exact artifact: NOT RUN on corrected code; historical artifacts are now count-free projections with original Git blob provenance and are NOT current proof
* readiness status: NOT ESTABLISHED
* audit status: phase-2 false-pass reproductions confirmed; fixes not yet green
* firewall status: RED reproduction confirmed at 14aacccc; corrected projections pushed, green not yet established
* fichiers acquisition-critical modifiés:
  - src/quant/dataplane/sec/audit.py (ca64db4fd63de8d357342107106619a36a414019)
  - src/quant/dataplane/sec/collector.py (a6170ebed4ec400c8239326fccef7856be09a226)
  - src/quant/clock.py (b6cb3bd6c82a8af4abd36ce2c97cde4268dd9279)
  - scripts/quant.py (d2575ce046060b19f992a74efb0e93919e5642c3)
  - tests/test_sec_form4_capture.py (c156bc490419a507c534c46482ab4dab58c8d3c0)
  - four historical handoff SEC_FORM4 artifacts projected at ef28be642bd7ff87c3b5645b161e49de0c793d15 (not fingerprint-critical themselves).
* prochaine action unique: inspect exact-head CI for 99358df8; keep every phase-2 finding OPEN until its discriminating test and full suite are green. Only then continue lifecycle/PIT/evidence-binding falsification.
* commandes exactes nécessaires pour reproduire/reprendre:
  git clone --branch astra/p0-deep-adversarial-pre-t0 https://github.com/fahimahmedb/Quant-Trade.git
  cd Quant-Trade
  git diff 14aacccc34e394770a6c344b0101be665d7438c2..ef28be642bd7ff87c3b5645b161e49de0c793d15
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0 -v
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  python3 scripts/status_artifacts.py --check
  python3 scripts/verify_p0.py --check
  git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD

No merge, no Blue review request, no t0 declaration, no 14-day claim. The code now contains candidate fixes for every phase-2 defect durably reproduced in run 35448899020; CLOSED requires green evidence on the corrected exact tree.


Regression checkpoint after run 35449542201:
- Snapshot deletion of renderer-required keys caused KeyError; corrected by preserving opaque string values and withholding all shared EventLog rows/counts in SEC mode.
- Direct audit fixtures lacked request-intent timestamps; corrected fixtures, not validator.
- Orphan request intent now emits both REQUEST_INTENT_WITHOUT_ATTEMPT and generic REQUEST_ACCOUNTING_INCOMPLETE.
- Permanent-4xx cooldown made the second scenario in a two-scenario reconciliation test legitimately suppressed; fixture now advances past cooldown.
- Materialization diagnostics now compare semantic manifest/fingerprint before top-level commit/version metadata, while wrong-commit materialization remains rejected.
No phase-2 defect is CLOSED yet.
