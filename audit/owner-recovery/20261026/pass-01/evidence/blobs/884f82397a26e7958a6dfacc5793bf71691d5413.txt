# WAVE 2 CONVERGENCE #2 — C0 ACCEPTANCE PACK

Date: 2026-10-21
Owner role: Integration Foreman / pre-convergence accelerator
Status: PRE-CONVERGENCE CONTRACT — NOT A C0 IMPLEMENTATION

## Immutable anchors

- `WAVE2_IMMUTABLE_BASE_SHA=2b99d8aeb8a342f1ef32544247d366cb8a26037e`
- qualified MEGA B source: `7ef088bb30ece88cf96f4514e8c581a95ca4b091`
- qualified D0 source code/test head: `84aa0f5ff74a701130c3a8a1cc5ef7c52e197db0`
- qualified E source: `2d5ff9d3d629affc720b706405fc093d0ae81548`

This pack does **not** emit `WAVE2_INTEGRATED_SHA`, does not seal Wave 2, and does not modify the C0 sibling branch.

## Foreman finding: C0 is an extraction/reuse problem, not a green-field Validator

The sealed Wave-2 base already contains the qualified scientific primitives C0 needs:

- Factory freeze / experiment identity / deterministic replay / pre-outcome receipt in `experiment_infrastructure`, `experiment_runner`, and `final_shape`;
- independent Validator entry point `validator_economic_readiness_v3` in `expansion/validation_v2.py`, backed by `validation_readiness.py`;
- Red Team negative-rights engine `red_team_negative_rights_v2` in `expansion/red_team_v2.py`;
- W1 Economic composition in `expansion/economic_test_readiness_v1.py` already calls both Validator and Red Team.

Therefore C0 MUST NOT build a second experiment registry, second freeze mechanism, second trial-accounting model, second Validator, or second Red Team.

The canonical convergence problem is instead:

`B Candidate + discovery binding`
→ `Factory exact frozen candidate/protocol/source/code identity`
→ `C0 independent scientific adjudication using existing Validator + Red Team law`
→ `W1 ECON structural/economic-identity boundary`
→ `D0 lifecycle refs`

The final convergence must remove/avoid double-adjudication semantics. W1 ECON may continue to verify a C0 receipt or call a shared primitive, but C0 and W1 ECON must not independently manufacture divergent scientific truth.

## Upstream seam: MEGA B law

C0 accepts only a B handoff that is already `READY_FOR_FACTORY` / `EXPERIMENT_READY_HANDOFF` and whose bindings validate exactly.

B explicitly guarantees at handoff:

- canonical Candidate is preserved and additively enriched under `candidate.discovery`;
- discovery binding is tamper-evident;
- `validator_invoked=false`;
- `red_team_invoked=false`;
- `experiment_frozen=false`;
- `scheduler_mutation=false`;
- `outcome_accessed=false`;
- all authority flags remain false.

C0 MUST NOT reinterpret a B `BLOCKED_DISCOVERY` result as admissible.

## Factory seam: exact identity, no outcome creation

C0 must consume the existing frozen experiment identity. At minimum, the adjudicated scientific subject is bound to:

- `hypothesis_id`;
- `generation_id`;
- canonical `candidate_hash`;
- `protocol_hash` and `frozen_protocol_hash`;
- source snapshot / source route / PIT bindings;
- code + environment binding;
- trial-accounting binding;
- experiment registry identity;
- deterministic pre-outcome plan / receipt / replay identity.

A material Candidate change after freeze MUST NOT reuse the old scientific disposition. It requires a new generation / new frozen binding or blocks fail-closed.

C0 must preserve the canonical outcome firewall. A C0 qualification cannot be obtained by opening, inferring, back-filling, simulating as observed, or optimizing against an economic outcome.

## Independent adjudication law

C0 must reuse the existing Validator law rather than self-certify producer output.

Required properties:

1. producer identity differs from validator identity;
2. candidate and frozen protocol are hash-bound and immutable during evaluation;
3. source provenance, PIT, clocks, revision policy and survivorship policy are checked;
4. implementability blockers cannot be overridden by scientific prose;
5. multiplicity and trial accounting remain explicit, with UNKNOWN preserved when unknown;
6. falsification scope and decision map remain preregistered inputs;
7. experiment infrastructure is exactly bound to registry / frozen protocol / runner plan / receipt / replay / geometry / power;
8. candidate mutation, protocol mutation, source mutation, code/environment mutation or receipt tampering block;
9. no outcome access is opened.

Red Team is negative-rights only. It may block; it may not repair, retune, optimize parameters, mutate the Candidate, or iterate until profitable.

## Scientific disposition boundary

The C0 result may express only scientific disposition / blockers / uncertainty / provenance for the exact frozen subject. It MUST NOT itself grant:

- economic experiment authority;
- prospective observation authority;
- capital authority;
- live trading authority;
- operational scheduler admission;
- queue/task leases;
- a Control Plane capability;
- a `ResearchTask READY` state.

Scientific readiness and operational readiness are different namespaces and different authorities.

## Downstream W1 ECON seam

The W1 Economic boundary remains upstream law for economic identity and structural portfolio readiness. C0 MUST NOT rebuild or bypass:

- 12-dimension economic fingerprint;
- candidate→economic identity binding;
- KNOWN / UNKNOWN / NOT_APPLICABLE / CONFLICTED semantics;
- structural overlap and same-exposure review;
- wrapper-equivalence law;
- portfolio readiness.

A favorable C0 scientific disposition is therefore necessary but not sufficient for downstream W1 ECON readiness.

The final adapter should bind the exact C0 disposition to the same candidate/protocol/trial identity consumed by W1 ECON. Any mismatch blocks.

D0 remains strictly downstream of W1 ECON and consumes `EconomicIdentityRef + PortfolioReadinessRef`; C0 must never emit D0 lifecycle state directly.

## Fail-closed acceptance cases

The machine-readable matrix in `handoff/fixtures/WAVE2_C0_ACCEPTANCE_MATRIX.v1.json` is normative for pre-convergence acceptance intent. C0 must demonstrate, with deterministic fixtures, at least:

- valid pre-outcome exact binding can receive a scientific PASS disposition without opening authority;
- producer self-validation blocks;
- post-freeze Candidate mutation blocks / requires new generation;
- protocol/source/PIT/code binding mutation blocks;
- outcome-bearing input blocks;
- Red Team leakage/clock/PIT/data objections block without repair;
- unresolved identity/timing/source ambiguity is not converted to a favorable disposition;
- missing multiplicity/trial accounting blocks or preserves explicit UNKNOWN as applicable;
- scientific PASS cannot become scheduler/Control Plane `READY`;
- downstream W1 ECON still has independent structural/economic-identity veto power.

## Qualification evidence required before canonical Convergence #2

C0 is acceptable for canonical integration only after all of the following exist on one exact C0 head:

- exact base ancestry from `2b99d8aeb8a342f1ef32544247d366cb8a26037e`;
- focused C0 acceptance suite green;
- Factory regression green;
- W1 Economic integration/regression green;
- outcome-firewall tests green;
- candidate/protocol/source/code tamper tests green;
- independent-validator test green;
- Red Team negative-rights tests green;
- authority flags all false;
- `OUTCOME_ACCESSED=FALSE`;
- exact-head workflow receipt naming the tested SHA.

Until that evidence exists:

`READY_FOR_CANONICAL_CONVERGENCE2=FALSE`

`WAVE2_INTEGRATED_SHA=NOT_AUTHORIZED_TO_EMIT`
