# ASTRA MISSION — GATE A V3 INDEPENDENT AUDIT — 2026-09-20

## Role

You are the independent Astra / Red Team auditor for Quant P0 / Gate A v3.

Your role is **not** to confirm Builder or Blue. Your role is to search actively for ways the frozen candidate can still be false, incomplete, bypassable, under-specified, or insufficiently proven.

Do not modify the frozen candidate. Do not implement fixes in this mission.

## Mandatory authority chain

Read first, from repository truth:

1. `QUANT_NORTH_STAR.md`
2. `handoff/BLUE_GATE_A_V3_RECEPTION_2026-09-20.md` on `blue/master-v2-2026-09-20`
3. `handoff/BUILDER_GATE_A_V3_2026-09-20.md` on the frozen candidate
4. `handoff/ASTRA_GATE_A_V2_INDEPENDENT_AUDIT_2026-09-20.md` at `64b105f5a2cc1d798d1cf1e41e715b967c845a85`
5. `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` at `astra/p0-deep-adversarial-pre-t0@643deacdf5bbbdb1d2410c762eb20f72aff16bbf`
6. `governance/P0_GATE_A_EVIDENCE_INDEX_2026-09-20.md` on `blue/master-v2-2026-09-20`

Repository truth is authoritative over chat summaries.

## Exact pinned objects

Frozen rejected v2 baseline:
`db166fd04c681e67a2c6d4440828af14ef58c48c`

Canonical v2 independent audit:
`64b105f5a2cc1d798d1cf1e41e715b967c845a85`

Builder Gate A v3 branch:
`builder/p0-gate-a-v3-2026-09-20`

