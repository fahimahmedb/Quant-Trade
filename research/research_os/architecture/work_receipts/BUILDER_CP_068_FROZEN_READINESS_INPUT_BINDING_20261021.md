# CP068 — Frozen input to independent readiness binding

Implements CP067's reproduced immutable-intent gap in existing interfaces. The
independent Validator reconstructs source manifest/snapshot/PIT joins and the
clock, universe, expression, costs, capacity, multiplicity and trial projections
from the envelope's frozen sources/protocol. Missing or different projections
produce FROZEN_INPUT_BINDING_FAILED. Qualifies routes independently through the
existing route qualifier; row order is not artificial evidence of difference.

The actual implementability declaration is included by this readiness path in
the existing protocol payload and its hash. Other envelope callers that omit
this optional declaration retain their existing payload/hash behavior. The
independent projection verifies the declaration's exact frozen hash/status.
No second freeze store or separate authority is introduced.

Full frozen candidate/body/ID/decision-map equality is checked too: a caller may
not replace a candidate and add a new explicit candidate_hash header over an old
hashed payload. Header/hash rebindings alone are not proof of immutable intent.
Declared entry/exit/universe maps also remain consistent within the frozen body.

Six new tests use real composed synthetic metadata and the real Validator.
Mutations of candidate, clock, universe, expression, implementation, costs,
capacity, multiplicity, trials and source/PIT projections independently rebind
their local hashes where relevant. All other scientific checks, including
protocol_freeze and reproducibility_binding, remain PASS; the new frozen-input
check alone blocks the changed intent. Missing declarations, explicit aliases,
PIT row order and optional envelope copy semantics are covered. No actual data
or economic experiment. 34 affected tests and broader Research OS 268 PASS;
configured root 784 PASS. Exact-source workflow follows the implementation commit.

Direct synthetic fixtures now declare complete frozen sources/protocol/
implementation and recompute their ordinary hashes. Positive multi-source/alias
fixtures add sources to the frozen body too; no valid-source guard is weakened.
The structured-rule positive case freezes the rule before expecting READY;
projection-only mutation explicitly remains BLOCK.
Old persisted receipts and scientific outcomes are not rewritten. Source SHA
versions the strengthened admission contract; no active Oracle epoch/policy or
runtime is silently changed. Four authorities remain FALSE.

The Owner-skipped network/configuration/deployment task remains excluded. Continue
qualification and reassessment of independent pre-outcome work. No Site/API
probe, configuration save, VM action, or higher-authority activation in this work.
