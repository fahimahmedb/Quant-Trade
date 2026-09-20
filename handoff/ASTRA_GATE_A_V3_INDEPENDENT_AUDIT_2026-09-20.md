# ASTRA INDEPENDENT AUDIT — P0 / GATE A V3 — 2026-09-20

## 0. Role and scope

Classification: **FRONTIER-WORTHY**.

This is the independent, adversarial repository-side audit of the frozen
Gate A v3 candidate, performed as a red-team review of Builder's
implementation and Blue's reception, not a confirmation of either.

Exact frozen candidate: `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`
Candidate branch: `blue/p0-gate-a-v3-frozen-2026-09-20` (verified identical)
Builder branch head: `builder/p0-gate-a-v3-2026-09-20` (verified identical)
Audit branch / final Astra HEAD: `astra/p0-gate-a-v3-independent-audit-2026-09-20`
Frozen rejected v2 baseline: `db166fd04c681e67a2c6d4440828af14ef58c48c`
Canonical v2 independent audit: `64b105f5a2cc1d798d1cf1e41e715b967c845a85`

The candidate's own production code (`src/quant/**`, `scripts/quant.py`) was
**not modified** by this audit. All new material is audit-only, added on the
dedicated Astra branch across two commits: the first adding
`tests/test_astra_gate_a_v3_audit.py`, this checkpoint, and this handoff; a
second, packaging-only correction commit regenerating committed status
artifacts to the correct discovered-test count and fixing this section's
commit-count wording, after the first commit's own exact-head CI failed
solely at the `Status artifact freshness` step (see Section 1a).

## 1. Ancestry and CI verification (independently re-derived)

**FACT** — `git rev-parse` on `origin/astra/p0-gate-a-v3-independent-audit-2026-09-20`
(pre-audit), `origin/blue/p0-gate-a-v3-frozen-2026-09-20`, and
`origin/builder/p0-gate-a-v3-2026-09-20` all resolved to the identical SHA
`2da079d8ad75c69eb3fc2990c512735cb4bdc02b` before any audit work began.

**FACT** — `git diff --stat b278e4c5403adcc92d2c065f2d305365e48ec6f0 2da079d8ad75c69eb3fc2990c512735cb4bdc02b`
touches exactly two files
(`handoff/BUILDER_GATE_A_V3_2026-09-20.md` added,
`handoff/BUILDER_GATE_A_V3_CHECKPOINT_2026-09-20.md` modified). The
documentation-only-delta claim is independently confirmed, not merely
repeated from Blue's reception note.

**FACT** — queried via the GitHub Actions API directly (not taken from any
handoff document): run `35513010411` has `head_sha =
b278e4c5403adcc92d2c065f2d305365e48ec6f0`, `status = completed`,
`conclusion = success`. Run `35514180655` has `head_sha =
2da079d8ad75c69eb3fc2990c512735cb4bdc02b`, `status = completed`,
`conclusion = success`. Both bindings are exact-head, independently verified.

**FACT** — `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` at the
frozen candidate is byte-identical to its copy at
`astra/p0-deep-adversarial-pre-t0@643deacdf5bbbdb1d2410c762eb20f72aff16bbf`.

**INFERENCE** — green CI on both SHAs is execution evidence only (the CI
workflow was read in full: it runs the full unit suite, the SEC P0 lane
suite, a V1 end-to-end regression, and generates/verifies an exact-head
artifact, with no network access and a deliberate fail-closed check with no
SEC identity configured). It is not scientific certification, runtime
continuity proof, P14D proof, economic readiness, or capital authorization,
consistent with Section 0 of this mission.

### 1a. Astra's own first audit commit had a red exact-head CI

