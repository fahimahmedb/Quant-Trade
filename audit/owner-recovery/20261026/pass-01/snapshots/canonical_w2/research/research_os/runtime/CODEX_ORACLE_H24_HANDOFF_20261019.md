# CODEX — ORACLE H24 RECOVERY HANDOFF

Repository: `fahimahmedb/Quant-Trade`
Branch: `builder/oracle-economic-loop-recovery-20261019`
Date: 2026-10-19

## Owner directive

Continue autonomously from this branch until the Oracle Free-Tier Research OS loop is code-complete and, when the configured Oracle host is reachable from the execution environment, operational H24.

Read first:

`research/research_os/runtime/CODEX_OWNER_AUTHORIZATION_20261019.json`

Authorization commit:

`d40376d346a6e2a630ea807a3ef698a7a01a91a8`

Do not restart from scratch. Push small recovery checkpoints after every bounded logical step.

## Final runtime objective

The steady-state path must be:

`Oracle Free-Tier VM -> bounded scheduled wake -> deterministic Python Research OS worker -> fresh GitHub durable state -> canonical claim/lease -> allowed stage(s) -> durable GitHub persistence -> exit`

A normal scheduled wake must not require Codex or another paid model inference call.

GitHub durable state is authoritative. Worker memory is not.

## Hard barriers

Keep all of these false:

- `economic_experiment_authorized`
- `prospective_observation_authorized`
- `real_capital_authorized`
- `live_trading_authorized`
- capital allocation / position sizing / orders

H24 research-worker launch is authorized; live trading and unauthorized outcome access are not.

## Recovery lineage

Initial recovery checkpoint:

`d69298b70c832955cf3bac7e0475dc7208412fc5`

Important refs:

