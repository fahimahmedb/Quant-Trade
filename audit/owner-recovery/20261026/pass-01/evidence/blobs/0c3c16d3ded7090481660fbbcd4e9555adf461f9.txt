# CP069 historical diagnostic convergence checkpoint

BRANCH_CLASSIFICATION: HISTORICAL_DIAGNOSTIC_CONVERGENCE
BASE_STATUS: NOT_A_WAVE2_BASE

This checkpoint closes only the trial-accounting lineage defect investigated during the interrupted CP069 convergence. It is not a continuation of full Wave-2 convergence, and it does not declare an immutable Wave-2 base.

## Exact defect

CP069 already binds the frozen candidate identity (`candidate.hypothesis_id`, `candidate.generation_id`) through the frozen protocol/candidate binding. However, the legacy `trial_accounting` contract is numeric-only. Factory-style enriched trial accounting introduces `hypothesis_id` and `generation_id` on that additional surface. Without an explicit equality invariant, enriched trial-accounting lineage could diverge from the frozen candidate while the legacy numeric accounting checks still pass.

This is a convergence-interface defect: legacy CP069 packages that do not carry lineage in `trial_accounting` are not themselves malformed.

## Root cause

The original trial-accounting validator was designed before lineage fields existed on `trial_accounting`. It validated observed-attempt/effective-trial numeric coherence but had no contract tying later optional lineage fields back to the already-frozen candidate identity.

## Repair

`research/research_os/expansion/validation_v2.py` now applies a compatibility-preserving lineage invariant at the canonical `validator_economic_readiness_v3` boundary:

- legacy accounting with neither lineage key remains governed by the existing CP069 validator;
- if either `hypothesis_id` or `generation_id` appears in `trial_accounting`, both are required;
- both identifiers must be non-empty strings;
- both must exactly equal the frozen candidate identifiers;
- mismatch fails closed through the existing `trial_accounting` check / `TRIAL_ACCOUNTING_INVALID` reason and cannot produce READY status.

No Factory registry, geometry, power, firewall, Economic lifecycle, or MEGA A implementation was imported by this repair.

## Affected files and contracts

Functional repair:
- `research/research_os/expansion/validation_v2.py`

Regression proof:
- `tests/test_trial_accounting_identity_binding.py`

Semantic contract affected:
- `readiness_bundle.candidate.{hypothesis_id,generation_id}`
- optional/enriched `readiness_bundle.trial_accounting.{hypothesis_id,generation_id}`
- canonical `validator_economic_readiness_v3` fail-closed disposition

The pre-existing CP069 core `validation_readiness.py` contract remains unchanged in this historical branch.

## Tests / falsification cases

The regression test covers:

1. legacy numeric accounting without lineage remains compatible;
2. enriched accounting with matching lineage is accepted by the new invariant;
3. mismatched lineage is rejected;
4. partial lineage (only one identifier) is rejected;
5. the canonical validator converts a would-be READY core receipt to BLOCK on lineage drift with `TRIAL_ACCOUNTING_INVALID`.

The test is placed in `tests/` so the repository's `SEC P0 pre-t0 gate` full-unit discovery executes it on push.

Code/test checkpoint immediately before this documentation commit:
`ddc6cea5715b544f47faa9524d1888b9c4577e33`

## CP079 applicability

Likely applicable: YES, specifically when CP079 convergence introduces Factory-style enriched trial accounting.

Observed CP079 reference during diagnosis:
`builder/convergence-cp079-wave2-base-20261021`
head observed: `cf593275e41d21435ac308a144570e1451148815`

Its readiness semantics still preserve the same split: frozen candidate identity is bound, while the legacy trial-accounting surface remains numeric-only. Therefore a later enrichment of that surface should reuse the identity invariant rather than introduce an unbound second lineage identity.

## Semantic changes to reuse in a CP079 convergence

- bind trial-accounting `hypothesis_id` and `generation_id` to the frozen candidate identity;
- fail closed on mismatch or partial enriched identity;
- preserve legacy compatibility only for the migration interval where lineage fields are genuinely optional;
- once enriched trial accounting is native in CP079, prefer making both identity fields mandatory in the core readiness contract rather than retaining a transitional wrapper-only rule;
- preserve CP079 frozen-input, PIT, protocol-hash, source, and outcome-firewall protections; do not replace or weaken them;
- keep the existing authorization semantics unchanged: identity validation grants no execution, outcome, prospective-observation, live-trading, or real-capital authority;
- retain regression cases for legacy transition, exact match, mismatch, and partial identity.

## Stop boundary

No further Factory integration was performed after closure of this defect. No Economic or MEGA A work was integrated. This branch is retained only as historical diagnostic convergence evidence and must not be selected as a Wave-2 base.
