# CHECKPOINT 011 — Repository hygiene / V2 source preservation

Recorded 2026-10-20 (Europe/Paris).

## Scope

This checkpoint continues CP10 and freezes the current repository-cleanup decision surface. It does not modify the live Oracle V1 branch or its runtime state.

Observed live Oracle branch:

- `builder/oracle-economic-loop-recovery-20261019`
- observed HEAD during CP11 preparation: `291540c5d69f0f2b0638dab10ba61862e6715cc4`
- CP10 had observed `14479dc7649c6126420a9627ad8fec2147e2c335`
- the two later commits were bounded current-lineage validation progress (`VALIDATE-DOC-FUND-9219d7f488ada3c2`) and did not invalidate CP10's architecture/runtime reconciliation.

Observed audit branch input:

- `audit/forensic-checkpoint-20261019`
- CP10: `090076945ff4d3e8006757047bbc6d2716d2eea6`

## Repository state

The live branch inventory had re-expanded to approximately 227 branches before this cleanup pass.

That is materially inconsistent with the earlier September repository-hygiene closure, which had reduced the repository to roughly 40 branches after 34 verified deletions.

The current problem is therefore not only historical clutter. Branch sprawl re-accumulated after the previous cleanup.

## Cleanup objective

`MINIMIZE_ACTIVE_BRANCH_NAMESPACE_WITHOUT_INFORMATION_LOSS = TRUE`

Branch names are not scientific evidence. Exact commits, durable artifacts, governance decisions and reconstructable ancestry are.

The cleanup policy is therefore:

- retain a small live/source set as branches;
- delete strict ancestors of retained refs;
- collapse redundant refs;
- archive exact unique/diverged tips with immutable tags before deleting their branch refs;
- preserve a machine-readable branch -> SHA -> disposition receipt;
- refuse deletion if a branch moves after the plan is generated.

## Retained branch set — first pass

### KEEP_LIVE / ROUTING

- `blue/master-v2-2026-09-20` — temporary default/routing portal only
- `builder/oracle-economic-loop-recovery-20261019` — live Oracle V1
- `audit/forensic-checkpoint-20261019` — independent audit/V2 forensic baseline

### V2_SOURCE

- `builder/research-os-aggressive-architecture-20261015`
- `builder/research-factory-core-v2`
- `research/edge-lab-continuous`
- `research/legacy-economic-reconciliation-20261015`
- `research/design-v1`
- `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08`

### SCIENTIFIC_MEMORY / OWNER OVERRIDE

- `codex/test` — historical negative economic result
- `claude/restaurant-stock-management-mvp-6oq43e` — explicit Owner retention override, unrelated to Quant but intentionally retained

The set is intentionally small. Other historical branches are not declared worthless; their exact tips are archived when not already reachable from a retained branch.

## Verified absorbed modern Research OS rails

Independent GitHub ancestry checks established:

- `builder/research-os-autonomous-loop-20261015` -> strict ancestor of Oracle line
- `builder/research-os-autonomous-econ-readiness-port-20261016` -> strict ancestor of Oracle line
- `builder/research-os-econ-readiness-activation-20261017` -> strict ancestor of Oracle line
- `builder/econ-test-flow-ust-auction-20261019` -> strict ancestor of Oracle line

These branch refs are safe cleanup candidates because their commits remain reachable from the retained modern line.

## Verified diverged branches that must not be treated as absorbed

- `builder/research-os-aggressive-architecture-20261015` retained substantial unique history (84 commits unique in the inspected comparison).
- `builder/research-factory-core-v2` retained unique product/research-factory history (15 unique commits in the inspected comparison).
- `research/edge-lab-continuous` retained substantial unique Edge Lab history (170 unique commits in the inspected comparison).
- `research/legacy-economic-reconciliation-20261015` retained unique Legacy reconciliation history (102 unique commits in the inspected comparison).

These are retained V2 sources rather than cleanup noise.

## Historical side rails

`ops/oci-one-shot-install-20261019` and `builder/research-os-vm-autonomy-20261019` remain historically diverged by a small number of commits. Their useful concepts were substantially superseded/ported into the qualified Oracle line, but branch deletion should still preserve any unique tip first unless ancestry at execution time proves it absorbed.

## Weather V4 family

The repository currently exposes a very large Weather V4 branch family spanning Astra, Blue, Builder, Owner and Team refs. The branch namespace itself is no longer an acceptable long-term index of Weather evidence.

First-pass policy:

- retain `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08` as the compact working/source ref;
- archive unique Weather branch tips before branch deletion;
- preserve their exact mapping in the cleanup receipt;
- later V2 reconciliation decides what Weather capabilities/evidence are imported, rejected or kept only as scientific memory.

This is a branch-namespace decision, not a scientific verdict on Weather V4.

## Updated routing on default branch

The stale September routing surface has been replaced on `blue/master-v2-2026-09-20` by a current 2026-10-20 routing layer.

New/updated surfaces include:

- `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
- `governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`
- `scripts/repository_hygiene_20261020.sh`
- `README.md`
- `CLAUDE.md`
- `CODEX.md`
- `AGENTS.md`
- `CLAUDE_CURRENT_MISSION.md`
- `NEXT_BUILD_MISSION.md`

Default-branch HEAD after this routing update was observed as:

`a0b9ffb604f8cf7496ed998cb4f199d42ff8c10f`

`STATE.md` / `CHIEF_BRIEF.md` were intentionally not rewritten during this pass because they contain generated/runtime snapshot semantics. The new routers explicitly demote them from project-routing authority.

## Cleanup implementation

`scripts/repository_hygiene_20261020.sh` is dry-run by default.

It:

1. verifies the repository remote;
2. fetches/prunes refs and tags;
3. protects the explicit keep-set and current default branch;
4. classifies every other branch against retained ancestry;
5. marks strict ancestors `ABSORBED`;
6. assigns an exact archive tag `archive/20261020/tip-<sha12>` to non-absorbed historical tips;
7. emits a TSV plan;
8. in `APPLY=1` mode re-checks every remote branch SHA before mutation;
9. re-proves ancestry immediately before deleting `ABSORBED` refs;
10. pushes and verifies archive tags before deleting unique/diverged refs;
11. skips any branch whose tip changed after planning.

This is intentionally fail-closed under concurrent work.

## Authority boundary

No cleanup decision changes:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Branch deletion is namespace hygiene, not scientific or capital authority.

## CP11 verdict

`REPOSITORY_CLEANUP_READY_FOR_OWNER_TERMINAL_DRY_RUN = TRUE`

`LIVE_ORACLE_V1_MUTATED_BY_CLEANUP = FALSE`

`V2_CANONICAL_TRUNK = NOT_YET_DECLARED`

`UNIQUE_DIVERGED_HISTORY_MAY_BE_DELETED_WITHOUT_REACHABILITY_PRESERVATION = FALSE`

`MAXIMUM_SAFE_BRANCH_REDUCTION_STRATEGY = ABSORB_OR_ARCHIVE_THEN_DELETE`

Next durable evidence should be the generated cleanup TSV plus final post-cleanup branch count. Only after that should V2 source branches be imported/rejected and a canonical V2 trunk declared.