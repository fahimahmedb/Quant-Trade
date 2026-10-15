# Quant-Trade — Aggressive Architecture Attack

Status: BUILD / ISOLATED BRANCH

Base production-research branch: `builder/research-os-autonomous-loop-20261015`
Base SHA: `fda8345f23ec363f8b98632ecb566c5d0bbaff53`

## Governing rule

**Final interfaces early, sophistication later.**

The six canonical shared contracts remain stable:

1. HypothesisContract
2. ResearchTask
3. ExperimentResult
4. EvidenceAssessment
5. CandidateEconomicIdentity
6. WorkerEvent

`WorkerReceipt` remains the durable execution receipt companion.

This branch does not redesign those contracts. It builds the remaining final-shape modules around them.

## Parallel build fronts

### Front A — Engine depth

- Quant / Mechanisms
- Event / Documents
- Fundamental
- Institutional / Forced Flows
- Edge Archaeology

All producers converge to the same frozen CandidateHypothesis/HypothesisContract path.

### Front B — Early Implementability

Before expensive experiment work, assess:

- source availability
- point-in-time feasibility
- expression feasibility
- liquidity / capacity observability
- cost-model feasibility
- operational complexity
- blockers and reopen conditions

Implementability may PARK/BLOCK expensive work, but does not rewrite scientific truth or kill a mechanism solely because implementation is inconvenient.

### Front C — Experiment Infrastructure

Common deterministic experiment envelope for:

- protocol hash
- dataset provenance
- code/reproducibility hash
- cost-model version
- observed attempts
- effective-trials status
- immutable result reference

No economic outcome is opened by this architecture build.

### Front D — Independent Validation / Red Team

Validator and Red Team remain producer-independent. Red Team has negative rights only: block/restrict claims for data, leakage, multiplicity, costs, capacity, claim level or governance violations.

### Front E — Economic Identity / Portfolio Map

Every surviving candidate receives an economic identity and overlap map before any future allocation layer. Portfolio v1 may reason about shared exposures and marginal diversification information, but has no capital or order authority.

### Front F — Forward Farm

Forward Farm manages immutable prospective contract generations:

`G_n frozen -> authorized future observation -> assessment`

Any material change creates `G_n+1`. No result-driven mutation can continue inside the same generation.

For this build:

`PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`

Therefore the farm may register/readiness-check contracts only; it may not ingest future outcomes.

### Front G — Decay / Learning

Decay consumes only admissible prospective evidence. With prospective authority off, it remains inactive by authority.

Learning telemetry may consume process facts, blockers, KILL/PARK paths, validation failures and trial-accounting facts. It must not invent effective trials or infer economic edge from workflow productivity.

## Required vertical proof

A deterministic synthetic candidate set must traverse:

```text
Engine producer
 -> Legacy/duplication screen
 -> Early Implementability
 -> frozen experiment envelope
 -> Independent Validator
 -> Red Team
 -> Economic Identity
 -> Portfolio Map
 -> Forward readiness registration
 -> Decay authority guard
 -> Learning telemetry
 -> WorkerEvents / receipts
```

Acceptance conditions:

- canonical shared interfaces unchanged
- no self-validation
- immutable generation semantics preserved
- no real outcomes consumed
- no prospective observations consumed
- no capital allocation or orders
- deterministic replay
- all stages persist explicit status and blockers
- Live Lab compatible events remain derivable

## Authority invariants

```text
PRODUCTION_RESEARCH_WORKERS = TRUE on the production-research branch
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
```

This isolated build branch must not change the production worker schedules.