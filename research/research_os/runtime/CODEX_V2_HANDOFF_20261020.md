# Codex Handoff — Oracle Research OS V2 Core

Date: 2026-10-20
Repository: `fahimahmedb/Quant-Trade`
Working branch: `builder/oracle-v2-core-20261020`
Handoff base HEAD at creation: `59cd2519fe99d228b1a1cf74405233c02ea5377b`

## 0. Mandatory reacquisition rule

This repository can move after this handoff. **Do not trust the HEAD above without checking it.**

Before any write:

1. fetch the fresh HEAD of `builder/oracle-v2-core-20261020`;
2. inspect the current V2 CI and SEC CI state for that exact HEAD;
3. read the canonical routing/spec/roadmap below;
4. preserve every commit that appeared after this handoff;
5. never force-push, reset, rewind or delete autonomous evidence.

GitHub is durable project memory. Runtime/VM facts require runtime evidence.

## 1. Owner objective

Finish **Oracle Research OS V2 Core** as an autonomous, restart-safe, bounded, pre-outcome research system that can continuously progress from research ideation/evidence through independent validation and a frozen economic-test-ready export intent.

The intended system-level qualification is:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`

The strongest candidate-level claim permitted in V2 Core is:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY`

This means “the research package is structurally/scientifically ready to be tested later under separate authorization.” It does **not** mean profitable, alpha-proven, economically validated, prospective-qualified or live-ready.

V2 Core should ultimately be able to run autonomously on the Oracle VM using the already-qualified V1 orchestration properties (fresh GitHub state, atomic claims/leases, recovery, systemd scheduling, local GPT-OSS), while preserving V1 as the previously qualified baseline.

## 2. Permanent authority boundary

These remain false throughout this mission:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Do not open any of them.

Do not read economic outcomes, future/prospective observations, live positions, orders or real-capital data as part of V2 Core qualification.

## 3. Owner override — P0-D lifted

The prior architecture had proposed server-side branch protection / fast-forward-only enforcement as P0-D.

Owner decision: **P0-D is lifted.**

Therefore GitHub branch protection, rulesets or server-side force-push prevention are **not** V2 Core Definition-of-Done gates.

Operational discipline still forbids agents from force-pushing, resetting, rewinding or deleting durable evidence. This is an operating rule, not a server-side requirement.

## 4. Read order

Read in this order before changing code:

1. `QUANT_NORTH_STAR.md`
2. `CLAUDE.md`
3. `CLAUDE_CURRENT_MISSION.md`
4. `research/research_os/architecture/ORACLE_V2_CORE_SPEC.md`
5. `research/research_os/runtime/ORACLE_V2_CORE_ROADMAP.md`
6. `research/research_os/runtime/V2_CORE_POLICY.json`
7. `research/research_os/runtime/V2_ACTIVE_EPOCH.json`
8. this handoff
9. only then inspect code/tests relevant to the next work package

V1 history is useful only for properties inherited from V1. Do not restart the entire project archaeology unless a concrete contradiction requires it.

## 5. What ChatGPT already implemented

### 5.1 Routing / architecture

Implemented and committed:

- dedicated V2 branch `builder/oracle-v2-core-20261020`;
- `CLAUDE.md` rewritten to route builders into V2 Core;
- `CLAUDE_CURRENT_MISSION.md` rewritten so stale September Blue handoffs do not override V2;
- canonical architecture:
  `research/research_os/architecture/ORACLE_V2_CORE_SPEC.md`;
- execution roadmap:
  `research/research_os/runtime/ORACLE_V2_CORE_ROADMAP.md`;
- fail-closed V2 policy:
  `research/research_os/runtime/V2_CORE_POLICY.json`;
- active research epoch:
  `research/research_os/runtime/V2_ACTIVE_EPOCH.json`.

### 5.2 Core V2 scientific contracts

Implemented in:

`research/research_os/expansion/v2_core.py`

It covers:

- four closed authorities;
- Research Epoch manifest/hash;
- pre-export vs post-export epoch mutation rules;
- source PIT vs model PIT distinction;
- model-routing policy checks;
- research-trial accounting from ideation;
- CandidateCore + family-specific extensions;
- Validator execution-state vs scientific-decision separation;
- multidimensional status axes;
- explainable priority decisions;
- scoped Negative Memory;
- frozen export intent;
- Evaluation reverse-channel allowlist;
- owner/supervisor blinding state;
- successor-only feedback release;
- fail-closed V2 system qualification.

### 5.3 Existing engine compatibility

Implemented in:

`research/research_os/expansion/v2_bridge.py`

It bridges all existing primary producer families into V2 CandidateCore:

