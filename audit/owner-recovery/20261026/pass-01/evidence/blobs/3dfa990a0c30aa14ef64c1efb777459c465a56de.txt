# BLUE CHECKPOINT — GATE A V2 READY FOR INDEPENDENT AUDIT — 2026-09-20

## Purpose

Durable handoff for starting a fresh independent audit conversation without relying on chat memory.

This checkpoint is written on a separate branch so the qualifying candidate remains frozen.

Candidate branch:
`blue/p0-gate-a-v2-final-2026-09-20`

Candidate HEAD:
`db166fd04c681e67a2c6d4440828af14ef58c48c`

Exact-head CI:
`35504152951 = COMPLETED / SUCCESS`

Do not move or modify that candidate branch while it is under independent audit.

## North Star

Read `QUANT_NORTH_STAR.md` first.

The architectural objective remains a persistent autonomous quantitative system that discovers, selects and monetizes real edge while preserving persistent state and learning from outcomes.

The terminal objective remains long-run net economic gain after real frictions.

P0 work is only one dependency of that system. Passing P0 repository qualification is not itself the product objective.

## Current hard flags

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

Target-host Gate B has not been proven.

No live qualifying window has begun.

## Authoritative Astra baseline

Branch:
`astra/p0-deep-adversarial-pre-t0`

HEAD:
`643deacdf5bbbdb1d2410c762eb20f72aff16bbf`

Exact-head CI:
`35478796506 = SUCCESS`

Important Astra conclusion:
repository-side capture integrity/PIT/firewall work was previously closed, but final target-runtime entrance and rodage remained unproven.

## Gate A v1 — rejected

Branch:
`blue/p0-gate-a-final-2026-09-20`

HEAD:
`19b6069e485c2e619698e235d24a6110556b1865`

Exact-head CI:
`35481518804 = COMPLETED / SUCCESS`

Independent audit verdict reported after that run:
`AUDIT_GATE_A = BLOCKED`

Therefore v1 is permanently treated as rejected despite green CI.

Do not reuse a PASS assumption from its test status.

## Confirmed v1 blockers and Blue reproductions

### B1 — direct reconciliation runtime bypass

Problem:
an operator path could explicitly request reconciliation for a day without being forced through the same due-calendar/settlement ordering boundary used by Clock.

Old red evidence:
branch `blue/p0-calendar-direct-reconcile-red-2026-09-20`
HEAD `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f`
CI `35480069110 = FAILURE`

Intended discriminant:
`test_direct_reconcile_before_settlement_emits_no_request`

Observed bad behavior:
the direct reconciliation call emitted a request before settlement instead of returning NOT_DUE.

Final runtime-boundary fix:
branch `blue/p0-direct-reconcile-fix-2026-09-20`
HEAD `dc9769b2790e724aaa281af209d822449d0bedfb`
CI `35481924437 = SUCCESS`

Design:
- Clock remains owner of WHEN.
- `reconcile_due(day)` is the runtime boundary used by Clock and CLI.
- lower `reconcile(day)` remains the comparison primitive.
- early/out-of-order runtime calls return `RECONCILIATION_NOT_DUE`.

### B2 — offline audit authority bypass

Problem:
external lifecycle authority validation could be skipped when the process executing the retrospective audit was itself non-qualifying/offline.

Red evidence:
branch `blue/p0-audit-authority-red-2026-09-20`
HEAD `ca0f6b00c3e88e2a6e6d541ad538a529bfb57aee`
CI `35482014024 = FAILURE`

Exactly one intended failure:
`test_offline_auditor_cannot_skip_qualifying_external_authority`

Observed false pass:
the report had no findings after removing supervisor authority because the auditor process identity weakened validation.

Fix:
branch `blue/p0-audit-authority-fix-2026-09-20`
HEAD `a98bc8aef3a397c054a3df495f14a781b1b939de`
CI `35482184292 = SUCCESS`

Design:
strict lifecycle validation is selected from the durable qualifying lifecycle records being audited, not from the identity of the shell/offline auditor process.

### B3 — manual operator intervention / sec-probe false pass

Problem:
a manual `sec-probe` could run before the normal due time, supersede the qualifying obligation and still leave the retrospective audit `accountable=True`.

Direct red evidence:
`345e18d94963b4fcc7063d73d1c23aff5244ca28`
CI `35482072929 = FAILURE`

Real CLI red evidence:
branch `blue/p0-manual-probe-red-2026-09-20`
HEAD `efbf72484e5e6873aba2446d53a728798b3f453f`
CI `35482105941 = FAILURE`

Exactly one intended CLI failure:
`test_early_manual_probe_cannot_supersede_qualifying_obligation`

Observed false pass:
manual early acquisition left `report['accountable'] == True`.