- newest economic rail: `ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`
- Oracle VM autonomy: `8a1bdadc9bc52c4889ee19d0472bcee61fe24318`
- old OCI rail: `6e8ea155b05086f8e5eabcf830a5f835d3e3d09c`
- modern shared ancestry: `d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

Do not wholesale-merge the old OCI branch.

## Verified CP1

Deployment reconciliation is already implemented around:

- `deploy/oracle_release_install.py`
- `deploy/oci_research_os_deploy.py`
- `tests/test_oracle_release_install.py`
- `tests/test_oci_research_os_deploy.py`
- `.github/workflows/oracle-economic-loop-recovery-ci.yml`

Verified CI:

- head `2539fb5c27ca526298f78a1daa71027dea66b791`
- run `39260609874`
- conclusion `success`

Properties already preserved: exact release SHA, install lock, narrow OCI execution path, resumable state, atomic receipts, real pinned Legacy materialization, no stale hard-coded VM/SHA, no committed secrets, no scheduler activation at CP1.

## Verified CP2a

Final verified code state before this handoff:

`4c96a2a4fd37f9d994df8be4afd8d28edfab6189`

CI run:

`39263296808` -> `success`

That run passed:

- Python compilation
- 16 Oracle tests
- 91 Research OS/preflight/readiness tests
- scheduler-absence assertion

Important files:

- `research/research_os/worker_preflight.py`
- `research/research_os/tests/test_worker_preflight.py`
- `research/research_os/expansion/economic_test_readiness_v1.py`
- `research/research_os/tests/test_economic_readiness_integration.py`

CP2a now enforces:

- real Legacy ledger must be materialized and blob-verified;
- every current hypothesis JSON is enumerated, including heterogeneous historical schemas;
- unsupported schema-critical state fails closed;
- exact current hypothesis duplicates block;
- unresolved current-exposure overlap blocks candidate screening;
- ASML re-detection is a mandatory regression;
- readiness cannot ignore unresolved same-exposure risk;
- same payer + same mechanism + unknown timing clock is treated as unresolved, not independent;
- no empirical correlation or portfolio contribution is invented.

Mandatory ASML regression pair:

- `FUND-ASML-CAPACITY-SERVICE-001`
- `FUND-ASML-CAPACITY-PRICING-001`

Preserve:

`empirical_correlation = UNAVAILABLE`

`marginal_portfolio_contribution = NOT_ESTIMATED`

when admissible return data does not exist.

## Canonical control-plane contract

Read:

- `research/research_os/runtime/CONTROL_PLANE.json`
- `research/research_os/runtime/WORKFLOW_LANES.json`
- `research/research_os/runtime/SCHEDULED_WORKER_PROTOCOL.md`
- current task/event schemas
- current task and hypothesis files

Important existing rules:

- `source_of_truth = GITHUB_DURABLE_STATE`
- `worker_memory_authority = NONE`
- `workflow_model = ONE_LINEAGE_MULTI_STAGE`
- maximum one lineage per wake
- fresh state before each stage
- persist after each stage
- worker reconstructs context each wake
- optimistic lock uses current blob SHA
- lease generation required
- stale claims rejected
- discovery lane cannot validate its own hypothesis
- queue refill cannot invent arbitrary work

## NEXT: CP2b

Implement the canonical worker transport/claim layer.

### CP2b.1 Fresh GitHub wake snapshot

Every wake must reconstruct fresh durable state from the configured repository/ref. The installed release supplies executable code but must not become stale state authority.

Freshly bind at least:

- control plane
- workflow lanes
- tasks
- hypotheses
- Legacy manifest + verified materialized ledger
- canonical claim/event state

Bind the wake receipt to an exact GitHub state identity.

### CP2b.2 Claim / lease

Reuse existing contracts. Required behavior:

- deterministic highest-priority admissible READY task within lane;
- optimistic lock against current GitHub blob SHA;
- lease generation;
- stale claim rejection;
- one lineage per wake;
- no blind overwrite after concurrent state change.

### CP2b.3 Canonical execution adapter

Inventory existing task/lane executors first. Do not create a second research architecture.

Build only the smallest adapter needed to translate a claimed canonical task into existing Research OS stage functions.

### CP2b.4 Durable persistence

Persist after every stage using canonical repository task/event contracts. Logs/stdout are not durable task state.

### CP2b.5 Crash/idempotence regressions

Prove at minimum:

- restart before claim write;
- restart after claim but before execution;
- restart after stage output but before completion persistence;
- valid lease resume behavior;
- stale lease rejection;
- competing stale claim rejection;
- repeated wake after completed work does not duplicate execution.

## CP3 — H24 scheduler

After CP2b is green, add the production scheduled-worker layer for Oracle.

Prefer a bounded one-wake service invoked by a timer rather than a permanently authoritative in-memory daemon, unless existing repository design clearly requires otherwise.

The normal timer wake must use deterministic repository code and must not require Codex/model inference.

Extend the dedicated Oracle recovery CI with worker/scheduler regressions.

## Live-host verification

If the configured Oracle host is reachable from the execution environment, complete the deployment and verify the actual service/timer/runtime behavior. Clearly separate live-host evidence from CI evidence.

If host access is unavailable, finish all repository implementation, CI and runbook work and emit a precise external-access blocker instead of stopping early.

## Checkpoint sequence

Push at least:

- `CP2b.1` fresh-state transport
- `CP2b.2` claim/lease
- `CP2b.3` canonical executor binding
- `CP2b.4` durable persistence
- `CP2b.5` crash/idempotence tests
- `CP3.1` service/timer assets
- `CP3.2` deployment integration
- `CP3.3` full CI green
- `CP4` live Oracle receipt when possible
- `FINAL` operational/code-complete handoff

## Definition of done

Repository completion requires:

- dedicated Oracle recovery CI green on exact final SHA;
- fresh GitHub state every wake and before each allowed stage;
- canonical lane selection;
- optimistic claim/lease protocol;
- stale claim/generation rejection;
- one lineage per wake;
- persist after each stage;
- duplicate execution prevention across restart;
- Legacy and current-corpus preflight preserved;
- ASML regression preserved;
- readiness overlap blocker preserved;
- all hard capital/outcome flags remain false;
- scheduled wake has no default paid-model dependency;
- final machine-readable receipt + runbook committed.

When live Oracle access is available, additionally verify service/timer installation, enabled state, successful scheduled wake, durable state transition, restart safety, and exact deployed SHA.

Final verdict must be one of:

- `H24_ORACLE_RESEARCH_LOOP_OPERATIONAL`
- `H24_ORACLE_RESEARCH_LOOP_CODE_COMPLETE_LIVE_HOST_ACCESS_BLOCKED`
- `BLOCKED_BY_SPECIFIC_EXTERNAL_DEPENDENCY`

Continue until one of those final states is justified by evidence.
