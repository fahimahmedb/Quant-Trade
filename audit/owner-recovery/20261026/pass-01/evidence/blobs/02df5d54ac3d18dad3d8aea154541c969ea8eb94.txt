# BLUE — F11 BUILDER RECEPTION / PARENT-PATH CLOSURE GATE — 2026-09-21

## 0. Purpose

This checkpoint receives the current Builder F11 handoff without yet authorizing Astra recheck.

The Builder has completed a materially stronger lock-path repair, but one Blue-mandated repository-level parent-path identity discriminant remains unclosed.

This checkpoint is non-authorizing.

```text
PASS_REPOSITORY_EVIDENCE = FALSE
ASTRA_F11_RECHECK_AUTHORIZED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
GATE_B_PASS_DECLARED = FALSE
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 1. Active Builder object

Active implementation branch:

`builder/gate-b-lock-path-identity-repair-2026-09-21`

Final Builder handoff HEAD currently observed:

`6ec12cd73de24b4a789d6abe9e292d8b616e3da1`

Handoff:

`handoff/BUILDER_GATE_B_LOCK_PATH_IDENTITY_REPAIR_2026-09-21.md`

Builder-declared status:

`GATE_B_LOCK_PATH_IDENTITY_REPAIR = READY_FOR_INDEPENDENT_REVIEW`

Audited repair baseline:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Lineage:

- ahead = 10;
- behind = 0;
- merge base = exact audited baseline.

Changed paths from the audited baseline:

- `scripts/quant_gate_b_runctl.py`;
- `tests/test_gate_b_lock_path_identity_repair.py`;
- `tests/test_gate_b_run_authority_m1_m3_repair.py`;
- `STATE.md`;
- Builder handoff.

No M4 verifier or frozen V4 `src/` change is present in this delta.

## 2. CI state

Pre-handoff implementation HEAD:

`ed51cc4251f556482eca18e396cc1c0d932879fb`

Exact-head CI:

`35608538693 = COMPLETED / SUCCESS`

The Builder handoff moved the branch to:

`6ec12cd73de24b4a789d6abe9e292d8b616e3da1`

Exact-head handoff CI:

`35610033532`

At this checkpoint it is still:

`IN_PROGRESS`

Observed completed stages already include:

- status artifact freshness = SUCCESS;
- full unit suite = SUCCESS;
- SEC P0 lane suite = SUCCESS.

Astra must not use the Builder handoff HEAD as final delivery evidence until `35610033532 = COMPLETED / SUCCESS`.

## 3. What the Builder repair closes

The current Builder repair materially closes the original F11 lock-file identity failure inside one stable configured registry parent directory.

The implementation now includes:

- a hard-link inode authority anchor for the public lock;
- repeated identity validation;
- parent-directory FD anchoring;
- an outer parent-directory `flock`;
- coordinated public-lock + anchor replacement coverage;
- repeated replacement coverage;
- real-process contention coverage.

Proof inventory at the implementation checkpoint:

`457 unit tests discovered`

A1-A10 remain regression surfaces, not reopened design work.

## 4. Blue parent-path closure requirement remains open

Blue previously committed:

`governance/BLUE_GATE_B_F11_BRANCH_RECONCILIATION_PARENT_PATH_CHALLENGE_2026-09-21.md`

That authority requires three discriminants before Builder reception can advance to Astra:

`F11-P1` — whole configured registry parent-path replacement while process A remains inside the real Registry critical section;

`F11-P2` — prove the replacement-parent contender performs no registry mutation if rejected;

`F11-P3` — define and prove deterministic post-condition/recovery semantics after the parent-path identity event.

The current dedicated Builder test file contains public-lock and authority-anchor replacement coverage, but no committed whole-parent-directory replacement discriminant satisfying F11-P1/P2/P3.

Therefore:

`F11_PARENT_PATH_IDENTITY_CHALLENGE = OPEN`

## 5. Residual-boundary classification

The Builder handoff labels ancestor/parent namespace stability as `TARGET_HOST_ONLY`.

Blue does not accept that classification yet for the specific F11-P1 case.

A same-filesystem parent-directory rename/replacement can be exercised entirely in a disposable repository-local temporary directory and can therefore be tested before target-host execution.

Target-host ownership, mount identity and ancestor namespace controls remain separate host-only evidence, but they cannot replace the required repository-local whole-parent-path discriminant.

## 6. Blue reception disposition

Current Builder reception:

```text
BUILDER_F11_HANDOFF_RECEIVED = TRUE
BUILDER_F11_IMPLEMENTATION_CI_GREEN = TRUE
BUILDER_F11_FINAL_HANDOFF_CI = IN_PROGRESS
F11_PARENT_PATH_IDENTITY_CHALLENGE = OPEN
BUILDER_F11_ACCEPTED_FOR_ASTRA = FALSE
ASTRA_F11_RECHECK_AUTHORIZED = FALSE
```

The Builder must continue on the same active implementation branch.

Do not create another F11 Builder branch.

Required active branch:

`builder/gate-b-lock-path-identity-repair-2026-09-21`

The mission-only duplicate remains superseded:

`builder/gate-b-f11-lock-identity-repair-2026-09-21`

## 7. Exact remaining Builder work

Before Astra dispatch, Builder must:

1. add F11-P1 whole-parent replacement reproduction using disposable local directories and real processes;
2. prove no concurrent second Registry mutation domain becomes usable;
3. add F11-P2 no-mutation evidence for a rejected replacement-parent contender;
4. add F11-P3 deterministic recovery/fail-closed semantics;
5. preserve A1-A10 regressions;
6. update the same Builder handoff;
7. obtain a new exact-head `COMPLETED / SUCCESS` workflow for the resulting final HEAD.

If F11-P1 reproduces a split authority domain, repair the implementation before final handoff.

## 8. Astra dispatch gate

Only after all of the following are true:

```text
F11_P1 = GREEN
F11_P2 = GREEN
F11_P3 = GREEN
BUILDER_FINAL_HANDOFF = COMPLETE
BUILDER_EXACT_HEAD_CI = COMPLETED / SUCCESS
BLUE_RECEPTION = PASS_FOR_INDEPENDENT_ASTRA_RECHECK
```

may Blue dispatch a fresh Astra F11 review.

Astra must then independently recheck:

- original F11 public-lock replacement;
- lock + authority-anchor coordinated replacement;
- whole-parent-path replacement;
- repeated replacement behavior;
- no-mutation fail-closed semantics;
- ordinary real-process serialization;
- A1-A10 non-regression.

Only Astra may establish:

`PASS_REPOSITORY_EVIDENCE`

## 9. Product / Antigravity state

Antigravity Product prestage remains complete and parked:

`parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21@568eea1e028302e14f96a06eb2515bb89aa73ad4`

No Product integration is authorized by this checkpoint.

## 10. Return control

`RETURN_CONTROL_TO = BUILDER_F11_PARENT_PATH_CLOSURE`

Astra remains stopped.
