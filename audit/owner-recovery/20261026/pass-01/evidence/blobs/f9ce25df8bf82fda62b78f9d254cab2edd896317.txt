# ASTRA — FIRST VERTICAL INDEPENDENT REVIEW — 2026-09-21

## 0. Verdict

```text
ASTRA_FIRST_VERTICAL_REVIEW = BLOCKED_REUSE_AS_IS_IMPORT_IDENTITY_DIVERGENCE_NOT_ADAPT_RECLASSIFIED
```

One reviewer cycle. One reproduced blocker, in attack domain A
(selective-import identity). Domains B–J reproduced clean, and all eleven
mandatory negative controls reproduced as required.

No score. No ranking. No architecture re-review.

## 1. Bound authority

```text
AUDITED_BUILDER_BRANCH = builder/post-p0-first-vertical-shadow-loop-2026-09-21
AUDITED_BUILDER_SHA    = 5c8b5b71ef627ac0ec0faa509edc40b7d9d0c4df
BUILDER_EXACT_HEAD_CI  = 35639267629 = COMPLETED / SUCCESS
  (workflow "SEC P0 pre-t0 gate", run_number 676, head_sha 5c8b5b71..., event push)
BLUE_RECEPTION_BRANCH  = blue/master-v2-2026-09-20
BLUE_RECEPTION_SHA     = bd061dcd5a2a75b37119ee3eb65edafd16a58544
BLUE_RECEPTION_CI      = 35658760465 = COMPLETED / SUCCESS
  ("governance: receive first-vertical Builder for one Astra review")
REVIEW_BRANCH          = astra/first-vertical-independent-review-2026-09-21
REVIEW_HEAD            = 8688226d927468d74c05db959711735c27f6e947
BUILD_BASE_SHA         = aa6a5c1
```

Lineage verified: `git merge-base --is-ancestor 5c8b5b71 HEAD` = true. The review
branch is the exact audited Builder object plus exactly one commit (8688226,
the ASTRA mission file, +228 lines, no source change). The audited Builder
object was not modified by this review.

`git log --merges aa6a5c1..5c8b5b71` is empty: no whole-branch merge. The
branch is twelve linear commits (2bc80e4 vendoring → 5c8b5b71 handoff).

## 2. Changed paths reviewed

`git diff --stat aa6a5c1 5c8b5b71` = 51 files, +12561/−17.

Vendored REUSE_AS_IS (30 files, manifest §2–4): `dataplane/{admissibility,
form4_parse,forward_admissibility,forward_recorder}.py`; the full `science/`
package (`__init__,eligibility,formation,inference,invariance,nulls,regimes`);
the full `economics/` package (19 files).

New/adapted Product surfaces: `science/effect.py` (+1581), `integration/
{__init__,forward_adapter,econ_bridge}.py`, `desk/economic_size.py` (+460),
`desk/{desk,execution}.py`, `book/ledger.py`, `learning/{durable,__init__}.py`,
`clock.py`, `paths.py`, `factory/workers.py`, `schemas/book_state.schema.json`,
`STATE.md`, and four test files (`test_first_vertical_science_effect.py`,
`test_m2_research_economic_boundary.py`, `test_m3_size_risk_fills_book.py`,
`test_learning_durable.py`, `test_vertical_e2e.py`).

## 3. Independent test commands and results

Executed by ASTRA on the review branch (audited Builder tree):

```text
PYTHONPATH=src python3 -m unittest discover -s tests -v
  -> Ran 478 tests in 30.336s -- OK (exit 0)
python3 -m compileall -q src
  -> exit 0, no syntax errors
python3 scripts/generate_schemas.py --check
  -> "schemas checked", exit 0, no drift
python3 scripts/demo_quant_system.py
  -> 35/35 checks passed, 0 [FAIL], exit 0
```

ASTRA additionally wrote and ran four independent adversarial probe scripts
whose assertions are ASTRA's own, not the Builder's, driving the real call
sites (`astra_sci2.py`, `astra_econ.py`, `astra_veto.py`, `astra_auth.py`,
`astra_look.py`, `astra_label.py`):

```text
science one-look / cohort / qualification / coordinate / D19   17 of 18 checks
  (the one non-pass was an ASTRA fixture artifact, resolved -- see §5 NCF2)
economic SIZE / costs / Risk / Book replay / Learning          16 of 16 checks
genuine Risk veto (not throttle)                                2 of 2 checks
singular authority + forward-evidence laundering               19 of 19 checks
one-look consumption                                            6 of 6 checks
synthetic evidence labelling                                    2 of 2 checks
```

Every probe set includes an explicit **positive control**, because a guard
that always refuses would pass every negative control vacuously. Both positive
controls hold: `G=12` IS `INFERENCE_ELIGIBLE` (share 0.0833), and a clean
Economic `CONTINUE` DOES book exactly one fill.

