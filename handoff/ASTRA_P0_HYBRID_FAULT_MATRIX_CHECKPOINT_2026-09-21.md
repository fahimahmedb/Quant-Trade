# ASTRA — P0 HYBRID FAULT MATRIX INDEPENDENT REVIEW — CHECKPOINT — 2026-09-21

Role: independent Astra / Red Team reviewer.

Mission branch:
`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`

Mission start HEAD verified:
`2f6c134f1202c6e22943638379be4e3435ecded0`

Frozen production candidate:
`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Codex delivery:
`686f77a383fb0e8c7ecd1b4a737585bedb544701`

Codex final checkpoint:
`e5c4c720e758cd8ab3f0e04faf541b26e204be16`

Independent evidence HEAD before this checkpoint:
`e774374861a9e2a20cdf6342a2fe1765770fe608`

## 1. F1 lineage and scope

Verified independently:

- merge-base(`d4d446c412258b2a9e4792cdcd9e2442ef24b615`,
  `686f77a383fb0e8c7ecd1b4a737585bedb544701`) is exactly the predecessor;
- Codex delivery is exactly one commit ahead of predecessor;
- Codex final checkpoint is exactly one documentation-only commit ahead of delivery;
- Astra mission was created exactly one mission-only commit ahead of the Codex final checkpoint;
- Codex mission paths are exactly:
  - `tools/p0_qualification/gate_a/fault_matrix.py`;
  - `tools/p0_qualification/evidence/gate_a/fault_matrix.json`;
  - `handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md`;
- no existing `src/`, `deploy/`, `scripts/`, `tests/`, production workflow,
  timing/calendar/long-history harness path was modified by the Codex mission.

`PRODUCTION_CODE_CHANGED = FALSE`.

## 2. F2/F3 row and existing-proof review

The matrix contains exactly the 19 required properties, with no duplicate or renamed-away requirement.

Independent CI resolved and executed all 18 unique cited test methods:

`18 tests / 18 PASS / 0 failures / 0 errors`.

Astra inspected the cited test bodies rather than accepting names. The 15
`EXISTING_DISCRIMINATING_PROOF` rows target the stated repository properties.
In particular:

- raw-write failure checks no raw object, staging residue or envelope;
- post-link directory-fsync failure leaves a visible object but retry must
  revalidate both directory levels before acknowledgement;
- envelope/crash replay checks both pre-envelope replay and post-envelope
  no-refetch/no-duplicate behavior;
- cursor crash boundary proves no skip and only advances after acknowledgements;
- request INTENT without FINISHED fails retrospective accounting;
- missing successor obligation makes the window non-accountable;
- cooldown persists across a fresh budget instance and cannot be shortened;
- supervisor SIGKILL + pending-obligation evidence remains non-accountable;
- child restart requires same-supervisor external failure witness;
- SEC torn/corrupt JSONL evidence fails closed through the production
  `read_jsonl` primitive;
- missing/foreign fingerprint and missing deployment authority all fail closed.

No stale or wrong-target citation requiring `MISSING_PROOF` was found.

## 3. F4/F5/F10 new discriminants

Current candidate:

- file-fsync discriminant = GREEN;
- state-newer-than-journal discriminant = GREEN;
- journal-newer-than-state discriminant = GREEN.

Independent temporary mutations:

- remove the regular-file fsync boundary:
  Codex discriminant turns RED
  (`regular_fsync_seen=False storage_failure=False target_exists=True`);
- make the real collector loader accept state/journal mismatch:
  both divergence discriminants turn RED.

These three new discriminants demonstrate the required sensitivity.

## 4. F6/F10 restart_burst_limit

Current repository fact:

- production constant = `5`;
- frozen unit declares `StartLimitBurst=5`;
- an independently constructed static `systemctl show` fixture with loaded value
  `5` is accepted by the real `_effective_systemd_definition` path;
- loaded value `4` is rejected by that same real path.

Repository binding of the current value is therefore independently closed.

However, the Codex helper
`_restart_burst_limit_discriminant` derives its expected "good" loaded value
from `launcher.RESTART_BURST_LIMIT` itself. Astra temporarily mutated only that
isolated constant from `5` to `4`. The Codex discriminant remained GREEN:

`constant=4 exact_loaded_value_accepted=True one_below_rejected=True`.

Classification:

`TEST_DEFECT / NON_BLOCKING_WITH_INDEPENDENT_ASTRA_COMPENSATION`.

This is not a production REAL_DEFECT. It means the Codex discriminant is
self-referential with respect to the frozen numeric contract and would not
automatically catch a source-constant drift. Astra's independent 5-vs-4 check
closes the current repository property without altering production.

Physical service-manager restart behavior remains `TARGET_HOST_ONLY`.

## 5. F8 reproducibility

Two independent generations in the same CI interpreter were byte-identical:

- Python: `3.12.14`;
- report digest #1:
  `sha256:8d86c8b8e65ec4f5c353481d134f8b45630cdd3754ec20e53bdd5a0551315cc6`;
- report digest #2:
  `sha256:8d86c8b8e65ec4f5c353481d134f8b45630cdd3754ec20e53bdd5a0551315cc6`.

The committed artifact was generated under Python `3.12.3` and embeds:

`sha256:bc7682fe22450ad63a84df1ac8443107056c4949dc07e58ff5335e260e832d73`.

Regeneration under Python `3.12.14` had the same non-environment payload but a
different `python_version`, therefore a different report digest.

Classification:

`TEST_DEFECT / NON_BLOCKING_ENVIRONMENT_BOUND_DIGEST`.

The artifact is deterministic for a fixed interpreter build, but the Builder
claim of an unqualified reproducible file digest is too broad. The environment
metadata is explicit rather than silent; no acquisition property is affected.

## 6. F9 artifact self-consistency and SHA binding

Verified:

- 19 rows;
- proof-class recount = 15 existing / 4 new / 0 target-host-only rows / 0 missing;
- defect recount = 19 NON_ISSUE in the Codex artifact;
- embedded report digest recomputes exactly;
- every row and top-level exact-SHA field names the frozen candidate
  `4d06bdbf...`;
- no t0, P14D amendment, target-host readiness or capital authority is claimed.

One evidence-structure limitation was found: the named
`harness_input_tree_digest` omits the production files directly exercised by
the new discriminants:

- `src/quant/dataplane/sec/store.py`;
- `src/quant/dataplane/sec/collector.py`;
- `deploy/quant_sec_supervisor.py`;
- `deploy/quant-sec-capture.service`.

Classification:

`TEST_DEFECT / NON_BLOCKING`.

Compensating evidence is independent exact Git ancestry plus the verified
no-production-delta scope from the frozen candidate through predecessor and
Codex delivery. No proof is silently transferred across a production SHA.

## 7. F7 repository vs TARGET_HOST_ONLY boundary

Astra actively attempted to force missing proof through the new discriminants.

Current result:

- `REAL_DEFECT = 0`;
- unresolved repository `MISSING_PROOF = 0` after independent compensation;
- `TARGET_HOST_ONLY` residuals remain real:
  physical power-loss/filesystem durability, actual effective systemd behavior,
  restart-storm enforcement, reboot/runtime-image/mount/state-root semantics.

Those are residual proof domains, not repository fault-matrix rows that must be
reclassified wholly as `TARGET_HOST_ONLY`.

## 8. Independent CI evidence

Workflow:
`Astra P0 hybrid fault-matrix independent review`

Run:
`35547273728 = COMPLETED / SUCCESS`

Exact evidence HEAD:
`e774374861a9e2a20cdf6342a2fe1765770fe608`

Artifact:
`astra-p0-hybrid-fault-matrix-independent-e774374861a9e2a20cdf6342a2fe1765770fe608`

Artifact id:
`10617375189`

Uploaded artifact ZIP digest:
`sha256:6193894684085077717e6c2b92932259d6883feb58da531a0b77b4dfcc1f53bc`

The ordinary SEC P0 pre-t0 gate on the same evidence HEAD is run
`35547273657`; it was still IN_PROGRESS when this checkpoint was authored.

## 9. Provisional disposition

No production REAL_DEFECT has been reproduced.

The three material findings so far are all `TEST_DEFECT` and are either
independently compensated for the current repository property or explicitly
bounded metadata/evidence-structure limitations.

Provisional disposition pending final handoff and final exact-head CI:

`ASTRA_FAULT_MATRIX = PASS_REPOSITORY_EVIDENCE`

This does not declare target-host readiness, P14D amendment, Gate B, t0,
Product integration, scientific/economic readiness, or real-capital authority.
