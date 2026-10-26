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

---

# INDEPENDENT AUDIT PROGRESS CHECKPOINT — 2026-09-20T10:35:17Z

This section was appended by the independent auditor after the audit had begun.
It records executed evidence, not Blue's implementation claims.  The final
verdict has not yet been issued, but the reproduced repository defects below
are already sufficient to prevent a Gate A PASS unless disproved.

## Audit isolation and exact-head verification

- The candidate was inspected in a clean detached worktree at exactly
  `db166fd04c681e67a2c6d4440828af14ef58c48c`.
- The candidate branch was not modified.
- GitHub Actions run `35504152951` was queried independently through the
  GitHub API.  It is `completed / success`, with exact `head_sha`
  `db166fd04c681e67a2c6d4440828af14ef58c48c`.
- Its only job, `gate`, is `completed / success`; every reported step is
  complete and successful.  The commit check-runs endpoint likewise reports
  the exact-head `gate` check as successful.
- The merge base of Astra baseline `643deacdf5bbbdb1d2410c762eb20f72aff16bbf`
  and the candidate is exactly that Astra baseline.
- The mandatory North Star, the Astra checkpoint at the baseline, and the
  qualifying deployment contract were read from exact Git blobs.

## Blind-diff observations

The full Astra-baseline-to-v2 diff and the separate rejected-v1-to-v2 diff
were inspected before relying on the Blue correction narrative.

Important structural observation:

- commit `048be0f` initially placed the due-date guard in the public
  `reconcile(day)` method;
- commit `dc9769b` moved the guard to a new public wrapper
  `reconcile_due(day)` and restored an unguarded public `reconcile(day)`;
- Clock and the CLI use the wrapper, but arbitrary Python/runtime callers can
  still call the unguarded primitive;
- corresponding tests were changed to exercise `reconcile_due(day)` instead
  of proving that the reachable lower-level primitive cannot bypass WHEN.

The final CLI test calls `sec_command()` directly rather than entering through
the complete subprocess/parser/lock boundary.  A separate existing lock test
does prove rejection while the service lock is held, but it does not close the
public-Python boundary.

## Executed discriminating reproductions

### R1 — direct reconciliation before due emits a SEC request

Classification: `REAL_DEFECT`.

At Friday 2026-09-18 12:00 UTC, `reconciliation_due()` returned `None`.
Calling public `collector.reconcile(date(2026, 9, 18))` directly nevertheless
emitted a request for:

`/Archives/edgar/daily-index/2026/QT3/master.20260918.idx`

The fixture returned a client error only because it did not contain that daily
index.  The discriminating property is the already-observed outbound request
before the day was due.  This reproduces the B1 bypass below the new wrapper.

Provisional regression status:
`B1_DIRECT_RECONCILE = STILL_OPEN`.

### R2 — direct manual poll supersedes qualifying work and still audits true

Classification: `REAL_DEFECT`.

Starting from a qualifying externally attested collector, a normal poll/drain
produced `accountable=True`.  Before the next normal poll was due, the current
process lifecycle was changed to nonqualifying/unattested and public
`collector.poll()` was called directly, without the CLI intervention marker.

Observed:

- the new scheduler transition carried
  `LIFECYCLE_CAUSE_UNATTESTED`;
- it superseded the prior qualifying obligation;
- the retrospective audit still returned `accountable=True` with no findings.

The audit does not bind each scheduler transition/supersession to a matching
durable, externally authorized lifecycle instance.

### R3 — supervised manual stop/current stopped state still audits true

Classification: `REAL_DEFECT`.

After a qualifying normal capture, the reproduction appended a durable
`CHILD_EXIT_OBSERVED` event with `stopped_by_supervisor=True` and wrote
`supervisor_state.json` with `supervisor_running=False`.  With the next
obligation still pending, `audit_observation_window()` returned:

- `accountable=True`;
- no findings;
- one pending obligation.

On the same evidence, `_external_lifecycle_binding_error()` returned
`EXTERNAL_SUPERVISOR_NOT_ACTIVE`.  Thus readiness/lifecycle validation knows
the supervisor is inactive while the retrospective audit ignores it.

### R4 — deletion of a referenced raw object is not detected

Classification: `REAL_DEFECT`.

After a qualifying poll/drain, a raw object referenced by the raw manifest was
deleted.  The manifest still referenced the deleted digest.  Nevertheless:

