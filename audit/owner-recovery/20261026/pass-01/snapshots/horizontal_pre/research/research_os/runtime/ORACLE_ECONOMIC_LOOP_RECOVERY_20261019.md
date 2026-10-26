# Oracle Economic Loop Recovery — 2026-10-19

Status: **RECOVERY IN PROGRESS**

This file is the restart anchor for the interrupted Oracle/OCI + Research OS economic-loop integration.

## Source-of-truth refs

- Recovery branch base / newest economic-flow state:
  - branch: `builder/econ-test-flow-ust-auction-20261019`
  - commit: `ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`
- Oracle VM autonomy checkpoint:
  - branch: `builder/research-os-vm-autonomy-20261019`
  - commit: `8a1bdadc9bc52c4889ee19d0472bcee61fe24318`
- OCI one-shot installation rail:
  - branch: `ops/oci-one-shot-install-20261019`
  - commit: `6e8ea155b05086f8e5eabcf830a5f835d3e3d09c`
- Modern Research OS ancestry used by the economic-flow and VM work:
  - commit: `d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

## Recovery rule

Do **not** merge the OCI installation branch wholesale. Its useful Oracle deployment surfaces must be reviewed and selectively adapted onto the newest economic-flow state so that older ancestry cannot silently replace later Research OS/economic-loop work.

## Economic loop currently in scope

Primary current economic candidate/task:

`FLOW-UST-PRIMARY-DEALER-AUCTION-001`

Existing economic evidence, validation and queue/control-plane contracts on the base branch remain authoritative unless a later commit explicitly changes them.

## Integration invariants

1. Preserve all existing owner/governance restrictions and fail-closed behavior.
2. Do not invent empirical outcomes or authorize economic/live-capital execution.
3. Oracle/OCI is an execution host for the autonomous research worker, not a new source of economic truth.
4. Reuse the existing queue, control plane, worker protocol and candidate contracts; do not create a parallel scheduler or second economic architecture.
5. A worker cycle must be restartable/idempotent enough that a VM/process interruption cannot silently duplicate an economic experiment.
6. Deployment secrets/credentials must never be committed.
7. Every recovery checkpoint must leave this branch in a readable/restartable state.

## Planned checkpoints

- **CP0 — baseline pinned:** source refs, invariants and recovery strategy recorded.
- **CP1 — Oracle deployment reconciled:** selectively port/adapt the OCI bootstrap/runtime surfaces onto the modern branch; syntax/static checks recorded.
- **CP2 — worker-to-economic-loop wiring:** bind the Oracle scheduled worker to the canonical Research OS queue/control-plane cycle without bypassing validation/economic gates.
- **CP3 — recovery/smoke contract:** add deterministic startup/smoke/recovery verification and document exactly what is locally verified vs what still requires a live OCI host.
- **CP4 — final handoff:** branch status, remaining live-host actions and verification commands frozen for owner review.

## Verification discipline

Because the current execution environment cannot clone GitHub directly, repository reads/writes are being performed through the authenticated GitHub connector. Where executable validation is possible, only the exact fetched/modified subset is reconstructed locally and tested. No full-repository or live-OCI test may be claimed unless it was actually executed.
