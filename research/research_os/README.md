# Quant-Trade Research OS — Autonomous Loop Backbone

Status: canonical Oracle worker implemented; live Oracle access/qualification pending.
Recovery branch: `builder/oracle-economic-loop-recovery-20261019`.
Deployment/canaries: [`deploy/ORACLE_H24_RUNBOOK.md`](../../deploy/ORACLE_H24_RUNBOOK.md).

## Purpose

Build the thinnest final-shape backbone that can support:

1. a canonical scientific ledger;
2. a task/lease control plane;
3. Oracle systemd wakes with a local, pluggable model backend;
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

Codex is the build/repair plane. The H24 worker reconstructs context from GitHub
and never invokes Codex, ChatGPT or Work. Stage output/event/receipt/task progress
publish atomically; the durable claim is a preceding transaction.

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