- `store.verify_objects()` returned an empty broken-object list because it
  scans only files that still exist;
- the retrospective audit remained `accountable=True` with no findings.

This is a PIT/durability false pass: neither `sec-verify` nor the observation
audit proves that every referenced raw object still exists.

### R5 — fingerprint rematerialization is an unmarked manual mutation

Classification: `REAL_DEFECT`.

After qualifying evidence existed, the materialized fingerprint file was
deleted and `materialize_fingerprint()` was called again, matching the real
`sec-fingerprint` command's behavior.

Observed:

- the semantic fingerprint stayed the same;
- the freeze-file bytes changed because the materialization time changed;
- zero operator-intervention lifecycle rows were added;
- the retrospective audit still returned `accountable=True` with no findings.

`sec-fingerprint` takes the service lock but is omitted from the set of CLI
commands that call `record_operator_intervention()` before mutation.

Provisional regression status from R2/R3/R5:
`B3_MANUAL_OPERATOR_INTERVENTION = STILL_OPEN`.

## B2 replay executed so far

The offline-auditor regression was replayed using durable qualifying lifecycle
evidence while the audit process itself was nonqualifying/offline.

- deleting `supervisor_events.jsonl` produced
  `LIFECYCLE_EXTERNAL_AUTHORITY_MISSING` and `accountable=False`;
- corrupting the supervisor-events tail produced
  `ACQUISITION_EVIDENCE_INVALID` and `accountable=False`;
- deleting `deployment_authorities.jsonl` produced
  `DEPLOYMENT_AUTHORITY_CONSUMPTION_MISSING` and `accountable=False`.

Provisional status for the exact v1 offline-mode bug:
`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED`.

This does not close the distinct transition-binding and stopped-supervisor
defects above.

## Existing tests independently rerun

- 12 continuity/calendar/reconciliation tests passed, covering wrapper/CLI
  early refusal, weekend, 2026 SEC holiday, DST, and settlement behavior.
- 11 selected Astra lifecycle/authority tests passed.
- the readiness/audit deployment-authority parity test passed.
- the subprocess service-lock exclusion test passed.
- the unsolicited zero-exit supervisor test passed.
- one selected-test command also contained a stale/nonexistent test class name;
  its loader error was command selection error, not a candidate failure.

These green tests establish behavior of their selected boundaries but do not
invalidate the red reproductions above.

## Other open adversarial observations

- public acquisition and budget mutators remain reachable directly, including
  `poll()`, `drain()`, `enable()`, `disable()`, `reconcile()`, and
  `SecTrafficBudget.clear_cooldown()`;
- `clear_cooldown()` is durable but has no operator/lifecycle provenance;
- scheduler transitions carry lifecycle fields, but the audit does not require
  a matching external launch authority for every transition;
- the audit does not consume final supervisor liveness/stop evidence;
- unconsumed or action-mismatched attempts require further discriminating
  checks because obligation resolution matching is primarily identity/time
  based;
- the 20,160-obligation stress fixture advances one record per ten minutes,
  spanning about 140 days despite describing a 14-day density proof;
- raw-locator/source-version reconstruction performs repeated journal scans
  and needs real-volume complexity assessment;
- journals are ordinary mutable files, so target-host permissions/immutability
  remain Gate B evidence even after repository logic is repaired;
- prospective t0 authority is not yet declared or proven.

## Remaining work after this checkpoint

1. Complete the manual-intervention matrix, including pending work,
   cooldown/backoff, direct budget mutation, and post-hypothetical-t0 cases.
2. Compute and compare acquisition-critical fingerprints for Astra, v1, and
   v2 under identical explicit service configuration.
3. Run the full local candidate test suite and repository verification checks.
4. Complete new-defect probes for attempt-action binding, crash windows,
   multi-process semantics, audit-window boundaries, and long-history costs.
5. Issue the required final verdict and separate repository blockers from
   target-host-only residuals.

## Safety flags remain unchanged

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`REAL_CAPITAL_AUTHORIZED = FALSE`


---

# INDEPENDENT AUDIT PROGRESS CHECKPOINT — CONTINUATION — 2026-09-20T11:00Z

This continuation records additional independent falsification work after the
10:35:17Z checkpoint.  The qualifying candidate itself remains frozen at
`db166fd04c681e67a2c6d4440828af14ef58c48c`; no candidate file was modified.

## New reproduced defect — omitted reconciliation is invisible to the audit

Classification: `REAL_DEFECT`.

