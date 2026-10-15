# Quant-Trade Research OS — Final-Shape Gap Audit

Date: 2026-10-15
Branch: `builder/research-os-aggressive-architecture-20261015`
Rule: **FINAL INTERFACES EARLY, SOPHISTICATION LATER**

## Audit verdict

The architecture does **not** need another deep subsystem before final-shape closure.

All major target modules already exist. The remaining architectural gap is the **canonical integration spine**: the inherited Control Plane / task state, Legacy gate, research stages, persistence, WorkerEvents/receipts and Live Lab need to be proven as one ordered vertical slice.

## Classification

| Target block | State | Audit conclusion |
|---|---|---|
| Owner / Governance | THIN_EXISTS | Authority flags exist, but governance/control state is not yet persisted as the first-class opening snapshot of the aggressive vertical slice. |
| Canonical Research Core | EXISTS | Shared contracts, scientific/trial ledgers and immutable generation semantics exist. Do not redesign. |
| Control Plane | EXISTS_NOT_IN_AGGRESSIVE_SLICE | Production workflow model/capabilities exist, but the aggressive architecture proof does not begin from a Control Plane snapshot / task contract. |
| Task / Lease state | EXISTS_NOT_IN_AGGRESSIVE_SLICE | Proven in autonomous-loop work, but not bound into the final aggressive vertical proof. |
| Legacy / Recovery / anti-restart | EXISTS_ORDERING_GAP | Legacy is loaded and persisted, but `build_persistent_final_shape()` screens candidates only after the aggressive scientific run has already traversed implementability/experiment/validation. Canonical target requires Legacy/duplication gate before expensive downstream work. |
| Quant / Mechanisms | THIN_EXISTS | Correct for current phase. |
| Event / Documents | THIN_EXISTS | Correct for current phase. |
| Fundamental | THIN_EXISTS | Correct for current phase. |
| Institutional / Forced Flows | THIN_EXISTS | Correct for current phase. |
| Edge Archaeology | THIN_EXISTS | Correct for current phase. |
| Early Implementability | EXISTS | Ordered correctly after candidate production, but must receive only Legacy-admissible candidates in the canonical spine. |
| Experiment Infrastructure | EXISTS_NO_OUTCOME | Correct authority boundary. |
| Independent Validator | THIN_EXISTS | Correct producer-independence boundary. |
| Red Team | THIN_EXISTS | Negative rights only; correct shape. |
| Economic Identity | EXISTS_EVENT_GAP | Identity exists and is persisted, but does not currently emit its own first-class WorkerEvent/receipt stage. |
| Portfolio Map | EXISTS_NO_CAPITAL | Correct shape. |
| Shadow / Forward | EXISTS_READINESS_ONLY | Correct while prospective authority is off. |
| Decay Monitoring | EXISTS_INACTIVE_BY_AUTHORITY | Correct while no admissible prospective evidence exists. |
| Learning Telemetry | EXISTS_PROCESS_ONLY | Correct shape. |
| Scientific / Trial persistence | EXISTS | Persistent wrapper is hash-chained and immutable. |
| WorkerEvents / receipts | PARTIAL_COVERAGE | Engine, implementability, experiment, validator, Red Team and aggregate stages emit; Control/Governance, Legacy screen and Economic Identity need explicit stage facts. |
| Live Lab bridge | EXISTS | Native event mapping exists; observability only. |

## Overbuilt / defer

Wave 3 engine dossiers and Wave 4 acquisition/PIT-firewall work are useful future depth, but are **not on the current critical path to final-shape closure**.

Do not delete them. Do not expand them further now.

Classify them as:

`BUILT_EARLY / DEFER_FURTHER_DEPTH`

## Critical architectural defects to close now

1. **Legacy ordering**

Current aggressive path effectively proves:

`candidate -> implementability -> experiment freeze -> validator -> red team -> ... -> persistence wrapper -> legacy screen`

The canonical path must prove:

`candidate -> legacy/duplication gate -> implementability -> experiment freeze -> validator -> red team -> ...`

An exact legacy duplicate must not reach experiment/validation/portfolio/forward stages.

2. **Control Plane / Task boundary absent from the aggressive vertical slice**

The final slice must begin with a durable control/task snapshot proving:

- current authority,
- workflow/capability routing,
- one bounded lineage,
- task identity / required capability,
- lease generation / claim state,
- no work invention.

This may be a deterministic synthetic task/lease representation; it must use the stable ResearchTask semantics and must not modify production schedules.

3. **Incomplete stage observability**

Add first-class WorkerEvent/receipt facts for:

- `CONTROL_PLANE_SNAPSHOT`
- `TASK_CLAIM`
- `LEGACY_SCREEN`
- `ECONOMIC_IDENTITY`
- final canonical persistence / handoff

No event may fabricate economic progress.

4. **One proof instead of stacked independent proofs**

The final gate must execute one canonical spine and assert the complete ordering, persistence, authority and observability invariants in one run.

## Canonical spine to build

```text
OWNER / GOVERNANCE SNAPSHOT
        ↓
CONTROL PLANE
        ↓
RESEARCH TASK + CLAIM / LEASE
        ↓
PRODUCER ENGINE
        ↓
LEGACY / DUPLICATION GATE
        ↓
EDGE ARCHAEOLOGY / NEGATIVE KNOWLEDGE CONTEXT
        ↓
EARLY IMPLEMENTABILITY
        ↓
EXPERIMENT ENVELOPE FREEZE
        ↓
INDEPENDENT VALIDATOR
        ↓
RED TEAM
        ↓
ECONOMIC IDENTITY
        ↓
PORTFOLIO MAP
        ↓
FORWARD READINESS
        ↓
DECAY AUTHORITY GUARD
        ↓
LEARNING TELEMETRY
        ↓
SCIENTIFIC + TRIAL LEDGER
        ↓
WORKER EVENTS + RECEIPTS
        ↓
LIVE LAB BRIDGE
```

## Acceptance gate

Final-shape closure requires all of the following in one deterministic exact-HEAD CI run:

- shared contracts unchanged;
- Control Plane valid;
- one lineage / bounded task semantics represented;
- Legacy screen occurs before downstream expensive stages;
- exact duplicate is blocked before experiment envelope / validation / portfolio / forward;
- no self-validation;
- Scientific Ledger verifies;
- Trial Ledger keeps effective trials UNKNOWN where unknown;
- each canonical stage has explicit status and receipt/event coverage;
- no economic outcome opened;
- no prospective observation started;
- no real capital;
- no live trading;
- deterministic replay byte/fingerprint stable;
- existing Live Lab native mapper remains compatible.

## Decision

`NEXT_BUILD = CANONICAL_INTEGRATION_SPINE_ONLY`

`NO_NEW_DEEP_SUBSYSTEMS_UNTIL_SPINE_PASS = TRUE`
