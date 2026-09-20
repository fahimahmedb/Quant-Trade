# BUILDER GATE A V3 FINAL HANDOFF — 2026-09-20

## 0. Role and non-claims

This is the Builder handoff for Gate A v3. It reports implementation and reproducible evidence only.

Builder does **not** declare:
- Gate A PASS;
- audit PASS;
- t0;
- P14D continuity;
- target-host readiness;
- real-capital authorization;
- Gate B readiness.

Blue / Mission Control remains the decision authority. Independent Astra review is still required after Blue reception.

## 1. Authority chain

- North Star: `QUANT_NORTH_STAR.md`
- Blue authority branch: `claude/quant-blue-master-2026-09-20-mogpvh`
- Blue authority handoff: `handoff/BLUE_MASTER_ORCHESTRATOR_2026-09-20.md`
- Frozen Gate A v2 base:
  `blue/p0-gate-a-v2-final-2026-09-20 @ db166fd04c681e67a2c6d4440828af14ef58c48c`
- Independent Gate A v2 audit:
  `astra/p0-gate-a-v2-independent-audit-2026-09-20 @ 64b105f5a2cc1d798d1cf1e41e715b967c845a85`
- Builder branch:
  `builder/p0-gate-a-v3-2026-09-20`
- Proven implementation candidate HEAD:
  `b278e4c5403adcc92d2c065f2d305365e48ec6f0`
- Final delivery HEAD:
  resolve `origin/builder/p0-gate-a-v3-2026-09-20`.
  A commit cannot truthfully embed its own SHA. Blue must resolve the branch HEAD before reception.

The Builder branch is a linear descendant of the frozen v2 SHA and does not modify the frozen branch.

## 2. Scope actually changed

Compared with `db166fd04c681e67a2c6d4440828af14ef58c48c`, the proven implementation candidate is 18 commits ahead / 0 behind.

Changed paths are limited to Gate A v3 SEC proof/runtime surfaces, their tests, status, and Builder checkpoint:

- `src/quant/dataplane/sec/audit.py`
- `src/quant/dataplane/sec/budget.py`
- `src/quant/dataplane/sec/collector.py`
- `src/quant/dataplane/sec/scheduler.py`
- `src/quant/dataplane/sec/store.py`
- `scripts/quant.py`
- `tests/test_gate_a_v3_red.py`
- `tests/test_sec_form4_capture.py`
- `tests/test_astra_pre_t0.py`
- `STATE.md`
- `handoff/BUILDER_GATE_A_V3_CHECKPOINT_2026-09-20.md`

No Forward, Economic, Desk, Risk, Book, Product Integration, Gate B, P14D governance, or real-capital execution code was integrated.

## 3. Seven Gate A v3 correction surfaces

### Surface 1 — Due reconciliation proof

Implemented independent/prospective reconciliation obligations so an omitted daily reconciliation remains detectable even if Clock never dispatches the action.

The obligation is typed `RECONCILE` and is materialized independently of a successful reconciliation call.

### Surface 2 — Typed obligation resolution

Scheduler obligations now carry a required action kind.

Audit resolution requires the attempt's `attempt_kind` to match the obligation's required action kind. A wrong-kind attempt cannot retire an obligation merely because id/time match.

### Surface 3 — Qualifying mutation authority

Public primitive fidelity is retained.

The correction is applied at the public primitive/authority boundary rather than only in safer wrappers:
- direct `collector.reconcile()`;
- direct `collector.poll()`;
- direct `collector.drain()`;
- fingerprint materialization;
- durable budget/cooldown mutation.

A qualifying process can no longer rely only on forgeable local environment markers. It must bind its collector instance to the exact durable externally authorized child launch.

The same external `CHILD_LAUNCH_AUTHORIZED` identity cannot be silently reclaimed by a second collector. An unclaimed/duplicate qualifying service start fails closed with `QUALIFYING_MUTATION_AUTHORITY_UNBOUND`.

### Surface 4 — Supervisor terminal/current liveness

Retrospective audit consumes durable terminal child-exit evidence.

A current qualifying child that has a matching `CHILD_EXIT_OBSERVED` cannot remain accountable merely because `supervisor_state.json` is absent or historical launch evidence still exists.

### Surface 5 — Raw-object referential integrity

`verify_objects()` now walks durable references and verifies:
1. the referenced object exists;
2. its bytes re-hash successfully;
3. the hash equals the referenced content address.

Deleting a still-referenced raw object is therefore detectable.

### Surface 6 — Pre-t0 baseline lifecycle

When t0/window start falls between ticks, audit retains the relevant pre-window baseline lifecycle record for structural lifecycle validation.

This correction is intentionally scoped to **baseline lifecycle only**. It does not add unsupported predecessor-obligation tolerance/context.

### Surface 7 — Qualifying state mutation provenance

