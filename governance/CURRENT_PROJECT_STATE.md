# Quant-Trade — current canonical project state

STATUS=`CANONICAL_CODE_ENGINEERING_CONNECTED_AND_QUALIFIED_VM_MULTI_WAKE_BLOCKED_EXTERNAL_HOST_ACCESS`
DATE=`2026-11-01`

## Canonical authority

- CODE AUTHORITY: `code/canonical`
- PROJECT / GOVERNANCE AUTHORITY: `project/canonical`
- repository default branch is not engineering authority
- `BRANCH_DELETION_AUTHORIZED=FALSE`
- `BRANCH_RETIREMENT=PARK`

Historical branches and forensic evidence remain preserved. Do not restart global archaeology.

## Current exact code head

`code/canonical=13c9ff03f0898e9af28abaa3dab78a520c70c887`

Base lineage remains Wave2 C2:
`ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

The canonical code contains selective CP099 hardening, selective GIGA-Q hardening/repair, PR46 bounded GPT-OSS/Codex orchestration, and now the minimal host-wake connection to the existing V1 systemd timer.

### Exact-head qualification

Workflow run `41265514716` completed `SUCCESS` on exact head `13c9ff03f0898e9af28abaa3dab78a520c70c887`.

Executed proof:
- exact head identity: PASS;
- compile integrated deltas: PASS;
- CP099 carried-hardening regressions: `22/22 PASS`;
- PR46 autonomy + host-wake regressions: `21/21 PASS`;
- `GPT_OSS_LAUNCHER_ISOLATION=PASS`;
- Wave2 non-regression sample: `48/48 PASS`;
- post-Wave2 GIGA-Q challenge: `110/110 PASS` plus `44 subtests PASS`;
- `CANONICAL_AUTHORITY_CLOSED=PASS`;
- clean checkout: PASS.

Claim ceiling:
`ENGINEERING_CONNECTED_AND_QUALIFIED=TRUE`
`ACTUAL_VM_MULTI_WAKE_AUTONOMY_PROVEN=FALSE`

CI proves the code seam and regressions. It does not prove deployment, current VM health, timer activation, a real Codex wake, or multi-wake autonomous continuation.

## Latest evidence → challenge → correction chain

Preserve, do not rewrite:

1. `6039cfd7a8502e0a4727a6928a4ef4cb75a3bb6e`
   - prior combined canonical candidate;
   - run `41264501411`: SUCCESS;
   - CP099 `22/22`, PR46 `16/16`, Wave2 `48/48`, GIGA-Q `110/110 + 44 subtests`.

2. Runtime-seam challenge discovered after that PASS:
   - canonical systemd V1 service still directly executed `research.research_os.oracle_worker`;
   - neither `oracle_worker` nor `oracle_worker_v2` invoked `scripts/gpt_oss_orchestrator.py`;
   - under `ProtectSystem=strict`, the Codex orchestration state also required an explicit writable root under `/var/lib/quant-research`.
   - verdict: `CONNECT_REQUIRED`, not a second daemon/scheduler.

3. `a0115d8a0b3f83e32d321d73d2dfb560f221a406`
   - added `research/research_os/host_wake.py`;
   - existing V1 timer now routes exactly one wake: default existing `oracle_worker`, feature flag `=1` bounded GPT-OSS/Codex orchestrator;
   - requires orchestration state below `/var/lib/quant-research`;
   - no second timer, daemon or scientific queue;
   - run `41265426984`: FAILURE only in the new host-wake test harness after CP099 passed. Two tests mocked `os.execve`; the mock returned and reached a deliberately impossible post-execve exception. This was not a demonstrated production routing failure.

4. `13c9ff03f0898e9af28abaa3dab78a520c70c887`
   - one-file correction: remove the unreachable production post-`execve` exception so mocked `execve` can return in tests;
   - real `execve` semantics unchanged: production process replacement remains one-process/one-wake;
   - run `41265514716`: full SUCCESS with all regression/challenge suites above.

Decision: the host-wake software connection is closed at hosted engineering qualification. Do not reopen CP099/GIGA-Q/PR46 or build another scheduler absent contradictory primary evidence.

## VM multi-wake proof

`VM_MULTI_WAKE_PROOF=BLOCK_EXTERNAL_HOST_ACCESS`
`CURRENT_HOST_STATE=UNKNOWN`
`HOST_ACCESS_IN_THIS_SESSION=BLOCKED_EXTERNAL`
`CURRENT_ORACLE_STATE_BRANCH_LAST_ACTIVITY=2026-10-20`
`SOFTWARE_CONNECTION_GAP=RESOLVED_AND_QUALIFIED`
`LIVE_HOST_DEPLOYMENT=NOT_PROVEN`
`REAL_CODEX_WAKE_FROM_VM=NOT_PROVEN`
`TWO_AUTOMATIC_WAKES=NOT_PROVEN`

Fresh primary evidence:
- state branch `builder/oracle-economic-loop-recovery-20261019` remains at `0837f419c4e3a9e17a39269994f27d97fcf79757`, authored `2026-10-20T11:00:11Z`; therefore it is not current November host evidence;
- issue #44 remains open and its durable terminal evidence says the PR46 engineering repair was qualified/published but actual VM rebind remained blocked by missing authenticated host access;
- no later issue receipt proves deployment or a real multi-wake loop;
- the current session has authenticated GitHub access but no demonstrated authenticated OCI Run Command / SSH / host-command channel.

Do not fake the E2E by manually posting a Codex comment: the acceptance requires zero human relaunch/routing on the normal path.

## Next action — single critical path

`NEXT_ACTION=VM_MULTI_WAKE_PROOF_ON_AUTHENTICATED_EXISTING_HOST`

When authenticated host execution becomes available:
1. inventory the actual intended VM: active release SHA, V1/V2 unit, timer, env/config, GPT-OSS command/model and GitHub principal;
2. deploy/rebind only if exact inventory proves it is required, using qualified `13c9ff03f0898e9af28abaa3dab78a520c70c887`;
3. configure `QUANT_CODEX_ORCHESTRATION_ENABLED=1` and a `QUANT_CODEX_ORCHESTRATION_ROOT` strictly below `/var/lib/quant-research`, plus the already-defined bounded task/issue/head/model/GitHub environment;
4. prove at least two consecutive automatic timer wakes with no Owner relaunch;
5. prove one real Codex dispatch/result causally bound to the following GPT-OSS decision;
6. bind task/dispatch/attempt/expected-head/result identities, exact-head CI and distinct review;
7. exercise duplicate/restart/stale-head/retry recovery;
8. preserve scientific semantics and all closed authorities;
9. persist sanitized host receipts in GitHub.

If host access remains unavailable, correct result is `BLOCK_EXTERNAL_HOST_ACCESS`; do not substitute more architecture, more CI, or another scheduler.

## Known next-layer limitation — PARK until VM bridge proof

Issue #44 evidence also shows the current launcher is task-bounded: environment supplies a fixed task/prompt/issue/branch/head. It can continue that task through dispatch/result/CI/review/DONE/PARK, but it does not yet prove global autonomous selection of the next unmet Quant-Trade mission after terminal completion.

Status: `GLOBAL_PROJECT_MISSION_SELECTION=PARK_AFTER_VM_BRIDGE_PROOF`.

Do not build that next layer before the real bridge is proven; otherwise we would expand unproven autonomy instead of closing the current critical path.

## Closed authorities

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`
`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`
`SCIENTIFIC_UNBLINDING_AUTHORIZED=FALSE`
`REAL_CAPITAL_AUTHORIZED=FALSE`
`LIVE_TRADING_AUTHORIZED=FALSE`
`PRODUCTION_DEPLOYMENT_AUTHORIZED=FALSE`
`DESTRUCTIVE_REPOSITORY_CLEANUP_AUTHORIZED=FALSE`

Canonical method: `REUSE > CONNECT > REPAIR > BUILD`.
Valid outcomes: `NO_CHANGE_REQUIRED`, `CONNECT`, `REPAIR`, `PARK`, `BLOCK`, `UNKNOWN`.
