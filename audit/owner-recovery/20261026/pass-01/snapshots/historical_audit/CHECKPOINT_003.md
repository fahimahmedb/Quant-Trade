# Forensic Audit Continuation — Checkpoint 003

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent audit head: `b59466c40547cb75511a912e5a6e8a5ad0dd5abd`
Status: `PARTIAL_IN_PROGRESS`

## Purpose

Freeze the forensic finding on the modern Research OS execution path and the U.S. Treasury auction candidate authority boundary before any Oracle/OCI integration is resumed.

This checkpoint is observational only. It adds no production worker, scheduler, workflow, economic result, authorization or deployment change.

## 1. Modern production executor: not observed in the reviewed canonical path

Reference modern Research OS commit:

`d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

### Runtime directory

The reviewed `research/research_os/runtime/` directory contains:

- `CAPABILITY_REGISTRY.json`
- `CONTROL_PLANE.json`
- `RESEARCH_FRONTIER.json`
- `SCHEDULED_WORKER_PROTOCOL.md`
- `WORKER_REGISTRY.sim.json`
- `WORKFLOW_LANES.json`
- `workflow_simulator.py`

No production worker/executor implementation is present in that runtime directory.

### Autonomous-loop GitHub workflow

`.github/workflows/research-os-autonomous-loop-ci.yml` is a CI-only surface. It is named `Research OS autonomous loop CI`, runs on the historical builder branch / workflow dispatch, and executes only:

`node --test research/research_os/tests/*.test.mjs`

Its job is explicitly named `preprod-simulation`.

It is not a scheduled production worker and does not claim/execute Research OS tasks.

### Multi-engine pipeline

`research/research_os/engines/pipeline.py` is also explicitly synthetic:

- constructs `EngineContext(..., synthetic_only=True)`;
- requires engine outputs to remain `synthetic_only`;
- returns authorities with `production_workers: false`;
- also returns `real_capital`, `live_trading`, `prospective_observation` and `economic_experiment` as false.

### Queue/control surfaces

The previously reviewed `SCHEDULED_WORKER_PROTOCOL.md`, `queue_replenisher.py`, `control_plane.py`, runtime registries and simulator define contracts, safe queue replenishment, orchestration permissions and simulations, but no reviewed surface has yet been shown to provide the complete production sequence:

1. refresh canonical remote state;
2. atomically claim a durable task;
3. persist `ACTION_STARTED`;
4. dispatch the exact producer/validator/integrator capability;
5. persist artifacts and handoff;
6. finalize task state / receipt;
7. recover idempotently after crash without duplicate scientific execution.

### Forensic classification

`PRODUCTION_EXECUTOR_OBSERVED_IN_REVIEWED_MODERN_PATH = FALSE`

This is a scoped negative finding, not a proof that no executor exists anywhere in all 3,494+ reachable commits or in an external system. Before Oracle activation, either the canonical executor must be located and audited, or its absence must be accepted and the missing implementation separately designed under governance. OCI MUST NOT invent a parallel executor merely because infrastructure is available.

## 2. UST candidate is frozen but no economic result artifact is observed

Branch:

`builder/econ-test-flow-ust-auction-20261019`

Current observed head remains:

`ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`

Head message:

`checkpoint: freeze UST auction screen state before outcome acquisition`

Candidate:

`FLOW-UST-PRIMARY-DEALER-AUCTION-001`

The candidate artifact directory currently contains only:

`research/research_os/artifacts/FLOW-UST-PRIMARY-DEALER-AUCTION-001/frozen-economic-screen-v1.json`

The frozen protocol itself records:

- `freeze_status = FROZEN_BEFORE_OUTCOME_ACCESS`
- `outcome_accessed = false`
- `economic_result = NOT_OBSERVED`

The validation task is `COMPLETE` with result `PASS_TO_TEST_DESIGN_BOUNDED`, but its authority object still declares:

- `economic_experiment_authorized = false`
- `prospective_observation_authorized = false`
- `real_capital_authorized = false`
- `live_trading_authorized = false`

The independent assessment likewise records no outcome or price/return access and recommends only a bounded test design.

### Forensic classification

`UST_PROTOCOL_FROZEN = TRUE`

`UST_ECONOMIC_RESULT_OBSERVED_IN_BRANCH = FALSE`

`UST_OUTCOME_ACCESS_RECORDED_IN_PROTOCOL = FALSE`

No audit action should execute the frozen screen merely because its protocol exists.

## 3. Hard authority-precedence conflict

The same UST lineage contains incompatible durable statements.

### Global durable control

Modern `research/research_os/runtime/CONTROL_PLANE.json` keeps economic experiment authority false.

The validation task and validation assessment also keep economic experiment authority false.

### Local frozen protocol / work receipt

`frozen-economic-screen-v1.json` contains:

`owner_authorization = "Economic outcome access is authorized only after this protocol file is committed. Real capital and live trading are not required for this screen."`

The CP2 post-freeze work receipt records:

- `current_stage = AUTHORIZED_OUTCOME_ACQUISITION_AND_EXECUTION_OF_FROZEN_SCREEN`
- `owner_authorization = CURRENT_CONVERSATION_OWNER_AUTHORIZATION_ACCEPTED_FOR_BOUNDED_ECONOMIC_RESEARCH_AND_CANDIDATE_SUBSTITUTION`
- `status = CHECKPOINT_PUSHED_CONTINUE_AUTONOMOUSLY`

### Conflict

There is therefore no single machine-readable durable authority source whose precedence is unambiguous:

- canonical/global control says economic experiment authorization is false;
- candidate-local receipt/protocol says bounded outcome acquisition is authorized after freeze.

A human may understand the conversational intent, but an autonomous worker cannot safely infer that a candidate receipt supersedes a canonical control-plane denial unless precedence is explicitly defined and auditable.

### Blocker classification

`AUTHORITY_PRECEDENCE_CONFLICT = TRUE`

`AUTONOMOUS_OUTCOME_ACCESS_SAFE = FALSE`

`ORACLE_AUTONOMOUS_ACTIVATION_SAFE = FALSE`

This blocker is fail-closed. The audit does not choose which authority should win and does not repair the conflict.

## 4. Scientific identity coverage remains incomplete

Checkpoint 002 established that PR #1 is a 700-commit scientific lineage and that the current Legacy reconciliation is explicitly partial. PR #1 contains scientific families, including PEAD and volatility-targeting work, that are not represented in the reviewed Legacy ledger.

This matters directly to autonomous execution: a queue/replenisher can only prevent re-testing/rebranding if its Legacy identity base actually contains the historical families and aliases.

Therefore:

`SCIENTIFIC_IDENTITY_COVERAGE_COMPLETE = FALSE`

`ANTI_RESTART_GATE_PROVEN_COMPLETE = FALSE`

Until the PR #1 lineage and other unreachable/closed-PR scientific histories are semantically reconciled, an autonomous producer may still generate a superficially new candidate that is an old tested exposure.

## 5. Oracle / OCI implication

The OCI branch has useful deployment/recovery mechanics but is 55 commits behind the modern Research OS line at the previously established comparison and remains unsuitable as a base.

The present forensic state is now stricter:

- infrastructure bootstrap exists on the OCI rail;
- modern worker semantics exist as protocol/contracts/simulation;
- the reviewed production executor is not yet located;
- the UST frozen test sits at an authority-precedence conflict;
- scientific anti-restart coverage is incomplete.

Therefore Oracle must remain a **host candidate**, not an autonomous economic authority or an excuse to create an ad hoc second worker architecture.

## Current verdict

- `COVERAGE_COMPLETE = FALSE`
- `SAFE_TO_CONSOLIDATE = FALSE`
- `SAFE_TO_WHOLESALE_MERGE_OCI = FALSE`
- `PRODUCTION_EXECUTOR_OBSERVED_IN_REVIEWED_MODERN_PATH = FALSE`
- `UST_PROTOCOL_FROZEN = TRUE`
- `UST_ECONOMIC_RESULT_OBSERVED_IN_BRANCH = FALSE`
- `AUTHORITY_PRECEDENCE_CONFLICT = TRUE`
- `SCIENTIFIC_IDENTITY_COVERAGE_COMPLETE = FALSE`
- `ORACLE_AUTONOMOUS_ACTIVATION_SAFE = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Next forensic work

1. Search all relevant modern/side branches and historical commits for any real executor/claim/dispatch implementation before concluding it is absent repository-wide.
2. Build the PR #1 scientific lineage/identity map and reconcile aliases/mechanisms/verdicts against the Legacy ledger and current Research OS hypotheses.
3. Trace all authority declarations and Owner decisions to determine the historical origin of the UST local authorization, without treating conversation-derived receipts as globally canonical by default.
4. Audit task state/lease/recovery contracts for crash semantics and duplicate-execution risk once the actual executor is located or its absence is firmly established.
5. Continue data-feed provenance/consumer review and final moving-ref delta before closing coverage.

No operational repair should be merged from this checkpoint.
