# ASTRA GATE A V3 CHECKPOINT — 2026-09-20

Exact frozen candidate: `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`.

Audit HEAD before this checkpoint: `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`
(the Astra branch was initialized exactly at the frozen candidate; this
checkpoint is the first commit on top of it).

## Ancestry/CI verification (independent)

- `origin/astra/p0-gate-a-v3-independent-audit-2026-09-20` HEAD, merge-base
  with the candidate, `origin/blue/p0-gate-a-v3-frozen-2026-09-20`, and
  `origin/builder/p0-gate-a-v3-2026-09-20` HEAD all resolve to the exact same
  SHA `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`. FACT.
- Implementation candidate `b278e4c5403adcc92d2c065f2d305365e48ec6f0` exists;
  diff `b278e4c5..2da079d8` is exactly the two documentation files claimed
  (`handoff/BUILDER_GATE_A_V3_2026-09-20.md` added,
  `handoff/BUILDER_GATE_A_V3_CHECKPOINT_2026-09-20.md` modified). FACT.
- GitHub Actions run `35513010411` (head `b278e4c5...`) and run `35514180655`
  (head `2da079d8...`) independently queried via the Actions API: both
  `status=completed`, `conclusion=success`, `head_sha` matching exactly. FACT.
- `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` at the frozen
  candidate is byte-identical to the copy at
  `astra/p0-deep-adversarial-pre-t0@643deacdf5bbbdb1d2410c762eb20f72aff16bbf`.
  FACT.

## What was replayed

Ran `tests.test_gate_a_v3_red` directly (not via CI) at the frozen candidate:
15/15 pass, including every discriminant named in
`governance/P0_GATE_A_EVIDENCE_INDEX_2026-09-20.md` (B1, B3 poll/drain, B3
fingerprint, B3 cooldown, D1, D2, D3, D4 (both variants), D5, and the two
second-order forged-environment/duplicate-launch regressions). Test bodies
were read in full: each still calls the named public primitive directly
(`collector.reconcile()`, `collector.poll()`, `collector.drain()`,
`materialize_fingerprint()`, `SecTrafficBudget.clear_cooldown()`) with no
substitution to `reconcile_due()`/`cli.sec_command()`/a safer wrapper.
Anti-redirection independently confirmed, not merely trusted from Blue's
reception note.

Read `audit.py`, `scheduler.py`, `supervisor.py`, `budget.py`, and the
relevant `collector.py` sections in full (not summaries) to verify the
mechanism behind each fix, not just its test's assertion.

Independently reproduced (own scripts, beyond the shipped test suite):

- B2 sub-scenarios: corrupted (not just deleted) `CHILD_LAUNCH_AUTHORIZED`
  tail, deleted `deployment_authorities.jsonl`, and a forged
  `AUTOMATIC_RESTART_AFTER_FAILURE` claim without a genuine witnessed exit —
  all fail closed under a simulated offline-auditor process identity
  (`lifecycle["qualifying_service_mode"] = False` on the auditing collector,
  durable evidence otherwise untouched). B2 verdict: CLOSED, independently
  re-verified across more sub-cases than the single canonical regression
  test covers.
- B1: read `reconcile()`'s body directly; the settlement-boundary check
  (`reconciliation_due() != day` -> `RECONCILIATION_NOT_DUE`, no request) is
  the first statement in the method body, before `_guard_public_mutation`
  even runs. Confirmed this is not test-shaped.

New probes that did **not** find a working end-to-end bypass, but are
recorded as committed audit evidence because they document real, narrow
properties of the candidate:

- `collector.poll()` does not check `state.enabled` at all; a disabled lane's
  `poll()` still performs a live discovery request if called directly. The
  retrospective audit still catches the window via
  `ACQUISITION_DISABLED_DURING_WINDOW` (any DISABLED transition inside the
  window is unconditionally non-accountable), so this is a design/operational
  observation, not a Gate A false pass.
- `acquisition_critical_fingerprint` does not bind `service_managed`/
  `invocation_id`. A process that forges `QUANT_SEC_QUALIFYING_MODE=1` plus
  matching poll/unit-digest environment variables (without ever being
  launched by a recognised service manager) can share the exact fingerprint
  of the real qualifying collector, even though its own
  `lifecycle_provenance()` correctly reports `qualifying_service_mode=False`.
  In the reproduced scenario this did not produce `accountable=True`, because
  the rogue's own scheduler activity collided with the real collector's
  obligation chain (`OBLIGATION_SUPERSEDED_MORE_THAN_ONCE`). Classified
  MISSING_PROOF: the fingerprint blind spot is a verified FACT; Astra did not
  find a scenario where it alone produces a false accountable=True, but did
  not exhaustively search all orderings either.

Both probes are committed as `tests/test_astra_gate_a_v3_audit.py` on this
branch (audit-only; no production code touched) and currently pass, i.e. the
candidate currently fails closed in both cases.

## Findings ledger so far

| id | classification | verdict |
|---|---|---|
| B1 direct reconcile | REAL_DEFECT (v2) | CLOSED in v3, independently confirmed |
| B2 offline audit authority | — | CLOSED, independently re-verified (3 extra sub-cases) |
| B3 poll/drain | REAL_DEFECT (v2) | CLOSED in v3, independently confirmed |
| B3 fingerprint provenance | REAL_DEFECT (v2) | CLOSED in v3, independently confirmed |
| B3 cooldown provenance | REAL_DEFECT (v2) | CLOSED in v3, independently confirmed |
| D1–D5 | REAL_DEFECT (v2) | CLOSED in v3, independently confirmed |
| disabled-lane poll() | NON_ISSUE for Gate A (caught at window level) | new observation, not blocking |
| fingerprint blind spot on service_managed | MISSING_PROOF | new observation, not blocking, not demonstrated exploitable |

No new REAL_DEFECT found as of this checkpoint.

## Next action

Search remaining section-7 attack surfaces not yet directly probed
(duplicate/reordered supervisor events beyond what D4's tests cover; t0
equality-boundary slicing beyond the existing D5 test; reconciliation
tolerance-boundary wrong-kind attempts), then write the final Astra handoff
with an explicit AUDIT_GATE_A_V3 verdict.

## Safety state (unchanged)

`t0 = NOT DECLARED`
`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`
`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`
`REAL_CAPITAL_AUTHORIZED = FALSE`
`PRODUCT_INTEGRATION = PAUSED`