Fix proof branch:
`blue/p0-manual-operator-provenance-fix-2026-09-20`
HEAD `927f496a58fe71ffbaa6cce4df5297fe9638d0bb`
CI `35482288370 = SUCCESS`

Final consolidated implementation uses an explicit operator-intervention lifecycle record with `MANUAL_START`, recorded before the acquisition/state mutation.

## Gate A v2

Intermediate consolidated branch:
`blue/p0-gate-a-v2-2026-09-20`

HEAD:
`d652d6dc9bda0c920b6ceb00437c14b904666497`

Exact-head CI:
`35482419456 = SUCCESS`

This version contains the cleaner dedicated `record_operator_intervention()` implementation.

Final audit candidate:
`blue/p0-gate-a-v2-final-2026-09-20`

HEAD:
`db166fd04c681e67a2c6d4440828af14ef58c48c`

Exact-head CI:
`35504152951 = COMPLETED / SUCCESS`

Proof inventory:
`396 unit tests discovered`

The final delta adds explicit CLI proof that real `sec-reconcile --day` cannot emit a request before the reconciliation date is due.

## What the next conversation must do

Start a NEW independent audit conversation.

Do not ask it to continue Blue implementation.

The sequence is:

1. Read North Star, Astra checkpoint and qualifying deployment contract.
2. Verify the exact candidate SHA and exact-head CI independently.
3. Perform a blind audit of Astra baseline -> v2 and v1 -> v2 before trusting Blue explanations.
4. Replay all three v1 blocker families:
   - B1 direct reconciliation;
   - B2 offline audit authority;
   - B3 manual operator intervention.
5. Attack the fixes themselves.
6. Search for new repository-side defects rather than stopping after the regressions close.
7. Do not modify the audited candidate.
8. If a new defect is suspected, first build a discriminating red test on a separate branch.
9. Give a final repository-side verdict.

Required final audit verdict:
`AUDIT_GATE_A_V2 = PASS | PASS_WITH_RESIDUALS | BLOCKED`

Required regression verdicts:
`B1_DIRECT_RECONCILE = CLOSED | STILL_OPEN | INCONCLUSIVE`
`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED | STILL_OPEN | INCONCLUSIVE`
`B3_MANUAL_OPERATOR_INTERVENTION = CLOSED | STILL_OPEN | INCONCLUSIVE`

Required gate recommendation:
`REPO_GATE_A_CAN_CLOSE`
or
`REPO_GATE_A_MUST_REOPEN`

## Important adversarial targets for v2

Do not judge by test count.

Try to falsify:

- Clock ownership of scheduling;
- no alternate runtime scheduler;
- direct/manual CLI paths;
- public lower-level primitives reachable from runtime;
- oldest-due reconciliation ordering;
- EDGAR business calendar / holidays / DST / 22:00 ET + 30 elapsed hours;
- no 404-based holiday laundering;
- request-intent -> reserve -> network -> receive -> finish accounting;
- one obligation -> one resolution;
- supersession authorization and chronology;
- manual mutation before/after due;
- manual mutation during pending work / cooldown / backoff;
- offline audit semantics;
- supervisor event deletion/corruption;
- deployment authority consumption;
- restart witness semantics;
- fingerprint coverage for collector, audit, clock, CLI and calendar;
- crash windows around scheduler/state/request persistence;
- single-writer locking;
- shared SEC requester budget assumptions;
- PIT reconstructability;
- raw object durability;
- firewall / anti-selection leakage;
- 20,160-obligation long-history behavior;
- tests that pass because they mock the very property they claim to establish.

Separate:
- REAL_DEFECT
- TEST_DEFECT
- MISSING_PROOF
- TARGET_HOST_ONLY
- NON_ISSUE

## What remains after a successful Gate A v2 audit

Even if repository Gate A closes:

1. P14D remains frozen until explicit governance review/amendment.
2. Run the final P14D unique-property Red Team, especially wall-time/resource leak questions.
3. Decide whether the hybrid evidence protocol can explicitly supersede fixed P14D.
4. Gate B must then run on the real target host.
5. Only after authoritative method + clean/frozen Gate B may Blue declare a prospective t0.
6. Gate C live source-event window then runs from that declared t0.
7. Gate D performs final retrospective closure.

A repository PASS is not target-host readiness, continuity proof, t0, or capital authorization.

## Product lanes remain separate

Forward and Economic/Product integration must not be merged into the qualifying P0 tree merely because Gate A closes.

Maintain the isolation between:
- qualifying P0 runtime;
- product integration runtime;
- development branches.

## Immediate next action

Launch the fresh independent Gate A v2 audit against exactly:

`db166fd04c681e67a2c6d4440828af14ef58c48c`

Do not modify that SHA until the independent audit verdict is returned.
