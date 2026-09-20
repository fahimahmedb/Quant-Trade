# ASTRA INDEPENDENT AUDIT — P0 / GATE A V2 — 2026-09-20

## Scope and authority

Classification: **FRONTIER-WORTHY**.

This is the independent repository-side audit of the frozen Gate A v2 candidate.

Candidate branch:
`blue/p0-gate-a-v2-final-2026-09-20`

Candidate SHA:
`db166fd04c681e67a2c6d4440828af14ef58c48c`

Authoritative Astra baseline:
`643deacdf5bbbdb1d2410c762eb20f72aff16bbf`

Rejected Gate A v1:
`19b6069e485c2e619698e235d24a6110556b1865`

Audit-only branch:
`astra/p0-gate-a-v2-independent-audit-2026-09-20`

North Star, the Astra checkpoint and
`governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` were read before
issuing this verdict.  The candidate implementation was not modified.

## Exact-head evidence

**FACT** — GitHub compare reports the candidate branch identical to
`db166fd04c681e67a2c6d4440828af14ef58c48c`.

**FACT** — candidate GitHub Actions run `35504152951` is
`completed / success` and is bound to exact head
`db166fd04c681e67a2c6d4440828af14ef58c48c`.

**FACT** — green candidate CI is not sufficient to decide Gate A.  Independent
red discriminants rooted at the exact candidate have already reached the full
unit-suite step and failed there.  In particular audit commit
`04f84d02b9f541e65bc5a8bb5ec64e8837fcb9ca` produced Actions run
`35506706067`; status-artifact freshness passed and the **Full unit suite
failed**.  That commit contains the omitted-reconciliation and t0-window
discriminants.

## Regression verdicts

`B1_DIRECT_RECONCILE = STILL_OPEN`

**FACT / REAL_DEFECT** — the public `reconcile_due(day)` wrapper rejects an
early/out-of-order day, but the public lower primitive `reconcile(day)`
remains reachable and immediately calls `_request("RECONCILE", ...)`.
Independent execution reproduced an outbound daily-index request while
`reconciliation_due()` was `None`.  Moving the guard into a wrapper did not
remove the lower runtime bypass.

`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED`

**FACT** — the exact v1 offline-auditor bug was replayed.  With durable
qualifying lifecycle evidence, deleting the supervisor authority, corrupting
its tail, or deleting deployment authority causes the retrospective audit to
fail.  Strictness is now selected from the durable qualifying window rather
than from the identity of the shell process running `sec-audit`.

This closes only B2.  It does not close the distinct lifecycle-transition and
supervisor-stop defects below.

`B3_MANUAL_OPERATOR_INTERVENTION = STILL_OPEN`

**FACT / REAL_DEFECT** — a direct public `collector.poll()` from an
unattested/nonqualifying process can supersede a qualifying obligation without
the CLI intervention marker and the retrospective audit can remain
`accountable=True`.

**FACT / REAL_DEFECT** — `sec-fingerprint` mutates/rematerializes the freeze
file under the service lock but is not among the commands that call
`record_operator_intervention()`.  Deleting and rematerializing the file
changed freeze bytes, added no operator-intervention lifecycle row, and the
audit still passed.

**FACT / REAL_DEFECT** — `SecTrafficBudget.clear_cooldown()` is a durable
public mutator with no lifecycle/operator provenance.  Together with reachable
direct acquisition methods, the qualifying runtime does not have a single
enforced authority boundary for manual mutation.

## New independent Gate A defects

### D1 — due reconciliation is not an independently audited obligation

Classification: **REAL_DEFECT**.

The audit derives obligations only from scheduler transitions.  The scheduler's
single open obligation describes discovery/backlog/cooldown timing; the source
calendar's daily reconciliation deadline is not independently materialized as
an obligation.

A real-policy reproduction kept satisfying discovery polls every 60 seconds
for 44 virtual hours from Friday 2026-09-18 12:00 UTC.  At the end,
`reconciliation_due()` returned the Friday business day, reconciliation had
been deliberately omitted, yet the retrospective audit returned
`accountable=True`.

The committed red discriminant is in
`tests/test_gate_a_v2_independent_audit.py`.  Run `35506706067` reaches the
full suite and fails.

This is materially stronger than "missing a unit test": a Clock regression
that simply stops dispatching reconciliation can still leave the proof layer
unable to derive that the action was due.

### D2 — obligation identity is not bound to required action kind

Classification: **REAL_DEFECT**.

`SecAttemptRecord` durably records `attempt_kind`, but
`audit._resolve_attempts()` resolves an obligation using only
`obligation_id` and the time window.  It never verifies that the attempt kind
matches the action required by the scheduler state.

A dedicated audit-branch red test binds an `AWAITING_POLL` obligation to a
`RECONCILE` request at the poll deadline and requires the audit to reject that
substitution.  The discriminant is
`tests/test_gate_a_v2_red.py`.

**INFERENCE** — until the audit binds action semantics, "one obligation -> one
resolution" is identity-safe but not action-safe; the wrong acquisition class
can satisfy the ledger.

### D3 — referenced raw object deletion can false-pass integrity