## 4. Reproduced blocker (domain A)

### A.1 Three REUSE_AS_IS blobs diverge from the frozen manifest at the audited SHA

`governance/BLUE_ONE_BIG_BUILD_IMPORT_MANIFEST_2026-09-21.md` pins 30
REUSE_AS_IS blobs by SHA. ASTRA re-derived all 30 at the audited HEAD and
against the two pinned source commits. 27 of 30 are byte-identical at both.
Three are not:

```text
path                              manifest/source blob  audited HEAD blob
src/quant/economics/consistency.py eb31c991...           13aaa5b2...   (+133/−0)
src/quant/economics/journal.py     d1584d32...           43ea00a7...   (+29/−2)
src/quant/economics/sizing.py      edfacc26...           89a2cc75...   (+92/−0)
```

Reproduce:

```text
git rev-parse 5c8b5b71:src/quant/economics/sizing.py
  -> 89a2cc755e46d116118715f892148caba2d44142
git rev-parse 35dff27b:src/quant/economics/sizing.py
  -> edfacc26d3c7e56bbee0028a407ffaf67be2cf74   (== manifest §4)
```

### A.2 Why this contradicts the frozen build scope

- Frozen spec §6: "exact pinned Forward/Economic blobs only; **byte-identical
  REUSE_AS_IS imports**; ... no silent semantic edits to imported authorities."
- Manifest §5: "A REUSE_AS_IS file that needs modification **must be
  reclassified explicitly as ADAPT in the Builder handoff before edit**."
- Prestage §5: "any file requiring semantic modification belongs in the
  **explicit ADAPT allowlist**, never silently edited while vendoring."
- The prestage's Expected ADAPT allowlist names `factory/workers.py`,
  `factory/strategies.py`, `desk/desk.py`, `desk/opportunity.py`,
  `learning/store.py`, `paths.py`. It does **not** name `economics/
  consistency.py`, `economics/journal.py` or `economics/sizing.py`. Blue's
  allowlist expected "Economic size composition; post-size/pre-fill
  consistency" to land in `desk/desk.py`, not inside the vendored Economic
  authorities.
- The audited Builder final handoff asserts
  `SELECTIVE_IMPORT_MANIFEST_VERIFIED = TRUE`, "all 30 REUSE_AS_IS files ...
  were vendored byte-identical to their pinned blobs", and "no vendored file
  was touched by M4". The last clause is true of M4 in isolation; the composite
  attestation is **not true at the audited SHA** for 3 of 30 files, which were
  edited by M2/M3. No ADAPT reclassification exists anywhere on the branch.

This is the enumerated blocking category "frozen-spec contradiction"
(prestage §5) and "contradicts the frozen build scope" (mission §5). It is
reproducible by hash alone and does not depend on any semantic judgement.

### A.3 What ASTRA did NOT find — scope of the blocker

ASTRA states plainly, so the bounded repair is not over-scoped: **no integrity
harm was reproduced from these three edits.** Specifically:

- All three diffs are **purely additive** at line level except two lines in
  `journal.py` (`from_verdict` gained an optional `strategy_id` kwarg and
  populates `margin_of_safety`). `git diff --numstat` shows `consistency.py`
  +133/−0 and `sizing.py` +92/−0: **zero** deleted or rewritten lines of
  imported authority logic.
- The additions are exactly the M3 work the frozen spec §7 mandates (the
  post-size/pre-fill check, `FINAL_SIZE = min(...)`), and they **strengthen**
  fail-closed behaviour rather than weakening it.
- The `AssessmentRecord` schema addition does **not** disturb durable identity:
  `assessment_id` is derived by `forward_adapter.assessment_id_for` from the
  evidence-scoped `ForwardEvidenceIdentity`, never from the record.
- No false-positive admission, authority bypass, evidence laundering, double
  Book mutation, replay/conflict corruption or missing provenance was
  reproduced from these edits, or anywhere else in this review.

The edits ARE disclosed, with exact rationale, in `STATE.md` (lines ~712–735)
on the audited branch. The defect is that the frozen, hash-pinned composition
authority and the Builder's final attestation no longer describe the audited
object — the property the freeze exists to give Blue.

## 5. Mandatory attack-domain disposition

```text
A. Selective-import identity ......... BLOCKED  (§4; 27/30 byte-identical,
     3/30 diverge, no ADAPT reclassification; no whole-branch merge; no
     alternate Book/scheduler/execution engine imported)
B. Cohort / one-look authority ....... CLEAN
C. Scientific method qualification ... CLEAN
D. D19 / provenance / coordinate ..... CLEAN
E. Forward evidence laundering ....... CLEAN
F. Research -> Economic -> SHADOW .... CLEAN
G. SIZE / costs / Risk ............... CLEAN
H. Fill / Book singular authority .... CLEAN
I. Learning durability ............... CLEAN
J. End-to-end economics .............. CLEAN
```