Frozen Gate A v3 candidate SHA:
`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Frozen Blue ref:
`blue/p0-gate-a-v3-frozen-2026-09-20`

Astra audit branch, pre-created exactly at the frozen candidate:
`astra/p0-gate-a-v3-independent-audit-2026-09-20`

Exact-head candidate CI:
`35514180655 = COMPLETED / SUCCESS`

Implementation-only green predecessor:
`b278e4c5403adcc92d2c065f2d305365e48ec6f0`
with `35513010411 = COMPLETED / SUCCESS`.

The delta from `b278e4c5...` to `2da079d8...` is documentation-only (Builder checkpoint + final handoff). Do not transfer proof silently; the final delivered SHA has its own exact-head green run.

## Historical defects that must be replayed independently

Canonical v2 verdict:

`AUDIT_GATE_A_V2 = BLOCKED`

`B1_DIRECT_RECONCILE = STILL_OPEN`

`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED`

`B3_MANUAL_OPERATOR_INTERVENTION = STILL_OPEN`

New v2 audit defects:
- D1 — due reconciliation not independently audited;
- D2 — obligation identity not bound to action kind;
- D3 — referenced raw object deletion false-passes integrity;
- D4 — terminal/current supervisor stop ignored;
- D5 — prospective t0 slicing loses baseline lifecycle.

Surface 7 also requires fingerprint/rematerialization and budget/cooldown mutation to be provenance-bearing or genuinely non-mutating/idempotent.

Historical anti-redirection evidence to preserve and replay:
- direct reconcile red:
  `blue/p0-calendar-direct-reconcile-red-2026-09-20 @ c81fa1cdf93d5b08265c5f06ed0f4424bdda917f`;
- original direct manual-probe/poll discriminant in history:
  `345e18d94963b4fcc7063d73d1c23aff5244ca28`
  retained through `blue/p0-manual-probe-red-2026-09-20`;
- canonical v2 audit branch:
  `astra/p0-gate-a-v2-independent-audit-2026-09-20 @ 64b105f5a2cc1d798d1cf1e41e715b967c845a85`.

Do not accept a repaired test that has moved from a primitive to a safer wrapper.

## Required audit procedure

### A. Verify the audit target before testing

Independently verify:
- current audit branch begins at exact frozen SHA `2da079d8...`;
- frozen Blue ref still points to exact `2da079d8...`;
- Builder branch delivery HEAD was `2da079d8...` at Blue reception;
- ancestry merge-base with v2 is exact `db166fd0...`;
- no evidence is silently borrowed from another SHA.

If any target moves, stop and classify the mismatch before continuing.

### B. Replay original primitive defects first

Replay at the raw/public primitives, not CLI wrappers:

1. B1 — direct `collector.reconcile()`.
2. B3 — direct `collector.poll()`.
3. B3 — direct `collector.drain()`.
4. D1 — maintain healthy discovery cadence across the real reconciliation deadline while deliberately omitting reconciliation.
5. D2 — attempt wrong-kind obligation resolution.
6. D3 — delete a raw object still referenced by durable evidence.
7. D4 — record terminal child exit/current stopped supervisor while an obligation remains pending.
8. D5 — set prospective t0 between ticks and require pre-window lifecycle context.
9. S7 fingerprint — direct `materialize_fingerprint()` after deleting the freeze.
10. S7 budget — direct `SecTrafficBudget.clear_cooldown()`.
11. Replay fresh-budget authority, arbitrary/no-op callback binding, forged qualifying environment, duplicate external-launch claim, and unclaimed qualifying service-start attacks.

### C. Re-check B2 independently

Do not assume Blue or Builder is correct.

Verify that offline/manual retrospective invocation cannot downgrade strict external authority when durable qualifying evidence exists.

At minimum attack:
- missing supervisor event authority;
- corrupted/tampered authority chain;
- missing deployment authority consumption;
- process-local offline/manual auditor identity;
- baseline lifecycle around prospective t0.

### D. Search for new bypasses

Do not stop when the listed reds pass.

Pressure-test at least:
- mutation authority before/after `record_service_start()`;
- copied environment markers and copied lifecycle identifiers;
- duplicate/reordered supervisor events;
- stale `supervisor_state.json` versus terminal event ordering;
- multiple launches/exits for the same supervisor/child identities;
- reconciliation obligation duplication/supersession;
- wrong-kind attempts around tolerance boundaries;
- reconciliation due exactly at/after settlement and cooldown edges;
- window slicing at equality boundaries;
- raw references present in any durable structure not walked by `verify_objects()`;
- state files deleted/recreated between operations;
- idempotent/no-op mutation paths that can still alter provenance or authority;
- interactions between manual operator intervention and qualifying process identity;
- crash/restart sequences that might reclaim mutation authority;
- any regression introduced by compatibility fallbacks for legacy transitions.

Classify each finding as one of:
`REAL_DEFECT`, `TEST_DEFECT`, `MISSING_PROOF`, `TARGET_HOST_ONLY`, `NON_ISSUE`.

For any suspected defect, reproduce with an independent discriminant before proposing a fix.

## CI and evidence discipline

Green CI is execution evidence, not scientific certification.

If Astra adds audit-only tests:
- keep production candidate code unchanged;
- commit only audit tests/checkpoint/handoff on the Astra branch;
- run exact-head CI for the audit commit;
- distinguish a deliberate red audit result from candidate workflow health.

Do not transfer success or failure across SHAs.

## Forbidden conclusions during Astra audit

Do not declare:
- t0;
- P14D continuity;
- target-host readiness;
- Gate B;
- product integration;
- real capital;
- economic readiness.

These remain downstream.

## Required final handoff

Write:
`handoff/ASTRA_GATE_A_V3_INDEPENDENT_AUDIT_2026-09-20.md`

The handoff must include:
- exact candidate SHA;
- exact Astra audit HEAD;
- exact test/reproduction SHAs;
- exact CI run IDs and conclusions;
- B1/B2/B3 verdicts;
- D1-D5 verdicts;
- S7 verdicts;
- any new defects;
- classification of every material finding;
- explicit `AUDIT_GATE_A_V3 = PASS | BLOCKED`;
- exact falsifier / what would change the verdict;
- unchanged safety state.

Return ownership to Blue / Mission Control after the handoff. Do not implement candidate fixes in the audit mission.