Classification: **REAL_DEFECT**.

After qualifying capture, deleting an object still referenced by durable
manifest/evidence left `store.verify_objects()` clean because
`verify_objects()` iterates only files that still exist.  The retrospective
audit also remained `accountable=True`.

The implementation confirms the mechanism: `verify_objects()` re-hashes
existing `*.bin` files but does not walk durable references and require every
referenced digest to exist.

This is a point-in-time reconstructability / durability false pass.

### D4 — terminal supervisor stop/liveness evidence is ignored by retrospective audit

Classification: **REAL_DEFECT**.

A qualifying capture followed by a durable `CHILD_EXIT_OBSERVED` with
`stopped_by_supervisor=True` and current supervisor state
`supervisor_running=False` still audited `accountable=True` while a next
obligation remained pending.

On the same evidence, the collector readiness binding reports
`EXTERNAL_SUPERVISOR_NOT_ACTIVE`.

The audit validates launch authority and restart witnesses, but it does not
consume terminal/current supervisor liveness as a window-closing fact.

### D5 — prospective t0 window slicing does not consistently carry baseline lifecycle

Classification: **REAL_DEFECT / qualification usability**.

The audit correctly selects a pre-t0 `baseline_lifecycle` for external
authority validation, but `_validate_structure()` receives only the
post-window lifecycle list.  If t0 is declared between normal ticks while the
qualifying service was already running, the post-t0 list can be empty and
structure validation can emit `LIFECYCLE_PROVENANCE_MISSING` despite a valid
baseline lifecycle.

A red discriminant for this case is committed in
`tests/test_gate_a_v2_independent_audit.py`.

This is primarily a false-negative qualification defect rather than a
false-positive continuity proof, but it matters because t0 is intended to be a
prospective declaration over an already-running qualifying service.

## Additional observations not promoted to new Gate A blockers

**TEST_DEFECT / MISSING_PROOF** — the 20,160-obligation stress fixture spans
roughly 140 days at one record per ten minutes although it is described as a
14-day density proof.  It is useful scale pressure but is not a faithful
14-day wall-time/resource proof.

**MISSING_PROOF** — raw-locator/source-version reconstruction repeatedly scans
journals and still needs real-volume complexity evidence.

**TARGET_HOST_ONLY** — filesystem permissions/immutability, actual systemd
stop/start and SIGKILL behavior, mount persistence, runtime image identity and
the final rodage artifact remain target-host evidence.  They cannot repair the
repository false-pass defects above.

## Required verdict

`AUDIT_GATE_A_V2 = BLOCKED`

`B1_DIRECT_RECONCILE = STILL_OPEN`

`B2_OFFLINE_AUDIT_AUTHORITY = CLOSED`

`B3_MANUAL_OPERATOR_INTERVENTION = STILL_OPEN`

`REPO_GATE_A_MUST_REOPEN`

## Why the gate must reopen

**FACT** — multiple independent repository paths can still produce or preserve
evidence that the retrospective proof layer accepts even though required
acquisition semantics were bypassed or durable evidence was lost.

**INFERENCE** — proceeding directly to target-host rodage would test deployment
quality on top of a proof layer already known to admit false positives.  A
successful rodage could therefore not close the scientific/continuity claim it
is supposed to support.

**RECOMMENDATION** — stop additional target-host qualification work on this
candidate.  Use Builder capacity on the smallest coherent repository correction
that closes the proof model, then independently replay the red discriminants.
Do not spend more Astra frontier quota on unrelated P0 architecture while these
decisive blockers are open.

## Minimum coherent correction surface

**RECOMMENDATION** —

1. Materialize every due acquisition class prospectively, including source
   calendar reconciliation; do not let "not written to the scheduler journal"
   mean "not due".
2. Give each obligation an explicit required action kind and require
   `attempt_kind` (or an equivalent typed resolution) to match before it can
   retire the obligation.
3. Enforce one qualifying mutation authority boundary for poll, drain,
   reconciliation, fingerprint materialization and budget/cooldown mutation.
   A public Python call must not silently have stronger authority than the CLI.
4. Make retrospective audit consume terminal/current supervisor liveness and
   stop evidence, not launch evidence only.
5. Verify referential integrity from durable manifests/envelopes/source-version
   records to raw objects: every referenced object must exist and re-hash to its
   address.
6. Carry the pre-window baseline lifecycle into all structural checks required
   for a prospective t0 declared between ticks.
7. Treat fingerprint rematerialization and any other qualifying-state mutation
   as explicit provenance-bearing intervention, or make the operation
   non-mutating/idempotent in the qualifying window.

After repair, rerun the focused reds first, then the full candidate suite and
exact-head CI.  Only a clean frozen successor candidate should return to
independent Gate A review.

## Falsifier / what would change this verdict

The verdict changes only if the reproduced scenarios are shown not to be
reachable under the repository's stated runtime contract, or a successor patch
makes the discriminants fail closed for the correct semantic reason while
preserving the existing closed regressions and full suite.

A green test count alone does not falsify these findings.

## Safety state

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

Gate B and later live-window work remain downstream of a repaired repository
Gate A.