**B.** Frozen parameters in `science/effect.py` match the frozen geometry
exactly: `252 / K_target=3 / K_max=4 / gap>=80 / G_MIN=10 / share<=0.10 /
alpha=0.05`. One-look quarantine is enforced at **type level**, stronger than
the Builder's name-based `one_look_signature_proof`: `StructuralEvent` carries
no outcome-bearing field at all, so the stopping path cannot reach `T_j` by
construction. `assemble_form4_effect` reads `outcomes` only after
`INFERENCE_ELIGIBLE` + D19 + qualification + coordinate + receipt + look
authority; every earlier return is a refusal with `point/lower/upper = None`.
Probed with a Mapping that raises on any read: never triggered. Cross-cohort
issuer/corporate merging, the >=80 gap, protocol-hash freeze and the fifth-
cohort refusal all hold at both decision and store level. Registering a
cohort after a structural stop raises `COHORT_ACCRUAL_AFTER_STRUCTURAL_STOP`.

**C.** `qualify_method` defaults to `synthetic_only=True` and
`target_cohort_applicability_supported=False`;
`qualified_for_forward_confirmation` requires all four of numerical pass,
applicability supported, an applicability evidence hash, and NOT synthetic-
only. Setting the caller-facing applicability boolean to `True` by itself does
**not** grant qualification — the method cannot self-authorize. Missing,
failed or wrong-protocol qualification all refuse with
`DEPENDENCE_MODEL_UNSUPPORTED`.

**D.** Missing and non-finite outcomes do not disappear: both refuse with
`D19_INSUFFICIENT_UNRESOLVED_COMPLETIONS` +
`MANDATORY_OUTCOME_MISSING_OR_NONFINITE` and set `d19_complete=False`.
Allocation weights are committed pre-outcome (`commit_reference_allocations`
takes no outcomes). `DELTA_COORDINATE_UNRESOLVED`, `DELTA_COORDINATE_MISMATCH`
and `EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE` remain distinct reason
codes and are never collapsed to a bare `NO_TRADE`.

**E.** `ForwardConfirmationReceipt.valid_for` rejects a consumed receipt
(`evidence_unconsumed=False`), an unproven post-freeze recording, a wrong
sample, a wrong protocol, a non-canonical `source`, and any blank identity
field — 12 of 12 rejection probes hold, with a fully-formed receipt accepted
as the positive control. Identity derivation takes only artifact-carried,
evidence-scoped fields (`artifact, ticket_id, strategy_id, forward_receipt`);
no ledger- or dataset-wide input, so unrelated Forward ledger growth cannot
refresh evidence identity. No caller boolean is accepted in place of the typed
receipt. The confirmatory look is content-addressed and single-use: exact
replay is idempotent, while changed outcomes, sample, qualification or
coordinate each raise `CONFIRMATORY_LOOK_ALREADY_CONSUMED`.

**F.** Research auto-promotion is genuinely removed: `factory/workers.py` no
longer calls `transition("SHADOW", ...)`, and exactly one SHADOW transition
site exists in the whole source tree — `integration/econ_bridge.py:168` —
reached only when the verdict is `CONTINUE` **and** eligibility is
`PORTFOLIO_CONSIDERATION_ELIGIBLE` **and** the strategy is currently
`VALIDATED`. `NO_TRADE`, `KILL` and development-only `CONTINUE` never promote,
and each is recorded as its own durable kind. `AssessmentConflict` propagates
before any lifecycle mutation.

**G.** `FINAL_SIZE = min(economic_margin_notional, desk_lifecycle_cap_notional)`
with `MarginSizingRule.fraction` clamped to `[0, max_fraction]`, so the
lifecycle cap can only reduce, never manufacture, size. Neither cost check can
be skipped: all post-size checks for every symbol resolve **before any**
`ExecutionModel.fill` call, so no partial-pass/partial-fill state exists.
Stale, missing, invalid and entirely-absent ADV all fail closed to `NO_TRADE`
with zero Book mutation. Risk is an independent downstream veto: a genuine
hard veto after Economic `CONTINUE` yields `VETOED`, zero fills, unchanged
cash, and a durable `RISK_VETO` Learning record.