**FACT** — the first audit commit on this branch (adding
`tests/test_astra_gate_a_v3_audit.py`, the checkpoint, and this handoff)
produced GitHub Actions run `35516760209`, `head_sha =
b55e4c460a561eee93cfa797c373b6315f4f5473`, `status = completed`,
`conclusion = failure`. Independently queried job steps show the failure is
isolated to step 7, `Status artifact freshness`; steps 1–6 (checkout,
setup, environment record, fail-closed check, generated-schema drift) all
succeeded, and steps 8–14 (full unit suite, SEC P0 lane suite, V1 end-to-end
regression, verification-artifact generation/upload, placeholder restore,
clean-tree check) were `skipped` as a consequence of the earlier failure,
not independently red.

**FACT** — the root cause was independently reproduced: adding
`tests/test_astra_gate_a_v3_audit.py` (5 test methods) raised the
repository's discoverable-test count from 411 to 416
(`unittest.TestLoader().discover("tests").countTestCases() == 416`), but
`STATE.md`'s committed generated status block still read "411 unit tests
discovered", which is exactly the drift `scripts/status_artifacts.py --check`
exists to catch.

**Classification: TEST_DEFECT / AUDIT_PACKAGING_DEFECT, not REAL_DEFECT.**
This is a packaging omission in Astra's own first audit commit (a generated
artifact not regenerated after adding tests), not a regression in the frozen
candidate `2da079d8ad75c69eb3fc2990c512735cb4bdc02b` or in any of the seven
correction surfaces. The candidate's own exact-head CI (`35514180655`,
Section 1) remains green and is unaffected by this commit.

**Correction applied, packaging-only, no `src/quant/**` or
`scripts/quant.py` change**: ran `python3 scripts/status_artifacts.py
--write` (the canonical generator, not a hand-edit) to regenerate `STATE.md`
from the same reconstructed canonical V1 snapshot the CI check uses; the
resulting diff is exactly the one generated line
(`411 unit tests discovered` → `416 unit tests discovered`).
`python3 scripts/status_artifacts.py --check` and
`python3 scripts/generate_schemas.py --check` both pass locally afterward.
This correction, plus the Section 0 commit-count wording fix, is the second
commit on this branch.

## 2. Method

Before drawing any conclusion, this audit:

1. Read `QUANT_NORTH_STAR.md`, Blue's reception handoff, Builder's final
   handoff, the canonical v2 independent audit, the P0 qualifying deployment
   contract, and the Gate A evidence index — all from repository state, not
   chat summaries.
2. Read the full production source of `audit.py`, `scheduler.py`,
   `supervisor.py`, `budget.py`, `fingerprint.py`, and the relevant sections
   of `collector.py` (construction, qualifying-authority claiming,
   `poll`/`drain`/`reconcile`/`materialize_fingerprint`/
   `record_service_start`, `_validate_external_lifecycle_authority`,
   `_terminal_supervisor_stopped`) — not summaries of them.
3. Ran `tests.test_gate_a_v3_red` directly against the frozen candidate
   (15/15 pass) and read every test body in full to confirm each still
   invokes the raw public primitive named in its own docstring/test name,
   independent of Blue's anti-redirection claim.
4. Independently reproduced B2 across three sub-scenarios beyond the single
   canonical regression test (corrupted authority tail, missing deployment-
   authority consumption, forged automatic-restart without a genuine
   witness), committed as `tests/test_astra_gate_a_v3_audit.py`.
5. Attacked new boundaries not covered by any existing test: mutation
   ordering before/after `record_service_start()`, a disabled lane's
   `poll()`, the acquisition-critical fingerprint's binding (or lack of it)
   to service-managed/invocation-id markers, and analytic boundary review of
   every `>=`/`>`/`<` comparison in the obligation-resolution, supersession,
   and window-slicing logic.

## 3. Regression verdicts (replayed independently)

`B1_DIRECT_RECONCILE = CLOSED`

**FACT** — `collector.reconcile(day)`'s first substantive statement is
`due_day = self.reconciliation_due(); if due_day != day: return
{"result_state": "RECONCILIATION_NOT_DUE", "reconciled": False}` — before
`_guard_public_mutation` even runs and before any request is issued. This is
enforced at the lowest public mutation boundary, not in a wrapper.
`test_direct_reconcile_before_settlement_emits_no_request` calls this
primitive directly and passes.