- `FUNDAMENTAL` -> `FundamentalExtension`
- `EVENT_DOCUMENT` -> `EventExtension`
- `INSTITUTIONAL_FLOW` -> `ForcedFlowExtension`
- `QUANT_MECHANISM` -> `QuantExtension`

Important invariant: non-flow families do **not** receive fabricated forced-flow fields.

It also bridges existing independent validation into the V2 Validator state model and requires explicit state-isolation evidence, not merely different worker names.

### 5.4 Deterministic whole pre-outcome pipeline

Implemented in:

`research/research_os/expansion/v2_pipeline.py`

It proves a deterministic bounded path:

`epoch -> research trial -> candidate -> validator -> frozen export intent -> evaluation ingest receipt`

with no outcome access.

Canonical fixture:

`tests/fixtures/oracle_v2_core_fixture.json`

Exact-head receipt generator:

`scripts/qualify_oracle_v2_core.py`

### 5.5 V2 worker integration without modifying V1 default

A critical design choice was made: **do not alter the qualified V1 worker default path.**

Instead V2 is additive.

Implemented:

`research/research_os/oracle_worker_v2.py`

This reuses V1 `ResearchOSWorker` for:

- fresh GitHub snapshots;
- queue/task selection;
- atomic claims;
- leases;
- crash recovery;
- CAS-safe publication;
- durable receipts;
- bounded wake behavior.

It substitutes only a V2 executor and requires explicit:

`research_contract_version = v2-core`

It fails closed if any of the four authorities are true.

Implemented:

`research/research_os/expansion/v2_stage_executor.py`

This wraps existing V1-qualified stage execution and writes V2 sidecars in the same atomic stage transition where appropriate:

- research trial;
- candidate draft;
- leakage/PIT classification;
- disconfirmation record;
- frozen V2 candidate;
- validation-handoff bindings;
- V2 validator artifact;
- V2 readiness artifact;
- frozen export intent when all pre-outcome gates pass.

The Evaluation plane remains SEALED. The worker can create a `FROZEN_EXPORT_INTENT`, but it does not run economic evaluation.

## 6. Tests and CI already proven

Dedicated workflow:

`.github/workflows/oracle-v2-core.yml`

At HEAD `59cd2519fe99d228b1a1cf74405233c02ea5377b`:

- V2 workflow run: `39355558790`
- conclusion: SUCCESS
- exact-head artifact ID: `12235620301`
- artifact name:
  `oracle-v2-core-verification-59cd2519fe99d228b1a1cf74405233c02ea5377b`
- artifact ZIP digest:
  `sha256:4ebf0ed41f4dae6173f2f10035210820c64938756a2c448ee52e52dba93fce9a`

The V2 CI executed 34 V2 tests and passed compilation, policy fail-closed checks, claim ceiling checks and exact-head receipt generation.

Exact receipt summary emitted by CI:

- `status = AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`
- `verified_commit_sha = 59cd2519fe99d228b1a1cf74405233c02ea5377b`
- `fixture_sha256 = 75cc0d4e29c2fb64dd10cf05ca04a87a85c18cd5cb570f498b465c205797458b`
- `receipt_hash = 82295fa29ef43cdf22508008738b06e767d7de149692836164b8fb908e6920a4`

At handoff creation time, the large historical workflow was still running on the same HEAD:

- workflow: `SEC P0 pre-t0 gate`
- run: `39355558865`
- status at handoff: `in_progress`

**Re-query it. Do not assume its final state from this document.**

## 7. Current unfinished work

### 7.1 Highest priority: finish exact-head repo qualification

Reacquire the current branch HEAD.

If HEAD is still `59cd2519...`:

- verify V2 run `39355558790` remains SUCCESS;
- inspect final conclusion of SEC run `39355558865`;
- if SEC failed, diagnose and fix the real regression rather than bypassing the gate;
- if HEAD advanced, use the newer exact-head runs instead.

### 7.2 Add real no-write GitHub dry-run of `oracle_worker_v2`

ChatGPT was about to add this when the Owner requested the handoff.

The desired next improvement is a CI step that executes the **real** V2 entrypoint in `dry-run` mode against the V2 branch using a fresh `GitHubStateStore`, proving:

- real entrypoint imports and starts;
- fresh GitHub state can be read;
- worker preflight succeeds;
- V2 contract is explicitly selected;
- no GitHub writes occur in dry-run;
- no hosted model fallback is used;
- all four authorities remain false.

Do not manufacture success with mocks for this specific proof. Unit tests with mocks already exist; this new step is an integration proof.

### 7.3 Roadmap/checkpoint is stale relative to implementation

`ORACLE_V2_CORE_ROADMAP.md` was created before worker integration completed.

Update it only after reconciling current CI. It should reflect that:

