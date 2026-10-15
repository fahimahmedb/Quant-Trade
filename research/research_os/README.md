# Quant-Trade Research OS — Autonomous Loop Backbone

Status: isolated build spike
Branch: `builder/research-os-autonomous-loop-20261015`
Base: `fdfee2006869ff3770f752f32fb672da0b0fc4ac`

## Purpose

Build the thinnest final-shape backbone that can support:

1. a canonical scientific ledger;
2. a task/lease control plane;
3. scheduled ChatGPT/Codex workers;
4. durable receipts and provenance;
5. real worker events consumable by the existing Live Lab native adapter.

This is infrastructure only. It does not authorize or run economic experiments.

## Invariants

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
```

No worker may infer additional authority from a task.

## Frozen thin interfaces

The backbone freezes only common contracts, not the full future implementation:

- `HypothesisContract`
- `ResearchTask`
- `ExperimentResult`
- `EvidenceAssessment`
- `CandidateEconomicIdentity`
- `WorkerEvent`
- `WorkerReceipt`

These contracts are intentionally small so Quant, Fundamental, Event/Document, Flows, Validation and future workers can be developed in parallel without sharing conversation memory.

## Canonical worker cycle

```text
WAKE
  -> read fresh branch HEAD / task ledger
  -> find one admissible READY task
  -> atomically claim with lease generation
  -> emit ACTION_STARTED
  -> execute only allowed bounded actions
  -> persist artifacts / evidence
  -> persist WorkerReceipt
  -> emit ACTION_COMPLETED or SESSION_ENDED
  -> update task terminal state
  -> STOP
```

A conversation is a replaceable worker, never the canonical memory.

## Source of truth

Canonical state lives in GitHub artifacts/contracts/receipts and, later, the Scientific Ledger. A worker must be able to reconstruct all required context from durable state on every wake.

## First vertical slice

`AUTONOMY-CANARY-001` is deliberately non-economic. Its only job is to prove:

```text
scheduled worker
-> fresh state read
-> lease claim
-> bounded action
-> durable receipt
-> native-shaped worker events
-> Live Lab-compatible event mapping
```

Success of this canary does not authorize Discovery, prospective observation, portfolio decisions or capital use.
