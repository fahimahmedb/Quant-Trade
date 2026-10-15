# Quant-Trade Research OS — Final Target Architecture

Status: DEVELOPMENT / SIMULATION ONLY

## Objective

Build the final architectural shape early, while keeping each component thin until the end-to-end contracts are proven.

```text
Owner / Governance
       |
Scientific Core
       |
Control Plane / Task + Lease Ledger
       |
+------+--------+---------+---------+
|      |        |         |         |
Legacy Quant  Event/Docs Fundamental Flows
              |
         CandidateHypothesis
              |
      Independent Validator
              |
           Red Team
              |
      Economic Identity
              |
        Portfolio Map
              |
      Shadow / Prospective
              |
         Decay Monitor

All components emit canonical WorkerEvents and durable receipts to the Live Lab event path.
```

## Canonical memory

Conversations and model sessions are workers, not the source of truth. Canonical state is repository-backed: contracts, ledgers, task state, receipts, evidence and artifacts.

## Development rule

Before any production scheduled workers are enabled, prove the whole chain with deterministic synthetic fixtures. No real market outcome, prospective observation, real capital or live trading is required for this phase.

## Required interfaces

1. HypothesisContract
2. ResearchTask
3. ExperimentResult
4. EvidenceAssessment
5. CandidateEconomicIdentity
6. WorkerEvent
7. WorkerReceipt

## Research engines

Initial production-facing engine families after simulation:

- Legacy / Recovery
- Quant / Mechanisms
- Event / Document Intelligence
- Fundamental Research
- Forced Flows / Institutional Constraints
- Independent Validation / Red Team
- Portfolio Mapping

Each engine produces or consumes the same canonical contracts. No engine may silently redefine scientific state.

## Portfolio boundary

Portfolio v0 maps economic identity, overlap and marginal contribution. Capital allocation and trading authority remain separate future capabilities.

## Safety

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
