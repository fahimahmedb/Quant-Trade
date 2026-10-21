# WAVE 2 C2 — D0 SEALED-BASE REBIND RECIPE — 2026-10-21

Status: `PRE_CONVERGENCE_RECIPE`
Role: foreman diagnostic/integration preparation only.
Not a sibling override. Not a canonical integration commit. Not a new D0 FINAL.

## Source evidence

D0 source branch:

`builder/mega-d0-economic-lifecycle-20261021`

Observed closure head:

`4262462e0c853d917f32e8f87c2423f93a313167`

D0 code+test exact-head qualified source:

`84aa0f5ff74a701130c3a8a1cc5ef7c52e197db0`

D0 source FINAL run:

`39623589944` -> `SUCCESS`

Historical D0 source base:

`97165db2faa3300cef1f23de0045ed93d25eb9cb`

Canonical sealed Wave2 base:

`2b99d8aeb8a342f1ef32544247d366cb8a26037e`

## Why a rebinding is required

D0 does not merely have old ancestry. Its kernel embeds the historical base as data/identity law:

```python
WAVE2_IMMUTABLE_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"
```

That constant is copied into and validated by:

- `EconomicIdentityRef.wave2_base_sha`;
- `PortfolioReadinessRef.wave2_base_sha`;
- shadow/lifecycle contract identity material;
- hashes derived from those records.

Therefore the D0 source FINAL is internally coherent but cannot be copied unchanged into canonical Wave2 Convergence #2 after the immutable base was sealed at `2b99d8ae…`.

## Required canonical-port code delta

Exactly this semantic pin must change in the D0 kernel when ported:

```diff
-WAVE2_IMMUTABLE_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"
+WAVE2_IMMUTABLE_BASE_SHA = "2b99d8aeb8a342f1ef32544247d366cb8a26037e"
```

Path:

`research/research_os/expansion/economic_lifecycle.py`

No W1 ECON algorithm, fingerprint, structural-overlap law, wrapper-equivalence rule, portfolio-readiness rule, outcome membrane or lifecycle transition semantics should change for this rebinding.

## Derived-identity consequence

Changing the immutable-base pin is expected to change deterministic hashes for newly generated D0 refs/contracts because the sealed base is part of their identity material.

This is **required**, not a regression.

Do not preserve old generated hashes by removing the base from the hash envelope or by weakening validation.

Historical D0 source artifacts remain historical evidence bound to `97165db2…`; canonical Convergence #2 must generate fresh fixture refs/contracts under `2b99d8ae…`.

## Test behavior

The canonical D0 test module imports `WAVE2_IMMUTABLE_BASE_SHA` from the kernel rather than hardcoding the old value in the observed fixtures. The focused contract tests should therefore naturally exercise the new base pin after the one-line kernel change.

Required focused rerun:

```text
tests/test_mega_d0_economic_lifecycle.py
```

Source FINAL proved `33/33 PASS`; the canonical port must re-establish the same suite semantics on the sealed base.

## Qualification workflow caveat

The sibling workflow `.github/workflows/mega-d0-exact-head-qualification.yml` is source-lane evidence and must not be copied blindly as canonical port law.

It currently contains:

```text
WAVE2_IMMUTABLE_BASE_SHA=97165db2...
MEGA_D0_FIRST_CHECKPOINT_SHA=e9268c89...
```

and proves:

```text
parent(MEGA_D0_FIRST_CHECKPOINT_SHA) == WAVE2_IMMUTABLE_BASE_SHA
```

That assertion is historically correct for the D0 source lane and becomes intentionally false after semantic porting to the finally sealed base.

### Canonical port qualification must instead prove

1. exact canonical integration candidate descends from `2b99d8ae…`;
2. D0 source delta provenance points to qualified source head `84aa0f5f…` / closure head `4262462e…`;
3. D0 kernel contains `WAVE2_IMMUTABLE_BASE_SHA=2b99d8ae…`;
4. focused D0 suite passes;
5. W1 ECON differential/non-regression is preserved relative to `2b99d8ae…`;
6. D0 did not mutate W1 ECON-owned implementation surfaces;
7. all authority/outcome flags remain closed;
8. no scheduler/runtime ownership is introduced;
9. exact integrated working tree is clean before seal.

Do not rewrite the historical D0 CP/FINAL documents to pretend that the original lane started from `2b99d8ae…`. Preserve them as source evidence and emit a separate canonical port receipt/manifest.

## W1 ECON differential note

The finally sealed base already contains the pinned immutable Legacy ledger and the corrected ECON assertions. A canonical D0 port should compare W1 ECON behavior against `2b99d8ae…`, not against `97165db2…`.

The base-repair files are upstream baseline law at that point and must not be classified as D0-owned changes.

## Expected conflict class

`BASE_BINDING_CONFLICT`

`TEXTUAL_CONFLICT_WITH_BASE_REPAIR=FALSE`

`SEMANTIC_REBIND_REQUIRED=TRUE`

`W1_ECON_REDESIGN_REQUIRED=FALSE`

`D0_LIFECYCLE_REDESIGN_REQUIRED=FALSE`

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`

`REAL_CAPITAL_AUTHORIZED=FALSE`

`LIVE_TRADING_AUTHORIZED=FALSE`

`OUTCOME_ACCESSED=FALSE`