`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED`

**FACT** — `_validate_external_lifecycle_authority()` derives `qualifying_claimed`
from durable lifecycle records (`OR`ed with the collector's own in-memory
claim), never from the identity of the process invoking the audit. The
canonical regression (`tests/test_astra_pre_t0.py::
test_offline_auditor_cannot_skip_qualifying_external_authority`) remains
present and unmodified in its essential assertion. Astra additionally
reproduced, independently, with the auditing collector's own
`qualifying_service_mode` forced to `False` to simulate an offline auditor
process in every case:
- a corrupted (not merely deleted) `CHILD_LAUNCH_AUTHORIZED` tail record →
  `LIFECYCLE_EXTERNAL_AUTHORITY_MISMATCH`, not accountable;
- a deleted `deployment_authorities.jsonl` → `DEPLOYMENT_AUTHORITY_CONSUMPTION_MISSING`,
  not accountable;
- a forged `AUTOMATIC_RESTART_AFTER_FAILURE` claim with no genuine witnessed
  child exit → `AUTOMATIC_RESTART_WITNESS_MISSING`, not accountable.

All three fail closed regardless of the auditing process's own claimed
identity. B2 is independently re-verified, not merely re-asserted from the
v2 canonical audit or from Blue's reception note.

`B3_MANUAL_OPERATOR_INTERVENTION = CLOSED`

**FACT** — `collector.poll()`, `collector.drain()`, and `collector.reconcile()`
each call `_guard_public_mutation(...)` at their own top, which records a
durable, window-invalidating operator-intervention row whenever
`_qualifying_history_exists()` is true and the calling process cannot prove
`_current_process_is_qualifying()` (which itself requires a claimed,
durably-matched, single-use `CHILD_LAUNCH_AUTHORIZED` binding via
`record_service_start()`). `test_direct_poll_from_unattested_process_...`
and `test_direct_drain_from_unattested_process_...` reproduce this directly
and pass. `materialize_fingerprint()` and `SecTrafficBudget.clear_cooldown()`
(via `save()` → `_authorize_mutation`) converge on the same
provenance-or-reject boundary; both direct-primitive discriminants pass.

## 4. D1–D5 (replayed independently)

All five were re-run directly (not only via CI) against the frozen
candidate and pass with the exact discriminant named in the Gate A evidence
index:

- **D1** (`test_omitted_due_daily_reconciliation_cannot_audit_accountable`):
  44 virtual hours of healthy 60-second discovery polling with reconciliation
  deliberately omitted; `reconciliation_due()` correctly returns the due day
  and the window is not accountable. `_ensure_reconciliation_obligation()` is
  independently invoked from `poll()`, `record_service_start()`, and
  `record_current_state()`, so a Clock that stops dispatching reconciliation
  cannot hide the obligation.
- **D2** (`test_reconcile_attempt_cannot_retire_discovery_poll_obligation`):
  `_resolve_attempts()` requires `attempt.attempt_kind == obligation.required_action_kind`;
  a `RECONCILE` attempt against a `DISCOVERY`-required obligation leaves it
  `UNEXPLAINED`.
- **D3** (`test_missing_referenced_raw_object_fails_verification_and_audit`):
  `store.verify_objects()` walks durable references (manifest, attempts,
  envelopes, source versions, coverage, reconciliation evidence) and flags a
  missing referenced object; the audit turns this into
  `RAW_OBJECT_REFERENTIAL_INTEGRITY_FAILED`.
- **D4** (both variants — with and without `supervisor_state.json`):
  `_terminal_supervisor_stopped()` treats a durable `CHILD_EXIT_OBSERVED` for
  the current qualifying child (with no later matching launch) as sufficient
  terminal evidence on its own, independent of whether
  `supervisor_state.json` exists.