- V2-1 core contracts: implemented + CI PASS;
- V2-2 repository integration: largely implemented, including additive V2 worker path;
- V2-3 adversarial verification: V2 CI PASS, broader SEC/V1 regression pending/reconcile exact HEAD;
- V2-4 deterministic whole pre-outcome receipt: PASS in CI;
- V2-5 deployment/runtime qualification: still pending.

Create a durable checkpoint after the exact-head CI state is known.

### 7.4 Deployment path still pending

V2 is repository-qualified but is **not yet the active Oracle VM worker**.

The current V1 production runtime remains the already-qualified V1 release path unless independently changed after this handoff.

Do not claim V2 runtime qualification merely because CI is green.

Build the deployment path by reusing the V1 exact-SHA discipline, but do not overwrite V1 blindly.

Preferred design:

1. exact-SHA release installation;
2. V2-specific worker config pointing to `builder/oracle-v2-core-20261020`;
3. explicit `research_contract_version = v2-core`;
4. same local GPT-OSS backend;
5. V2 canary with scheduler stopped;
6. verify real GitHub read/dry-run/no-write path;
7. controlled V2 write canary only if necessary for new properties;
8. activation only after exact-release qualification;
9. natural scheduled wake proof;
10. restart/reboot regression only for properties materially affected by the V2 runtime change.

Keep V1 recoverable as previous known-good release.

### 7.5 Systemd entrypoint issue

The existing V1 service unit still calls:

`python3.12 -m research.research_os.oracle_worker`

V2 has a separate entrypoint:

`python3.12 -m research.research_os.oracle_worker_v2`

Do not silently replace the V1 service unit before qualification.

Use a V2-specific deployment/service path or an explicitly qualified exact-release switch. Preserve rollback to V1.

## 8. Final V2 Core objective

The mission is complete only when both repository and runtime evidence support the following without opening outcomes:

### Repository/scientific

- Research Epoch frozen and enforced;
- trial accounting begins at ideation;
- source PIT and model PIT are distinguished;
- CandidateCore + family-specific contracts are enforced;
- Validator independence/state separation is explicit;
- Evaluation membrane is sealed;
- reverse channel is restricted;
- feedback can influence successor epochs only;
- priority is explicit and explainable;
- Negative Memory is scoped/revisitable;
- structural overlap is not mislabeled empirical correlation;
- all four authorities remain false;
- exact-head qualification receipt exists.

### Autonomous runtime

- V2 entrypoint runs on the actual Oracle host;
- local GPT-OSS is used; no hosted fallback;
- fresh GitHub state is the durable orchestration source;
- claim/lease/CAS/recovery behavior inherited from V1 still works;
- V2 sidecars are durably produced in real autonomous wakes;
- natural timer wakes continue autonomously;
- restart/reboot resilience remains valid for the new release where affected;
- no duplicate task/stage/receipt/export sidecars under crash/replay;
- no outcome access;
- all four authorities remain false.

Then create a final V2 Core checkpoint stating exactly what is proven and what remains outside scope.

## 9. Explicit non-goals for this handoff

Do **not**:

- authorize or execute an economic experiment;
- start prospective observation;
- trade live or use real capital;
- infer profitability from V2 qualification;
- fabricate market evidence;
- turn model commentary into evidence;
- silently change epoch close policy after first accepted export;
- weaken Validator independence;
- treat infrastructure failures as scientific falsification;
- require P0-D branch protection after the Owner lifted it;
- replace GitHub orchestration with a second authoritative backend without an explicit migration gate;
- rewrite V1 history to make V2 look cleaner.

## 10. Execution doctrine for Codex

Act as the implementation lead, not as a passive reviewer.

- Work in large coherent packages.
- Do not repeatedly ask the Owner for decisions already encoded in repo governance.
- Reacquire HEAD before writes.
- Prefer direct implementation when delegation overhead exceeds the task.
- If delegating, give exact branch/base SHA, scope, invariants, acceptance tests and expected handoff.
- Fix real failures instead of suppressing gates.
- Keep commits meaningful.
- Keep GitHub as reacquisition memory after every major package.
- Stop only at a genuine external boundary (e.g. root/SSH Owner action on the VM).

## 11. First actions Codex should execute

1. `git fetch` / resolve the exact current HEAD of `builder/oracle-v2-core-20261020`.
2. Read the files in section 4.
3. Query exact-head GitHub Actions.
4. Reconcile SEC/V1 regression result.
5. Run/inspect the V2 test suite locally.
6. Add the real no-write GitHub `oracle_worker_v2 --mode dry-run` integration proof if not already present at the new HEAD.
7. Update the V2 roadmap + create a checkpoint only after the evidence is reconciled.
8. Build the V2 exact-SHA deployment/canary path without changing V1 production by default.
9. Stop for Owner only when a real VM/root action is required; provide one large copy/paste block and precise expected evidence.

The project should continue from here, not restart.