A qualifying collector was kept continuously active for 44 virtual hours with
normal discovery polls every 60 seconds.  The daily reconciliation action was
deliberately omitted.  At the end of the run:

- `collector.reconciliation_due()` reported that a daily reconciliation was
  due under the bound EDGAR calendar;
- every discovery cadence obligation remained durably accounted for;
- `audit_observation_window()` nevertheless returned `accountable=True`.

Root cause confirmed by exact-candidate code reading:

- `reconciliation_due()` independently knows when the oldest daily-index
  reconciliation is due;
- the retrospective audit builds expected work only from scheduler transitions
  already written to the journal;
- therefore, if Clock omits an entire action class and never writes the
  corresponding transition, the audit has no independent calendar oracle from
  which to derive that missing action.

This is not a test-count issue.  It is a proof false-positive: the mechanism
whose contract says it must not infer that work was not due merely because no
attempt was recorded can still make exactly that inference for reconciliation
when the scheduler itself omits the work.

## New audit-window defect — prospective t0 between ticks loses context

Classification: `REAL_DEFECT`.

A separate discriminant starts with an already-running, qualifying service whose
full-history audit is accountable.  It places prospective `t0` halfway between
two 60-second ticks and then performs the next normal poll.

Exact-candidate window slicing keeps a pre-t0 scheduler transition when its due
time falls after t0, but filters lifecycle rows to records at/after t0.  The
latest pre-t0 lifecycle is retained only as `baseline_lifecycle` for external
authority validation; it is not passed to structural lifecycle validation.
Likewise, a retained transition can name a supersession target that is filtered
out because the predecessor was both created and due before t0.

Consequences on an otherwise healthy already-running service include spurious
structural findings such as missing lifecycle provenance and/or unknown
supersession ancestry.  A valid prospective t0 declaration between ticks can
therefore produce a false negative rather than a coherent observation window.

This defect is distinct from the earlier B2 offline-auditor bug: B2 correctly
uses durable qualifying history to decide whether strict authority validation
applies, while this defect concerns the consistency of explicit-window slicing.

## Durable red branch created

Independent audit branch:

`astra/p0-gate-a-v2-independent-audit-2026-09-20`

Merge base:

`db166fd04c681e67a2c6d4440828af14ef58c48c`

First red-test commit:

`d72b057bce8d7e2c0168d8d7bd4af52d26c4c0ba`

It adds only:

`tests/test_gate_a_v2_independent_audit.py`

with two discriminants:

1. `test_omitted_due_daily_reconciliation_cannot_audit_accountable`
2. `test_t0_between_ticks_preserves_pre_t0_lifecycle_and_supersession_context`

Because repository status freshness binds the discovered unit-test count,
the audit-only branch then refreshed the proof inventory from 396 to 398 tests:

`e3c51e6b937646c77fea037f8cb8a505d272b4c2`

A compare against the frozen candidate shows the audit branch is exactly two
commits ahead and changes only:

- `tests/test_gate_a_v2_independent_audit.py`;
- the single `STATE.md` proof-inventory count line.

No production implementation file differs from the frozen candidate.

GitHub Actions run for exact audit-branch head
`e3c51e6b937646c77fea037f8cb8a505d272b4c2`:

`35506576224`

Status at this checkpoint: `IN_PROGRESS`.

The expected discriminating outcome is a red full-unit-suite failure caused by
the two assertions above, after ordinary repository freshness checks pass.  Do
not convert that expectation into a fact until the run completes.

## Gate implication already established independently of pending CI

The earlier reproduced defects R1-R5 already prevent a Gate A PASS.  The omitted
reconciliation false-positive adds a separate reason the repository audit cannot
currently certify scheduler completeness.

Current evidence state:

`B1_DIRECT_RECONCILE = STILL_OPEN`

`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED` for the exact v1 regression, with
distinct lifecycle/transition-binding defects still open.

`B3_MANUAL_OPERATOR_INTERVENTION = STILL_OPEN`

A final audit verdict has not yet been durably issued in this checkpoint, but no
evidence currently supports closing repository Gate A.

## Resume point

1. Query run `35506576224` to confirm the two independent red discriminants.
2. Record exact CI result here.
3. Stop broadening the attack surface once the blockers are sufficiently
   discriminated; route narrowly scoped repairs to Builder.
4. Re-audit a new frozen candidate rather than modifying the rejected candidate.

Safety flags remain:

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
