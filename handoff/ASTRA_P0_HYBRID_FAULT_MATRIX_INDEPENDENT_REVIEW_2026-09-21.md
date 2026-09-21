# ASTRA — P0 HYBRID FAULT MATRIX INDEPENDENT REVIEW — FINAL HANDOFF — 2026-09-21

Role: independent Astra / Red Team reviewer.

Decision authority after this handoff returns to Blue / Mission Control.

## 0. Final repository verdict

`ASTRA_FAULT_MATRIX = PASS_REPOSITORY_EVIDENCE`

This is a bounded repository-evidence verdict for the Gate-A hybrid fault matrix.
It is not a Gate B authorization, target-host entrance result, t0 declaration,
P14D amendment, Product-integration decision, scientific/economic readiness
claim, or real-capital authorization.

## 1. Exact objects under review

Mission branch:
`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`

Mission start HEAD:
`2f6c134f1202c6e22943638379be4e3435ecded0`

Codex predecessor:
`d4d446c412258b2a9e4792cdcd9e2442ef24b615`

Codex delivery:
`686f77a383fb0e8c7ecd1b4a737585bedb544701`

Codex final checkpoint:
`e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Frozen production candidate:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Final audit-evidence parent HEAD before this handoff:
`398b76d2f739df7d7dd47ccda909a0b8ea2a7e85`

The commit containing this handoff cannot truthfully embed its own SHA.
Resolve the live head of
`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`
after this file is pushed. That resolved live SHA is the final Astra branch HEAD
and is reported to Blue together with its exact-head CI. This is the explicit
self-reference cut already used by this repository's durable governance.

## 2. Lineage and production immutability

Astra independently verified:

- merge-base(predecessor, Codex delivery) = predecessor exactly;
- Codex delivery is exactly one commit ahead of predecessor;
- Codex final checkpoint is exactly one docs-only commit ahead of delivery;
- Astra mission starts exactly from the Codex final checkpoint;
- Codex mission changed only:
  - `tools/p0_qualification/gate_a/fault_matrix.py`;
  - `tools/p0_qualification/evidence/gate_a/fault_matrix.json`;
  - `handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`;
- no production `src/`, `deploy/`, `scripts/`, existing test, production
  workflow, or completed timing/calendar/long-history path was changed.

The predecessor itself descends exactly from the frozen v4 candidate, with the
intervening changes confined to qualification harness/evidence/handoff paths.

`PRODUCTION_CODE_CHANGED = FALSE`

No production fix was made by Astra.

## 3. Required row set

Astra verified exactly the 19 required properties, in the required set, with no
duplicate or renamed-away row:

1. before_after_raw_write
2. before_after_file_fsync
3. before_after_hardlink_publication
4. before_after_directory_fsync
5. before_after_envelope_append
6. before_after_attempt_completion
7. before_after_cursor_advancement
8. before_after_successor_scheduler_obligation
9. before_after_cooldown_persistence
10. supervisor_death
11. child_death
12. corrupt_torn_journal_tail
13. duplicate_replay
14. state_newer_than_journal
15. journal_newer_than_state
16. missing_fingerprint
17. foreign_fingerprint
18. missing_deployment_authority
19. restart_burst_limit

Stored proof-class recount is internally consistent:

- `EXISTING_DISCRIMINATING_PROOF = 15`;
- `NEW_DISCRIMINATING_PROOF = 4`;
- `MISSING_PROOF = 0`;
- `TARGET_HOST_ONLY rows = 0`.

The last count means no row is wholly target-host-only. It does not erase the
explicit target-host residual domains recorded on the rows.

## 4. Review of all 15 existing proof rows

Astra inspected the cited test bodies, not merely the test names, and then
independently resolved and executed all 18 unique cited methods.

Execution result:

`18 tests / 18 PASS / 0 failures / 0 errors`

### before_after_raw_write

Citation:
`RawStoreTests.test_disk_full_during_raw_write_raises_instead_of_acknowledging`

The test injects ENOSPC into the real raw-write primitive, requires
`SecStorageFailure`, and checks zero raw objects, zero staging residue and zero
envelopes.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### before_after_hardlink_publication

Citation:
`RawPublicationDurabilityTests.test_retry_after_directory_fsync_failure_revalidates_durability`

The test forces failure after a hardlink is already visible, verifies the first
operation is not acknowledged, then requires retry to fsync both relevant
directory levels before deduplicated acceptance.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### before_after_directory_fsync

Citations include the retry test above plus
`test_new_hash_prefix_is_fsynced_in_its_parent`.

Both object-directory durability and creation of the hash-prefix entry in its
parent are asserted.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### before_after_envelope_append

The two crash-boundary tests cover both sides:

- raw bytes durable but no envelope => task remains replayable;
- durable envelope before acknowledgement/drop => restart deduplicates with
  zero refetch and no duplicate envelope.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### before_after_attempt_completion

An INTENT without a FINISHED attempt produces
`REQUEST_ACCOUNTING_INCOMPLETE` and makes the retrospective audit
non-accountable.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### before_after_cursor_advancement

A crash before cursor movement leaves the cursor unadvanced; replay does not
refetch already acknowledged evidence and only advances after all tasks are
acknowledged.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### before_after_successor_scheduler_obligation

An answered request without the successor scheduler commitment cannot yield an
accountable window; production audit logic explicitly emits
`SUCCESSOR_OBLIGATION_MISSING` when an enabled lane has no valid pending
successor.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### before_after_cooldown_persistence

A fresh budget instance observes the durable cooldown; a shorter new proposal
cannot shorten it and a longer proposal can extend it.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### supervisor_death

A real SIGKILL process-boundary test kills the child with the supervisor and
requires replacement to be manual. A separate audit test proves a stopped
supervisor with a pending obligation cannot remain accountable.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### child_death

The same live supervisor can record an automatic failure restart, while the
negative authority test requires an external prior child-exit witness from that
supervisor.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### corrupt_torn_journal_tail

The cited test writes a torn acquisition-critical SEC journal tail and requires
a loud failure. Astra additionally inspected the production
`quant.state.read_jsonl` / `append_jsonl` path: SEC evidence with a torn tail
is rejected rather than silently truncated or repaired; the audit wrapper turns
malformed evidence into an explicit failed verdict.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### duplicate_replay

The crash/replay tests prove content-addressed raw bytes are not duplicated and
a durable envelope prevents a second fetch or append.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### missing_fingerprint

Qualifying readiness blocks when no materialized fingerprint exists.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### foreign_fingerprint

A scheduler fingerprint differing from the active acquisition-critical
fingerprint makes the retrospective audit non-accountable.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

### missing_deployment_authority

Removing the consumed deployment-authority ledger produces
`DEPLOYMENT_AUTHORITY_CONSUMPTION_MISSING` and a non-accountable audit.

Classification:
`NON_ISSUE / EXISTING_DISCRIMINATING_PROOF`

No cited existing row required reclassification to `MISSING_PROOF`.

## 5. Four new discriminants and independent falsification

### A. before_after_file_fsync

Current discriminant:

`regular_fsync_seen=True storage_failure=True target_exists=False staging_entries=0`

Astra mutation:
the regular-file fsync was removed from the isolated publication path.

Observed Codex discriminant after mutation:

`regular_fsync_seen=False storage_failure=False target_exists=True staging_entries=0`

It turned RED.

Classification:
`NON_ISSUE / NEW_DISCRIMINATING_PROOF`

Physical crash/power-loss durability remains `TARGET_HOST_ONLY`.

### B. state_newer_than_journal

Current candidate fails closed with:

`COLLECTOR_STATE_UNCOMMITTED_OR_ROLLED_BACK`

Astra monkeypatched the real collector loader to tolerate exactly that
state/journal mismatch. The Codex discriminant then reported that collector
restart accepted divergent durable state and turned RED.

Classification:
`NON_ISSUE / NEW_DISCRIMINATING_PROOF`

Physical filesystem/crash ordering remains `TARGET_HOST_ONLY`.

### C. journal_newer_than_state

Current candidate fails closed with the same explicit storage error.

Under the same permissive-loader mutation, the discriminant turned RED.

Classification:
`NON_ISSUE / NEW_DISCRIMINATING_PROOF`

Physical filesystem/crash ordering remains `TARGET_HOST_ONLY`.

### D. restart_burst_limit

Current frozen repository fact was independently reconstructed without deriving
the expected good fixture from the production constant:

- `RESTART_BURST_LIMIT = 5`;
- frozen unit contains `StartLimitBurst=5`;
- loaded value `5` is accepted by the real
  `_effective_systemd_definition` path;
- loaded value `4` is rejected by that same real path.

Therefore the current repository property is proven.

However, Astra found a discriminant-quality defect in the Codex helper. The
helper derives its expected loaded value from
`launcher.RESTART_BURST_LIMIT`. Astra mutated only that isolated production
constant from `5` to `4`. The Codex discriminant remained GREEN:

`constant=4 exact_loaded_value_accepted=True one_below_rejected=True`

Classification of the production property:
`NON_ISSUE`

Classification of the Codex test:
`TEST_DEFECT / NON_BLOCKING_WITH_INDEPENDENT_ASTRA_COMPENSATION`

Reason:
the helper proves loaded-value consistency with whatever source constant exists,
but does not itself lock the frozen numeric contract to five. Astra's separate
static-5-vs-4 discriminant closes the current repository proof without modifying
production.

Physical service-manager enforcement of restart limits remains
`TARGET_HOST_ONLY`.

## 6. MISSING_PROOF challenge

Astra did not accept `MISSING_PROOF_COUNT = 0` from the artifact.

It attempted to force proof gaps through:

- all existing citations;
- file-fsync mutation;
- both state/journal divergence mutations;
- restart-burst constant mutation;
- exact candidate/SHA binding;
- artifact repeatability;
- input-tree binding;
- repository-vs-target-host boundary.

Result:

`REAL_DEFECT = 0`

`UNRESOLVED_REPOSITORY_MISSING_PROOF = 0`

The restart-burst Codex helper has a `TEST_DEFECT`, but the current numeric
contract is independently proven by Astra. Therefore it does not leave an
unresolved repository `MISSING_PROOF`.

## 7. Artifact reproducibility

Codex machine artifact:

`tools/p0_qualification/evidence/gate_a/fault_matrix.json`

Frozen candidate embedded:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Committed embedded report digest:

`sha256:bc7682fe22450ad63a84df1ac8443107056c4949dc07e58ff5335e260e832d73`

The embedded digest recomputes exactly from the committed payload.

Two independent Astra generations on the same CI interpreter were byte-identical
and produced the same report digest:

`sha256:8d86c8b8e65ec4f5c353481d134f8b45630cdd3754ec20e53bdd5a0551315cc6`

The final probe revision also records SHA-256 over the complete generated file
bytes for both generations and requires those hashes to be identical.

Astra also reproduced an environment-bound difference:

- committed artifact Python:
  `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`;
- audit runner Python:
  `3.12.14 (main, Aug 13 2026, 02:47:42) [GCC 13.3.0]`;
- non-environment payload: identical;
- report digest: changes because `python_version` is part of the hashed payload.

Classification:
`TEST_DEFECT / NON_BLOCKING_ENVIRONMENT_BOUND_DIGEST`

The artifact is deterministic for a fixed interpreter build. The unqualified
Builder wording "reproducible file digest" is too broad across Python builds,
but the environment difference is explicit metadata rather than hidden state and
does not alter the acquisition property conclusions.

## 8. Artifact binding limitation

The field named `harness_input_tree_digest` does not include four production
paths directly exercised by the new discriminants:

- `src/quant/dataplane/sec/store.py`;
- `src/quant/dataplane/sec/collector.py`;
- `deploy/quant_sec_supervisor.py`;
- `deploy/quant-sec-capture.service`.

Classification:
`TEST_DEFECT / NON_BLOCKING`

This digest alone is therefore not sufficient to prove production-byte binding.
The proof is independently closed by exact Git ancestry and the verified
absence of any production delta from the frozen candidate through the
qualification predecessor and Codex delivery.

No proof is silently transferred across a different production SHA.

## 9. Artifact self-consistency

Verified:

- exact row count = 19;
- no duplicate rows;
- stored proof-class counts equal a recount;
- stored non-issue count equals row classifications in the Codex artifact;
- top-level `exact_sha`, body `frozen_candidate_sha` and every row's
  `frozen_production_candidate_sha` all equal the exact frozen v4 candidate;
- embedded report digest recomputes exactly;
- no t0, target-host readiness, P14D amendment or capital authorization is
  claimed.

`MISSING_PROOF_COUNT = 0` is accepted as the current repository-evidence
conclusion after this independent review.

The statement `NEW_DISCRIMINATING_PROOF_COUNT = 4` requires the explicit
qualification that one Codex discriminant has the restart-constant oracle
`TEST_DEFECT`; Astra independently supplies the missing hard-coded 5-vs-4
sensitivity for the current candidate.

## 10. Classification summary

### REAL_DEFECT

None reproduced.

### TEST_DEFECT

1. `restart_burst_limit` Codex discriminant uses the production constant as
   its own expected-value oracle; a temporary 5 -> 4 mutation remains green.
   Non-blocking because Astra independently proves the current constant/unit
   contract is 5 and the real validation path rejects 4.

2. Artifact report/file digest is Python-build-bound because `sys.version` is
   inside the hashed payload. Same-build generation is deterministic; cross-build
   digest stability is not a valid unqualified claim.

3. `harness_input_tree_digest` omits exercised production paths. Non-blocking
   because exact Git ancestry/no-production-delta evidence independently binds
   the tested bytes to the frozen candidate.

### MISSING_PROOF

None unresolved repository-side after independent compensation.

### TARGET_HOST_ONLY

Still required outside this repository verdict:

- actual power-loss/crash durability of file data and directory metadata;
- deployed filesystem semantics;
- actual loaded systemd unit on the target host;
- physical service-manager restart-burst enforcement;
- runtime image/package/service-manager behavior;
- mount/state-root and reboot behavior;
- any other target-host entrance requirement already defined by governance.

### NON_ISSUE

The 19 current repository properties are not reproduced as production defects.
The three TEST_DEFECT findings above concern evidence/test machinery or claim
precision, not a current frozen-candidate production failure.

## 11. Independent execution evidence

Audit-only files added by Astra:

- `audit/astra_p0_hybrid_fault_matrix_independent_probe.py`;
- `.github/workflows/astra-p0-hybrid-fault-matrix-independent-review.yml`;
- `handoff/ASTRA_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`;
- this final handoff.

Completed independent run on evidence HEAD
`e774374861a9e2a20cdf6342a2fe1765770fe608`:

`35547273728 = COMPLETED / SUCCESS`

That run executed:

- exact lineage/scope assertions;
- all 18 cited tests;
- all four current new discriminants;
- independent exact-5 / reject-4 restart check;
- three successful red mutations;
- the restart 5 -> 4 oracle falsifier;
- two artifact generations;
- SHA/digest/self-consistency checks.

Uploaded independent evidence artifact:

`astra-p0-hybrid-fault-matrix-independent-e774374861a9e2a20cdf6342a2fe1765770fe608`

Artifact id:
`10617375189`

Artifact ZIP digest:
`sha256:6193894684085077717e6c2b92932259d6883feb58da531a0b77b4dfcc1f53bc`

The later audit-probe revision at
`398b76d2f739df7d7dd47ccda909a0b8ea2a7e85`
adds explicit full-file SHA-256 comparison for the two generated artifacts.

Final exact-head audit and ordinary SEC P0 CI runs are resolved after this
handoff push because their run IDs do not exist until the push itself. Astra
must observe those exact-head runs before returning control to Blue.

## 12. Safety boundary

This review does not authorize or declare:

- `TARGET_HOST_READY`;
- Gate B;
- t0;
- P14D hybrid amendment;
- Product integration;
- scientific/economic readiness;
- real capital.

Existing target-host-only entrance checks remain mandatory.

## 13. Final disposition

The Codex matrix has correct lineage and bounded scope.
All 19 required rows exist.
All 15 existing proof citations were inspected and executed.
The file-fsync and both state/journal discriminants demonstrate independent
mutation sensitivity.
The restart-burst repository property is correct and independently proven,
while the Codex helper's self-referential expected-value construction is
preserved as a non-blocking TEST_DEFECT.
The artifact is internally consistent and deterministic within a fixed Python
build, with the cross-build digest limitation explicitly classified.
No production path changed.
No repository REAL_DEFECT was reproduced.
No unresolved repository MISSING_PROOF remains.
Target-host residuals remain target-host residuals.

`ASTRA_FAULT_MATRIX = PASS_REPOSITORY_EVIDENCE`

After final exact-head CI is observed, Astra stops and returns control to Blue.
