CHECKPOINT ASTRA P0

* timestamp UTC: 2026-09-19T18:44:00Z
* branch: astra/p0-deep-adversarial-pre-t0
* exact HEAD SHA: c2edb2993b1ab044bbd9bc3cd80be6c7fd1b66f1 (phase-3 red head; this checkpoint is a subsequent documentation-only commit)
* parent/base SHA: parent 1e11b221b69a33e9b303865724a648416194d49f; phase-2 green code head 8a03aa2938fbb823ba250e2566f21030d889b2be; audit baseline 8d5dbb41559c4716e94d5290b6ae979a8b96143c; Blue c1a955316055aaf6c1b28853e21ed07e36e55f6a
* t0 status: NOT DECLARED
* P0_CONTINUOUS_SERVICE_STATE: OPEN / NOT_YET_PROVEN_CONTINUOUS
* defects CONFIRMED OPEN:
  - FORGED_CHILD_LIFECYCLE_ENV_BUYS_QUALIFYING_READINESS — BLOCKS_CAPTURE_INTEGRITY. A child constructed with service-manager/cause/boot/supervisor/nonce environment markers but no durable external launch authority reaches instrumentation_ready=true after one valid acquisition cycle.
  - FUTURE_LAST_POLL_SUPPRESSES_DUE_ACQUISITION — BLOCKS_CAPTURE_INTEGRITY. A future last_poll_started_at_utc makes poll_due() false, allowing backward-clock/future-state skew to suppress discovery.
  - VERIFICATION_DIGEST_OMITS_SYSTEMD_UNIT — BLOCKS_CAPTURE_INTEGRITY. Mutating deploy/quant-sec-capture.service leaves scripts/verify_p0.py verified_tree_digest unchanged although the unit is acquisition-critical.
* defects CONFIRMED CLOSED: all phase-1 and phase-2 defects recorded in the prior checkpoint remain closed; no phase-3 finding is closed yet.
* hypotheses NOT YET REPRODUCED: audit window not explicitly bound to future Blue t0; truncated task-id collision; supervisor signal/abrupt-death matrix; target-host effective loaded unit; deeper PIT/request-budget crash matrix; concurrent/interrupted materialization; additional indirect firewall leaks; exact final evidence binding/rodage.
* tests rouges ajoutés: Phase3AuthorityAndBindingCampaign in tests/test_astra_pre_t0.py at 1e11b221b69a33e9b303865724a648416194d49f; canonical STATE inventory restored at c2edb2993b1ab044bbd9bc3cd80be6c7fd1b66f1.
* tests verts obtenus: phase-1/phase-2 green remains established at run 35449811049 on 8a03aa2938fbb823ba250e2566f21030d889b2be. No phase-3 green claim.
* full-suite status: FAIL on exact head c2edb2993b1ab044bbd9bc3cd80be6c7fd1b66f1: GitHub Actions run 35461894468, 350 tests, exactly 3 failures, one for each phase-3 discriminant.
* CI run id/status: 35461894468 / FAILURE (discriminating red execution reached full suite; status/schema pre-gates passed).
* active fingerprint: NOT MEASURED IN ACTUAL SERVICE RUNTIME
* materialized fingerprint: NOT AVAILABLE
* manifest schema/version: p0_materialized_fingerprint/v2; acquisition_critical_fingerprint/v1; final freeze not performed
* rodage status + exact artifact: NOT RUN on current code; historical rodage artifacts have no current proof authority
* readiness status: NOT ESTABLISHED; current code has a confirmed readiness false-positive under forged lifecycle environment
* audit status: phase-3 INCOMPLETE; three confirmed blockers open
* firewall status: phase-2 public-surface tests green; broader final firewall audit still required
* fichiers acquisition-critical modifiés: none in phase-3 red commit; only tests/test_astra_pre_t0.py was added to and STATE.md returned to its canonical generated inventory
* prochaine action unique: correct the three confirmed phase-3 defects with the existing red tests unchanged, then obtain exact-head full-suite green before opening further falsification scenarios
* commandes exactes nécessaires pour reproduire/reprendre:
  git clone --branch astra/p0-deep-adversarial-pre-t0 https://github.com/fahimahmedb/Quant-Trade.git
  cd Quant-Trade
  git checkout c2edb2993b1ab044bbd9bc3cd80be6c7fd1b66f1
  PYTHONPATH=src python3 -m unittest tests.test_astra_pre_t0.Phase3AuthorityAndBindingCampaign -v
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  git diff 8d5dbb41559c4716e94d5290b6ae979a8b96143c..HEAD

Red evidence: run 35461894468 shows FORGED_CHILD_LIFECYCLE_ENV... readiness=True, FUTURE_LAST_POLL... poll_due=False, and identical verification digests before/after systemd-unit mutation. No new branch, no merge, no Blue review request, no t0 declaration, no 14-day claim.
