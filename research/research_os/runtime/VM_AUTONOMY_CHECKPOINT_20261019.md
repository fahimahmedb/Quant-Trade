# Quant-Trade Research OS — Oracle VM Autonomy Checkpoint

Date: 2026-10-19

## Branch

`builder/research-os-vm-autonomy-20261019`

## Exact source checkpoint

This branch was created directly from the current autonomous Research OS head:

`d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

Source branch:

`builder/research-os-autonomous-loop-20261015`

Source commit message:

`research-os: close FDA adcom validation`

## Mission

Make the existing Research OS executable continuously from the Oracle Cloud VM without creating a second research architecture or a second source of truth.

The VM is an execution host for the canonical Research OS workflow protocol. It must reconstruct state from fresh GitHub state on every wake and operate through the existing durable queue, leases, receipts and worker events.

## Explicitly out of scope

- Live Lab 3D / UX rail
- Site publication / public live wiring
- SSE visual integration
- redesign of Research OS architecture
- free-form autonomous research outside the existing frontier/control-plane contracts
- real capital
- live trading

The failed/separate 3D/live rail is intentionally not touched here.

## Verified existing canonical surfaces

The autonomous branch already contains and uses:

- `research/research_os/runtime/CONTROL_PLANE.json`
- `research/research_os/runtime/CAPABILITY_REGISTRY.json`
- `research/research_os/runtime/WORKFLOW_LANES.json`
- `research/research_os/runtime/RESEARCH_FRONTIER.json`
- `research/research_os/runtime/SCHEDULED_WORKER_PROTOCOL.md`
- `research/research_os/control_plane.py`
- `research/research_os/queue_replenisher.py`
- durable task files under `research/research_os/tasks/`
- durable worker events under `research/research_os/events/`
- durable receipts under `research/research_os/receipts/`

## Existing worker contract that must be preserved

The current protocol already defines:

- `MAX_LINEAGES_PER_WAKE = 1`
- multi-stage work only inside the same lineage
- maximum bounded stages per wake
- producer/challenge separation
- optimistic-lock task claim using the Git blob SHA
- bounded leases (<=55 minutes)
- exactly one durable wake receipt
- fresh queue observation before terminal worker state
- deterministic empty-queue refill through the integrator steward only
- no free-form work invention
- Legacy screening before candidate freeze
- conservative queue observability (`IDLE` only after fresh global proof)

The VM runner must implement this contract, not replace it.

## Queue/refill implementation already present

`research/research_os/queue_replenisher.py` already provides deterministic, bounded refill logic and preserves authority boundaries. The VM rail should call/reuse this implementation rather than duplicate it.

## Hard authority state to preserve

The current control-plane contract requires all of the following to remain false unless separately changed by a later explicit Owner decision:

- `economic_experiment_authorized = false`
- `prospective_observation_authorized = false`
- `real_capital_authorized = false`
- `live_trading_authorized = false`

Production research workers themselves are already authorized by the control plane.

## Current diagnosis

The Research OS protocol and queue semantics are present, but the repository does not yet prove the existence of a continuously running Oracle-VM service that wakes lanes and executes the protocol end-to-end.

The missing layer is therefore primarily **execution/orchestration**, not a new scientific architecture.

## Next implementation slice

Build the smallest bounded VM execution rail that:

1. starts from fresh GitHub state;
2. validates the control plane before every wake;
3. selects one configured workflow lane;
4. enumerates durable tasks and selects one admissible READY lineage;
5. claims by optimistic locking / lease semantics;
6. delegates the bounded stage execution through a pluggable worker backend;
7. persists task/event/receipt outputs durably;
8. handles empty-queue refill only through the existing integrator policy;
9. stops after one lineage per wake;
10. exposes a dry-run/canary mode before any continuously scheduled VM activation.

The worker backend should be model-agnostic so the Oracle host can use the already-installed local/free model path later without coupling Research OS semantics to one LLM provider.

## Deployment target

After the runner is proven locally/in CI, add a minimal Oracle-VM deployment surface (for example systemd timer/service or equivalent) that invokes bounded lane wakes. Do not deploy/enable the service until exact-head tests and a no-mutation canary pass.

## Checkpoint status

`VM_AUTONOMY_RAIL = CHECKPOINTED`

`VM_SERVICE_IMPLEMENTED = FALSE`

`VM_SERVICE_ENABLED = FALSE`

`AUTONOMOUS_SOURCE_BRANCH_MUTATED = FALSE`

`LIVE_LAB_3D_TOUCHED = FALSE`

`ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`LIVE_TRADING_AUTHORIZED = FALSE`

## Resume instruction

Resume from this branch and this checkpoint. Do not restart architecture discovery. Build only the minimal Oracle-VM execution layer needed to operationalize the already-defined scheduled-worker protocol.