Fingerprint rematerialization and budget/cooldown durable mutations are either:
- provenance-bearing; or
- genuinely non-mutating/idempotent.

Fresh/unbound budget objects fail closed when qualifying durable history exists. Arbitrary public/no-op callback binding cannot mint budget mutation authority.

## 4. Primitive-level RED integrity

The Gate A v3 discriminants were kept on the named primitives.

Specifically:
- B1 tests public `collector.reconcile()` directly.
- B3 poll tests public `collector.poll()` directly.
- B3 drain tests public `collector.drain()` directly.
- D1 keeps discovery healthy while deliberately omitting reconciliation.
- D2 attempts to resolve a discovery obligation with a reconciliation attempt.
- D3 deletes a referenced raw object.
- D4 supplies terminal supervisor evidence with an open obligation.
- D5 places t0 between ticks and checks baseline lifecycle preservation.
- fingerprint mutation attacks public `materialize_fingerprint()`.
- cooldown mutation attacks public `SecTrafficBudget.clear_cooldown()`.
- second-order attacks forge qualifying environment markers and attempt duplicate external-launch claims.

No Gate A v3 red was redirected from a raw/public primitive to `reconcile_due()`, `cli.sec_command()`, or another safer wrapper merely to make it green.

## 5. Adversarial reproduction chronology

Important reproduced defects and closures include:

- `8609aaa0`: initial primitive RED set.
- `7d11e812`: fresh budget instance reproduced a qualifying mutation-authority bypass as the sole full-suite failure.
- `a550da04`: unbound qualifying budget mutation made fail-closed.
- `f287f74f`: second-order terminal-liveness and forged budget-authority attacks.
- `6fc9f10d`: arbitrary/no-op budget callback can no longer mint authority.
- `bccd9420`: terminal child-exit evidence is consumed even without supervisor state.
- `7b56a064`: forged qualifying-environment direct `poll()` bypass reproduced.
- `a6ad8bbf`: qualifying public mutation bound to one exact external child launch.
- `6ed7c9a5`: stronger duplicate-launch-claim discriminant added.
- `e1869a11`: unclaimed qualifying service start made fail-closed.
- `b278e4c5`: discriminant accepts legitimate fail-closed duplicate-launch rejection.

Intermediate failing runs are part of the red-first evidence trail and are not presented as production regressions that were ignored.

## 6. Regression / proof result on proven implementation candidate

Exact proven implementation candidate:
`b278e4c5403adcc92d2c065f2d305365e48ec6f0`

Exact-head GitHub Actions run:
`35513010411`

Result:
`COMPLETED / SUCCESS`

Successful workflow stages:
- Fail-closed check with no SEC identity;
- generated schema drift;
- status artifact freshness;
- full unit suite;
- SEC P0 lane suite;
- V1 end-to-end regression;
- exact-head verification artifact generation;
- exact-head verification artifact upload;
- committed verification placeholder restore;
- clean working tree.

Committed proof inventory at that candidate:
- 411 unit tests discovered;
- 35 end-to-end demo assertions.

Earlier exact-head green evidence also exists for intermediate corrective commits, including `a550da04`, `a6ad8bbf`, and `9000a1b2`; these are supporting chronology only. Proof is not silently transferred from those SHAs to this final candidate.

## 7. B2 regression

The v2 independent audit classified the offline-audit-authority issue B2 as closed.

Gate A v3 did not reopen or weaken that boundary. Offline invocation mode is not used to downgrade durable qualifying external authority.

Blue and Astra should independently verify this again; Builder does not self-certify it.

## 8. Safety state preserved

Builder did not declare or authorize any of the following:

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

No target-host rodage, Gate B, Forward integration, Economic integration, Product integration, or real-capital work was started from this branch.

## 9. Known limitations / non-proof

- Repository CI SUCCESS does not prove target-host continuity.
- This does not prove 14-day continuity.
- This does not prove economic readiness.
- This does not authorize t0.
- This does not authorize capital.
- Builder is not an independent certifier of its own implementation.
- The final handoff commit itself must receive exact-head CI SUCCESS before this branch is treated as delivered.

## 10. Blue reception contract

Next owner: **Blue / Mission Control**.

Blue should independently:
1. resolve the current branch HEAD;
2. verify ancestry from `db166fd04c681e67a2c6d4440828af14ef58c48c`;
3. inspect the complete diff and scope;
4. verify all seven correction surfaces;
5. re-check primitive-target fidelity / anti-redirection;
6. verify B2 remains closed;
7. inspect exact-head CI on the final delivery HEAD;
8. freeze the exact candidate SHA only after reception;
9. then hand that frozen SHA to independent Astra;
10. receive Astra's result before making any Gate disposition.

Builder stops here. This document is **not** a Gate A verdict.