**H.** Exactly one `Ledger`, one `ExecutionModel` and one `CapitalDesk` class
definition exist in the source tree (AST scan over `src/**/*.py`). Every
`apply_fill` call site also sources its fill from `ExecutionModel.fill`;
`economics/opening.py` has no Book-mutating call and no Book import. Operation
identity is deterministic (`opportunity_id:symbol:phase`). Exact replay leaves
`fills=1` and cash unchanged; the applied-operation set survives restart from
disk; a conflicting fill under an already-applied operation id raises
`FillConflict` and leaves the Book unchanged. No second bankroll or ledger.

**I.** `DurableOutcomeStore` rebuilds its processed-id index from the full
append-only record list at load, so durability is independent of any last-200
display window: after 240 later entries plus a restart, replaying an original
id returns `NOOP` with the record count unchanged. A same-id/changed-payload
replay raises `LearningConflict` and leaves the store file **byte-identical**
with the original record unmutated. A later counterfactual takes its own
processed id and links back, leaving the original's digest and payload intact.
`NO_TRADE`, `KILL`, `RISK_VETO`, `INSUFFICIENT` and `BOOKED` are all
first-class durable kinds.

**J.** The negative path (no real Form-4 evidence) fails closed at the
econ_bridge boundary with
`EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE`, zero Book mutation and a
durable record. The synthetic positive path is structurally incapable of
laundering into market evidence: `forward_ok = not synthetic`, so a synthetic
artifact is always labelled `DEVELOPMENT`, carries `synthetic=True` and a
`SYNTHETIC_FIXTURE_DEVELOPMENT_ONLY` reason code — verified empirically on a
resolved synthetic estimate. Q1–Q8 answer or fail closed with explicit reason
codes; Q9–Q12 raw histories persist without overclaim.

## 6. Disclosed deferred limitations — ASTRA disposition

Per mission §5 these are not automatically review defects. ASTRA assessed each
against the blocking test and **none is blocking**:

1. `CapitalDesk._run_strategy`'s inline entry path does not call
   `economic_size.run_lane_entry`. **NOT BLOCKING.** It reduces Learning
   coverage for that legacy path; it creates no false-positive authority, no
   Book mutation and no laundering. The frozen spec's M3/M4 bullets name
   `run_lane_entry`/`run_lane_scheduled_exit`, which are wired and covered.
2. No Clock call site invokes `assess_and_admit` automatically before a Desk
   session. **NOT BLOCKING.** Fail-closed: absent admission, nothing promotes
   to SHADOW and nothing sizes. It defers convenience, not authority.
3. Real positive Form-4 confirmatory evidence is structurally unavailable.
   **NOT BLOCKING — and correct.** The frozen geometry itself names a ~3.6–5.0
   year structural timeline. The refusal is the intended behaviour; note that
   because `qualify_method` yields `synthetic_only=True`, no
   `FORWARD_CONFIRMATION` can be issued today at all. That is maximally
   conservative and is the opposite of a false positive.

## 7. Safety state

```text
TARGET_HOST_TOUCHED = FALSE
GATE_B_STATE_CHANGED = FALSE
P0_RUNTIME_MUTATED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE = 0
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
t0 = NOT_DECLARED
AUDITED_BUILDER_OBJECT_MODIFIED = FALSE
```

This review read the repository, ran the suite and ran ASTRA-authored probes
against temporary directories only. No target host was contacted, no Gate-B
state was moved, no frozen ref was moved, and no capital state exists or was
created.

## 8. Return to Blue — bounded repair routing

Per mission §9, ASTRA returns the exact reproduced defect and nothing more.
The blocker is narrow and admits a small, bounded repair by **one** owner. Two
sufficient remedies (Blue chooses; ASTRA does not implement):

1. **Reclassify and re-attest.** Amend the frozen manifest / ADAPT allowlist to
   carry `economics/{consistency,journal,sizing}.py` as ADAPT with their exact
   new blob SHAs (`13aaa5b2...`, `43ea00a7...`, `89a2cc75...`), and correct the
   Builder handoff's `SELECTIVE_IMPORT_MANIFEST_VERIFIED` attestation to state
   27/30 byte-identical + 3 ADAPT. No code change.
2. **Relocate.** Move the three additive blocks to an allowlisted surface
   (e.g. `desk/`), restoring all 30 vendored blobs to byte-identity.

Remedy 1 is a governance/documentation change; remedy 2 is a code move. Neither
requires reopening the science, the economics or the Book.

No recurring red-team loop is requested. Domains B–J and all eleven mandatory
negative controls are reproduced clean and need not be re-run on the repair;
re-verification should be scoped to import identity and the final attestation.

```text
ASTRA_FIRST_VERTICAL_REVIEW = BLOCKED_REUSE_AS_IS_IMPORT_IDENTITY_DIVERGENCE_NOT_ADAPT_RECLASSIFIED
ASTRA_REVIEW_CYCLES_USED = 1
CONTROL_RETURNED_TO = BLUE
```
