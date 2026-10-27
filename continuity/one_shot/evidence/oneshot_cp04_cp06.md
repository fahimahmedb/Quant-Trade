# CP04 / CP06 retrospective audit

FACT: CP04 (d35629b56362cd4704032925e4d6415102c6d28a) added exactly one product module, `research/research_os/continuation.py`, one test, and evidence. `rg` finds no product imports; only `tests/test_verified_continuation_contract.py` imports it.

FACT: CP04 `validate_obligations` indexes all closures by lifetime `OBLIGATION_ID` (lines 81–94) and rejects more than one. Its `reopen_event` (110–128) preserves the original closure hash but carries no revision/current-resolution identity. An isolated in-memory probe at 40c590189e1389502d179e63f6e0925df8513d2c produced `MULTIPLE_DURABLE_CLOSURES:O-1` for BLOCK -> REOPEN -> CHILD_TASK when preserving history. Probe metadata: `/tmp/cp04_revision_probe.json`. This is a current product-contract defect against the new mission, not stale fixture or environmental failure.

FACT: W2 already owns actual continuity mutations. `ebc72b9:research/research_os/oracle_worker.py:210–252` atomically publishes stage output, immutable event and receipt with task transition and expected task blob; child creation is owned by `worker_stages.py:269–292` and authority-gated at `338–369`. `oracle_worker.py:266–296` rechecks snapshot HEAD and derivation before atomic refill. Generic revision-aware declared-obligation semantics are not proven equivalent, but this does not establish a requirement for forensic UST classification.

RECOMMENDATION: CP04 outcome C `SEPARATE_MISSION_REQUIRED`; explicitly revert its unused product module by new commit, retain historical evidence and executable historical tests. Do not port a new generic obligation model in this primary forensic mission. Reporting an action-specific authority block is possible without asserting a historical or current production obligation, creating a task, or mutating production history. No BLOCK/PARK schemas need migration.

FACT: CP06 (3be85e3314aa70d2fecfd1b145c3aaa9ab5df199) adds only `research/research_os/renewal_policy.py`, own test and evidence. It is imported only by `tests/test_verified_continuity_renewal.py`. Current policy is disabled. W2 already owns bounded queue refill and control constraints (`control_plane.py:84–103`; `oracle_worker.py:266–296`).

FACT: Frozen independent challenger `642b551:architecture-review/04_FRONTIER_RENEWAL_ANALYSIS.md` identifies renewal as a precise separate policy seam and explicitly says source-family labels, issuance counts and new cohorts cannot manufacture new science or exposure budget. It does not authorize integrating renewal into an unrelated witness. The Owner architecture delta `e97bb38:audit/owner-recovery/20261026/architecture-delta-01/DELTA_ARCHITECTURAL_MINIMAL.md` describes functional recommendations only and says existing owners should be reused. Both are evidence, not authority.

RECOMMENDATION: CP06 `KEEP_EVIDENCE_ONLY + REPLAY_TEST_ONLY + SEPARATE_MISSION_REQUIRED`, explicitly revert product module. Its technical merits do not justify its presence in a read-only UST forensic witness.

## Preserving tests without product resurrection

Retain the original test bytes as replay-only artifacts (outside ordinary current-product test discovery), and run them against an isolated `git archive 3be85e3314aa70d2fecfd1b145c3aaa9ab5df199` extraction, or keep replay runner using that immutable source tree. This tests historical claims without making those claims current qualification. Original CP06 test imports CP03 `idea_feed.primitives`; if CP03 is reverted, historical replay must preserve its historical tree dependencies. Do not leave broken top-level imports, silently skip, or treat a historical replay PASS as retained-product qualification.

## Follow-up acceptance

If revision-aware continuation becomes necessary: prove actual declared obligation first; use one canonical thin resolution record or native fields; preserve append-only per-revision history; exactly one current authoritative resolution per revision; test BLOCK/PARK -> REOPEN -> CHILD_TASK -> TERMINAL, duplicate resolution rejection, replay idempotency, stale revision rejection, and no authority uplift. If renewal becomes necessary: independently authorize bounded successor policy, retain all predecessor exposure and roots, preserve source/PIT and protected outcome boundaries, and qualify current native route without new scheduler ownership.
