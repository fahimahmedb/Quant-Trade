# W1 ECON — Integration Manifest — 2026-10-21

MODULE: ECONOMIC IDENTITY → STRUCTURAL PORTFOLIO MAP / PORTFOLIO READINESS
MODE: PRE-OUTCOME ONLY
BASE_SHA: fecd09e0839f1208d9f876c311331221bde3ab7d
CODE_QUALIFIED_HEAD_SHA: 73f99bf7ec504b217463f5435700887994e5ec5f
AUTHORITATIVE_NORTH_STAR_BLOB: a328b4e6d7d71dafd532938888ebf9818b1b610f
BRANCH: builder/w1-economic-portfolio-depth-20261021

## Integration intent

Integrate one hardened structural-economic identity / portfolio-readiness capability without creating a second truth store, second portfolio engine, empirical outcome path, Scientific Memory implementation, or trading authority surface.

## Code delta relative to mandatory base

The code-qualified head is 16 commits ahead and 0 behind the mandatory base. Code delta is limited to six files:

1. `research/research_os/expansion/final_shape.py` — modified
2. `research/research_os/expansion/portfolio_v2.py` — modified
3. `research/research_os/tests/test_economic_identity_memory_context_w1.py` — added
4. `research/research_os/tests/test_economic_identity_portfolio_depth_w1.py` — added
5. `research/research_os/tests/test_economic_identity_portfolio_frontier_w1.py` — added
6. `tests/test_research_os_structural_unknown_evidence.py` — modified

GitHub compare at the code-qualified head reports: 16 commits ahead, 0 behind; `final_shape.py` +48/-34, `portfolio_v2.py` +497/-159, memory tests +70, depth tests +258, frontier tests +109, root regression bridge +22/-2.

## Canonical ownership after integration

- Economic identity production: `economic_identity_v1` in `final_shape.py`, with exact candidate binding and provenance.
- Canonical structural identity / pair / portfolio diagnostics: `portfolio_v2.py`.
- Legacy V1 portfolio entry point: compatibility facade only; delegates to canonical V2 diagnostics.
- Broader economic test readiness: existing `economic_test_readiness_v1.py`, which imports and composes the canonical V2 portfolio surfaces.
- V2 independence: process/retrieval/provenance independence only; it is not a portfolio-diversification claim.
- Scientific Memory: not owned by this lane; only opaque non-empirical references may be consumed when supplied.

## Public contract changes

Structural outputs now expose richer deterministic semantics, including:
- canonical field-state handling (`KNOWN`, `UNKNOWN`, `NOT_APPLICABLE`, `CONFLICTED`);
- exact candidate binding status;
- field-by-field structural relations and named relationship signals;
- diagnostic overlap intervals that are explicitly non-empirical;
- portfolio mapping/readiness blockers and sealed empirical requirements;
- lateral memory context that is excluded from fingerprints and empirical inference.

Existing legacy summary compatibility is retained. Golden hashes were deliberately re-anchored only after the intended deterministic contract changed and the broader suite showed no other regression.

## Expected integration conflicts

Highest-probability conflicts are textual/semantic, not architectural:

1. `research/research_os/expansion/portfolio_v2.py`
   - Any parallel lane editing structural fingerprint fields, pair classifications, readiness blockers or deterministic output shape can conflict.
   - Resolution rule: preserve explicit UNKNOWN/CONFLICTED semantics, exact binding, and the prohibition on empirical inference.

2. `research/research_os/expansion/final_shape.py`
   - Any parallel lane editing `economic_identity_v1` or `portfolio_map_v1` can conflict.
   - Resolution rule: retain producer candidate binding and keep `portfolio_map_v1` as a facade over the canonical V2 engine; do not resurrect independent portfolio logic.

3. `tests/test_research_os_structural_unknown_evidence.py`
   - Golden-hash or bridge edits can conflict if another lane intentionally changes the same deterministic public outputs.
   - Resolution rule: recompute/accept a new golden only after semantic review and a broad test run; never update a golden merely to silence an unexplained regression.

Dedicated W1 test files should have low merge-conflict probability.

## Integration order

1. Reacquire mandatory base / convergence target and verify North Star identity.
2. Inspect semantic delta before resolving any conflicts; do not blindly favor either side.
3. Preserve canonical V2 ownership and V1 facade delegation.
4. Preserve candidate hash/generation/hypothesis binding.
5. Preserve UNKNOWN / NOT_APPLICABLE / CONFLICTED distinctions and non-finite/bool rejection.
6. Preserve memory references outside the structural fingerprint.
7. Preserve empirical layer sealing and all authority flags false.
8. Re-run focused W1 ECON adversarial tests.
9. Re-run the repository broad CI / SEC P0 gate at the exact integration head.
10. Re-anchor deterministic goldens only if an intended reviewed semantic delta requires it.

## No-build / reuse decisions

- No second portfolio engine.
- No duplicate validator.
- No empirical correlation/covariance/alpha engine.
- No capital allocation/sizing/trading engine.
- No Scientific Memory provider implementation in this lane.
- No duplicate literal `outcome_accessed` field added to portfolio V2: the readiness composition boundary already exposes `outcome_accessed=False`, while portfolio V2 independently proves no return-series consumption and a sealed empirical layer.
- Existing candidate/export outcome firewall and exact validator binding are reused rather than duplicated.

## External dependencies / future empirical facts

The structural module remains intentionally unable to establish empirical portfolio behavior. Future empirical qualification requires, under separate authority and protocol:
- ADMISSIBLE_RETURN_SERIES_WITH_PROVENANCE
- FROZEN_EMPIRICAL_PORTFOLIO_PROTOCOL
- AUTHORIZED_OUTCOME_ACCESS
- OBSERVED_COST_AND_CAPACITY_INPUTS_WHERE_REQUIRED

These are dependencies, not permissions.

## Scientific integration limit

Safe integration means the repository gains a stronger pre-outcome structural map and readiness gate. It does not mean any pair is empirically independent, any portfolio is diversified, any edge exists, capacity is realized, costs are observed, capital may be allocated, or trading may begin.

## Authority invariant

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESSED: FALSE

INTEGRATION_MANIFEST_STATUS: COMPLETE