- **D5** (`test_t0_between_ticks_preserves_pre_t0_baseline_lifecycle`): the
  pre-window `baseline_lifecycle` row is inserted into both
  `_validate_structure`'s and `_validate_external_lifecycle_authority`'s
  input lists when `window_start` falls between ticks, so
  `LIFECYCLE_PROVENANCE_MISSING` is not raised on a genuinely running
  qualifying service.

Boundary review (analytic, not just the shipped test cases): `_resolve_attempts`
accepts `offset ∈ [0, tolerance]` (both ends inclusive, forward-only);
`_resolve_supersessions` requires the superseding transition strictly
*before* the due time (`>= due` is rejected, not just `> due`); window-start
filtering includes a record with `recorded_at_utc == window_start` (`>=`);
`_mark_pending`'s zero-grace rule for `RECONCILE` obligations means an
obligation exactly at its due instant is immediately `UNEXPLAINED` rather
than `PENDING` if unresolved — a conservative (fail-closed), not permissive,
choice. No equality-boundary reviewed produces a permissive gap.

## 5. S7 verdicts (replayed independently)

`S7_FINGERPRINT = CLOSED` for the direct-primitive attack: deleting and
rematerializing the freeze file via `materialize_fingerprint()` after
qualifying history exists is durably provenance-bearing
(`test_direct_fingerprint_rematerialization_is_not_silent` passes).

`S7_BUDGET = CLOSED` for every primitive named in the mission brief: direct
`clear_cooldown()`, a fresh `SecTrafficBudget` instance over qualifying
durable state, an arbitrary/no-op `bind_mutation_authority` callback, and
`record_service_start()` without a valid unclaimed durable launch all either
reject or provenance the mutation. All four corresponding discriminants
pass. Duplicate claims of the same `CHILD_LAUNCH_AUTHORIZED` identity are
rejected (`test_forged_collector_cannot_reclaim_already_bound_external_launch`).

## 6. New findings

No new **REAL_DEFECT** was found. Two properties were newly probed, found
narrow, and are recorded as committed audit evidence
(`tests/test_astra_gate_a_v3_audit.py`) rather than promoted to blockers:

**NON_ISSUE (for Gate A's specific claim), but a genuine design observation**
— `collector.poll()` (and by inspection, `drain()`/`reconcile()`) do not
check `state.enabled` at all. A disabled lane's `poll()` still performs a
live discovery request if called directly; `sec-disable` does not itself
stop the primitive from running. This is not a Gate A false pass: any window
containing a `DISABLED` transition is unconditionally non-accountable via
`ACQUISITION_DISABLED_DURING_WINDOW`, so the retrospective audit still
correctly reports `accountable=False`. Recorded because it means "disable"
is enforced at the audit/window level, not by primitive refusal — worth
Blue's attention for the SEC fair-access/firewall commitment even though it
does not affect the Gate A continuity claim.

**MISSING_PROOF** — `acquisition_critical_fingerprint` does not bind
`service_managed`/`invocation_id` (only `qualifying_mode`,
poll/max-waits/restart/unit-digest, via `effective_service_configuration()`).
A process that forges `QUANT_SEC_QUALIFYING_MODE=1` plus matching
poll-interval and unit-digest environment variables — without ever being
launched by a recognised service manager — can obtain the **same**
acquisition-critical fingerprint as the real qualifying collector, even
though its own `lifecycle_provenance()` correctly computes
`qualifying_service_mode=False`. This narrows the evidentiary value of
`ACQUISITION_FINGERPRINT_CHANGED`/`ACTIVE_FINGERPRINT_DIFFERS_FROM_JOURNAL`
as an independent signal distinguishing an unattested process from the real
one. Astra reproduced the fingerprint collision as a verified **FACT**, but
could **not** construct an end-to-end scenario where it alone produces
`accountable=True`: in the reproduction attempted, the rogue collector's own
scheduler activity collided with the real collector's obligation chain
(`OBLIGATION_SUPERSEDED_MORE_THAN_ONCE`), and the window still failed
closed. This is left as **MISSING_PROOF** rather than **REAL_DEFECT**: the
blind spot is real, but Astra did not find (and did not exhaustively search
for) an ordering that turns it into a false pass. A falsifier for this item:
a reproduction, on a brand-new durable state directory, where the forged
process's activity precedes the very first legitimate
`record_service_start()` without colliding on obligation identity, and the
resulting window still reports `accountable=True`.

No test defect was found in the existing `tests/test_gate_a_v3_red.py`
suite: every discriminant reviewed still exercises the primitive named in
its own docstring, matching the anti-redirection ledger in
`governance/P0_GATE_A_EVIDENCE_INDEX_2026-09-20.md`.

## 7. TARGET_HOST_ONLY items (unchanged from v2, not repaired by this candidate and not expected to be)

Filesystem permission/immutability of the durable evidence volume, actual
systemd stop/start and SIGKILL behavior, mount persistence across reboot,
runtime image identity, and the final rodage artifact remain target-host
evidence outside repository scope. Both new observations in Section 6 above
implicitly assume an attacker without direct filesystem write access to the
durable `var` evidence volume; an attacker with such access could
additionally tamper with JSONL evidence rows directly (a threat model shared
with, and no narrower than, the one D3 already addressed for raw objects —
Astra did not find a *narrower*, JSONL-specific gap beyond what direct file
tampering already implies for every durable-evidence check in this system).
Locking down that access is the qualifying deployment contract's job, not
this repository's.

## 8. Required verdict

`AUDIT_GATE_A_V3 = PASS`

`B1_DIRECT_RECONCILE = CLOSED`
`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED`
`B3_MANUAL_OPERATOR_INTERVENTION = CLOSED`
`D1 = CLOSED`
`D2 = CLOSED`
`D3 = CLOSED`
`D4 = CLOSED`
`D5 = CLOSED`
`S7_FINGERPRINT = CLOSED`
`S7_BUDGET = CLOSED`

This PASS is a repository-proof-layer verdict only. It certifies that the
frozen candidate's retrospective audit, scheduler, budget, and lifecycle
mechanisms correctly fail closed against every historical regression this
mission required Astra to replay, plus the additional B2 sub-cases and new
boundary probes Astra constructed independently. It does **not** certify
scientific validity beyond this proof model, target-host continuity, P14D
continuity, economic readiness, or capital authorization.

## 9. What would change this verdict

- A reproduction (with test) showing the fingerprint-blind-spot MISSING_PROOF
  item above actually reaches `accountable=True` end-to-end.
- Any discovery that a currently-passing discriminant in
  `tests/test_gate_a_v3_red.py` has been silently redirected to a safer
  wrapper in some future commit (this audit found none at
  `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`).
- Target-host evidence contradicting an assumption this proof model depends
  on (e.g., the durable evidence volume is not actually write-protected from
  unauthorized processes, making the Section 7 caveat load-bearing rather
  than theoretical).
- A successor candidate that touches any of the seven correction surfaces
  without an accompanying independent re-replay of the discriminant it
  affects.

A green test count alone would not have been sufficient evidence for this
verdict; this audit is based on independently re-run tests plus direct
reading of the mechanism, plus new adversarial probes beyond the shipped
suite.

## 10. Safety state (unchanged — Astra does not declare any of these)

`t0 = NOT DECLARED`
`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`
`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`
`REAL_CAPITAL_AUTHORIZED = FALSE`
`PRODUCT_INTEGRATION = PAUSED`

## 11. Handoff

Next owner: **Blue / Mission Control**.

Astra's role ends here. This document does not authorize t0, Gate B,
target-host rodage, Product integration, or any capital action. Blue should
independently confirm this verdict before any further Gate disposition, and
should decide whether the two Section 6 observations (disabled-lane poll
enforcement point; fingerprint blind spot on service-managed markers)
warrant a future correction surface, given that neither was found to reopen
Gate A on the evidence available to this audit.
