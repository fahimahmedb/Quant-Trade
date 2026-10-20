# CHECKPOINT 012 — Deep organizational audit for V2 repository consolidation

Recorded 2026-10-20 (Europe/Paris).

## Status

`CP12_DEEP_ORGANIZATIONAL_AUDIT = CURRENT`

`CP11_CLEANUP_POLICY = SUPERSEDED_PRELIMINARY`

`DESTRUCTIVE_BRANCH_CLEANUP_AUTHORIZED_BY_THIS_CHECKPOINT = FALSE`

This checkpoint supersedes CP11 as the current repository-cleanup decision surface. CP10 remains valid for the scientific/runtime reconciliation of CP7–CP9 against qualified Oracle V1. CP11 remains historical evidence of a preliminary branch-hygiene pass, but its keep-set and one-shot deletion proposal MUST NOT be used as deletion authority.

The reason for supersession is substantive: after CP11, a deeper reconstruction from the September Blue organizational/hygiene audits and current V2 branches showed that several branches previously treated as archive candidates still contain unique capabilities, Owner decisions, negative scientific results, or parallel product work not yet absorbed into V2.

---

## 1. Audit baseline and method

This audit resumes the observation-first method established by:

- `governance/BLUE_ORGANIZATIONAL_AUDIT_2026-09-20.md`;
- `governance/BLUE_REPOSITORY_HYGIENE_AUDIT_2026-09-21.md`;
- `governance/BRANCH_AUTHORITY_REGISTRY_2026-09-21.md`;
- `governance/BRANCH_CLEANUP_PLAN_2026-09-20.md`;
- `governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md`.

The governing historical principle is preserved:

> repository hygiene is authority clarity, not deletion count.

A branch is not classified only by age, name, commit count, or whether a later-looking branch exists. Classification requires, where material:

1. ancestry/reachability;
2. unique implementation capability;
3. scientific/economic result value, including negative results;
4. Owner/Blue/Astra governance evidence;
5. current live/runtime status;
6. whether the capability/result has been durably imported into the V2 target;
7. whether deleting the ref would make reconstruction materially harder;
8. current authority over destructive Git operations.

Old, rejected, failed, negative, or superseded work is not automatically disposable.

---

## 2. Current repository drift

The 2026-09 repository-hygiene closure had reduced the active branch namespace to roughly 40 branches after a verified 34-branch deletion tranche.

Current REST pagination on 2026-10-20 returns:

- page 1: 100 branches;
- page 2: 100 branches;
- page 3: 29 branches.

`CURRENT_BRANCH_COUNT = 229`

The namespace therefore re-expanded by approximately 189 branches after the previous cleanup.

This is not merely inherited clutter. It demonstrates a process-level failure: workstreams repeatedly created Builder/Blue/Astra/Owner/Claude/Research/Parallel/Team refs without a mandatory consolidation/retirement phase after the workstream reached a durable result.

V2 MUST therefore adopt branch lifecycle governance, not just perform a one-time purge.

---

## 3. Current live workstreams

### 3.1 Oracle H24 V1 — live qualified runtime

Branch:

`builder/oracle-economic-loop-recovery-20261019`

Observed during CP12:

`599315e77d9d474e7e61c586c1676792c0f98a8e`

Qualified V1 release remains:

`f3943830e20b05d926d3013501573b8b21fdace7`

Classification:

`LIVE_RUNTIME_V1`

V1 remains operationally qualified and continues to advance autonomously. It is evidence and a running subsystem, not the V2 trunk and not proof of economic edge.

Do not mutate or consolidate its live durable task/event/receipt state as part of repository hygiene.

### 3.2 Oracle V2 Core — active scientific architecture/build rail

Branch:

`builder/oracle-v2-core-20261020`

Observed HEAD:

`a313dbe57e47c7cf50802a4b8a118f0dc9e52097`

Classification:

`LIVE_V2_BUILD`

V2 Core is not a greenfield replacement package. It deliberately reuses the V1-qualified worker mechanics for fresh GitHub state, claim/lease, publication and recovery, while adding stricter scientific state and V2 stage execution.

Current key surfaces include:

- `research/research_os/oracle_worker_v2.py`;
- `research/research_os/scientific_store.py`;
- `research/research_os/expansion/v2_core.py`;
- `research/research_os/expansion/v2_bridge.py`;
- `research/research_os/expansion/v2_pipeline.py`;
- `research/research_os/expansion/v2_stage_executor.py`;
- `research/research_os/runtime/V2_CORE_POLICY.json`;
- `research/research_os/runtime/V2_ACTIVE_EPOCH.json`;
- `.github/workflows/oracle-v2-core.yml`.

V2 currently strengthens, among other things:

- Research Epoch binding;
- MODEL_PIT discipline;
- research/evaluation separation;
- trial/multiplicity accounting;
- validator sidecars and independence constraints;
- append-only scientific state;
- successor-only feedback intent;
- sealed outcome/evaluation membrane;
- current-lineage readiness context.

It is still `PRE_OUTCOME_RESEARCH_ONLY` and does not absorb every historically built capability.

### 3.3 Live Lab — active parallel product surface, currently split

Current relevant rails include:

- `builder/live-lab-oracle-canonical-20261020`;
- `builder/live-lab-oracle-integration-20261020`;
- historical but still semantically relevant `builder/live-lab-3d-full-build-20261015`.

Classification:

`LIVE_PARALLEL_PRODUCT / RECONCILIATION_REQUIRED`

The two current 2026-10-20 rails are diverged rather than one being a clean descendant of the other. The integration rail includes Oracle site bridge/native contract work; the canonical rail carries a broader subsequent UX/production/evidence line. The old WebGL PR #29 branch retains four unique commits relative to its old base and passed dedicated CI.

Therefore no single Live Lab branch may yet be declared the sole canonical survivor based on naming or date alone.

Required V2 action:

`LIVE_LAB_SEMANTIC_RECONCILIATION -> ONE_CANONICAL_PRODUCT_RAIL -> RETIRE_INTERMEDIATE_REFS`

---

## 4. V2 capabilities that are NOT yet absorbed

A key CP12 finding is that current V2 Core is a stronger scientific wrapper around the V1-qualified runtime, not a complete import of all valuable Product/Data/Research capabilities previously developed.

### 4.1 Research Factory Core

Branch:

`builder/research-factory-core-v2@ca8ffe439953b063fb9d049773ce0b6245958c7d`

Relation to V2 Core: diverged, 15 unique commits observed.

Known unique capabilities include:

- experiment registry/experiment infrastructure;
- power/geometry surfaces;
- `src/quant/factory/outcome_firewall.py`.

The historical Outcome Firewall is not cosmetic. It implements fail-closed outcome access with exact gate/protocol/dataset/lineage checks, restricted column roles, lexical/alias defenses and dataset hashing. The same file is absent from current V2 Core.

Classification:

`SOURCE_IMPORT_REQUIRED`

Do not archive-and-delete this branch until each unique capability is explicitly `IMPORTED`, `SUPERSEDED_WITH_PROOF`, or `REJECTED_BY_V2_DECISION`.

### 4.2 Evidence Store / Identity Data Plane

Branch:

`builder/evidence-store-identity-v2@b8f7dffbe040753cb1e47b7f38f3ab4485e1e7ba`

Relation to V2 Core: diverged, 22 unique commits observed.

Known unique capabilities include:

- evidence identity;
- PIT identity semantics;
- corporate-action/source identity structures;
- adversarial evidence tests.

Classification:

`SOURCE_IMPORT_REQUIRED`

### 4.3 SEC Form-4 Census

Branch:

`builder/sec-form4-census-v2a@08dcfc39b4b22e0b25e54edde7b6accbb2bc4502`

Relation to V2 Core: diverged, 67 unique commits observed.

Known unique capabilities include SEC/Form-4 product-side census, calendar/schema and associated tests.

Classification:

`SOURCE_IMPORT_REQUIRED`

### 4.4 Aggressive Research OS architecture

Branch:

`builder/research-os-aggressive-architecture-20261015`

Relation to V2 Core: diverged, 84 unique commits observed.

Classification:

`SOURCE_IMPORT_REQUIRED / SEMANTIC_REVIEW_REQUIRED`

Do not infer that V2 Core's later date supersedes this branch's architectural concepts.

---

## 5. Scientific memory sources not yet safely disposable

### 5.1 Edge Lab continuous

Branch:

`research/edge-lab-continuous`

Relation to V2 Core: diverged with 170 unique commits observed.

It contains durable discovery protocols, source/capture work, experiment contracts/results, negative results, prospective designs and platform-probe history.

Classification:

`SCIENTIFIC_MEMORY_REQUIRED + SOURCE_IMPORT_REQUIRED`

Required V2 action:

- construct a durable Edge scientific-memory index;
- import result identity/outcome status/exposure history into V2 negative/positive knowledge without pretending all records meet V2 protocol quality;
- preserve original SHAs and caveats;
- only then retire branch refs that no longer add discoverability.

### 5.2 Legacy economic reconciliation

Branch:

`research/legacy-economic-reconciliation-20261015@183ad65ff260b903a16548ce37948f54d47a9ec8`

Relation to V2 Core: diverged with 102 unique commits observed.

This line remains essential because V1 Legacy bootstrap being fail-closed does not mean historical reconciliation is complete. Current canonical status remains:

`PARTIAL_WITH_EXPLICIT_GAPS`

Classification:

`SCIENTIFIC_MEMORY_REQUIRED + SOURCE_IMPORT_REQUIRED`

### 5.3 Design V1

Branch:

`research/design-v1`

Relation to V2 Core: diverged with 20 unique commits observed.

Historical audit identified unique Alpha Factory, market-selection, abstention and launch-doctrine material.

Classification:

`ARCHITECTURE_SOURCE_REVIEW_REQUIRED`

### 5.4 codex/test

Branch:

`codex/test`

Relation to V2 Core: one unique commit observed.

The unique commit is scientifically material because it contains a historical negative/KILL result. Commit count is therefore not a proxy for value.

Classification:

`SCIENTIFIC_MEMORY_REQUIRED`

Before ref retirement, the result must be indexed into canonical negative knowledge with exact original SHA and limitations.

---

## 6. Edge/F1/F2 current PR history

Open PRs observed after closing the clearly obsolete coordination/proposal PRs #21–#23:

### PR #24 — F1 acquisition

Status: durable Stage-A capture/acquisition evidence.

Important state:

- complete capture evidence;
- checksums/provenance;
- acquisition only.

Classification:

`SCIENTIFIC_EVIDENCE_CHAIN`

### PR #25 — F1 discovery A

Observed result:

- selected theta 0.20;
- annualised mean 3.823%;
- Sharpe 0.490;
- robust t 0.957;
- doubled-cost mean 1.114%;
- below the assumed 4% cash comparator.

Status: discovery information, not sealed family verdict.

Classification:

`SCIENTIFIC_EVIDENCE_CHAIN`

### PR #26 — F1 sealed B verdict

Observed result:

- annual arithmetic mean: -1.356922%;
- Sharpe: -0.448546;
- doubled-cost mean: -2.957394%;
- `FAMILY_STATUS = REJECT`.

This is the final bounded family verdict for the fixed tested expression. It MUST remain durable negative knowledge. A/B must not be rerun simply to repair publication.

Classification:

`SCIENTIFIC_MEMORY_REQUIRED / FINAL_NEGATIVE_RESULT`

### PR #27 — F2 source permission

Status:

`BLOCKED_DATA_PERMISSION`

No statistical look was consumed. Official terms did not clear the intended credential-free historical research route.

Classification:

`SCIENTIFIC/ACCESS_MEMORY_REQUIRED`

### PR #28 — EURUSD range-grid

Status:

- frozen exploratory quote-proxy harness;
- no market ZIP/row/result/look acquired at the recorded freeze;
- no economic result yet.

Classification:

`FROZEN_UNEXECUTED_RESEARCH_MEMORY`

### PR #29 — Live Lab 3D

Status:

- functional WebGL/3D renderer;
- dedicated CI passed;
- four-commit isolated implementation;
- not automatically superseded by current Live Lab rails.

Classification:

`PRODUCT_CAPABILITY_RECONCILIATION_REQUIRED`

Repository hygiene should ultimately close stale PR routing surfaces after their durable state is imported/indexed, while preserving their commit/evidence history.

---

## 7. Weather V4 is a governance/evidence corpus, not one final branch

A preliminary CP11 keep selected:

`builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08@73280c3e9d8604b2f2d8e6d2d174aa940389a760`

Deep inspection changes its interpretation.

Its tip explicitly describes itself as a candidate only: not loaded, verified, reviewed or activated, with conditional execution authority not in effect.

The branch does, however, contain a valuable compact Weather V4 evidence corpus under `research/weather_forward/v4/`, including:

- archaeology/gold map;
- A2 harness;
- audits;
- Blue evidence;
- Owner decision documents.

The Owner directory contains explicit decisions including OD01–OD03, OD04–OD12, harness construction/suitability, bounded offline test authority, prerequisite attestations, partial configuration and later technical authorization/draft material.

Classification of the branch:

`OWNER_GOVERNANCE_REQUIRED + SCIENTIFIC_MEMORY_REQUIRED`

Classification of the wider Weather branch family:

`CONSOLIDATE_TO_CANONICAL_WEATHER_MEMORY_THEN_RETIRE_INTERMEDIATE_REFS`

The consolidation MUST distinguish ratified Owner decisions from drafts, conditional authorities, Builder output, Blue recommendations and Astra audits. No draft may be silently promoted to Owner authority merely to simplify cleanup.

---

## 8. Workflows / CI are part of repository clutter

The current V2 Core tree still carries many workflow generations simultaneously, including:

- V1 proof/runtime gates;
- Oracle V1 recovery CI;
- Oracle V2 Core CI;
- multiple Research OS architecture/depth/queue/workflow-lane gates;
- Edge Lab generic and candidate-specific workflows;
- Live Lab integration CI;
- SEC P0 pre-t0 gate;
- data-feed workflows;
- economic-readiness integration.

Therefore branch deletion alone cannot make the repository comprehensible.

Every workflow must be classified as one of:

- `ACTIVE_V1_RUNTIME_GUARD`;
- `ACTIVE_V2_BUILD_GUARD`;
- `ACTIVE_PARALLEL_PRODUCT_GUARD`;
- `HISTORICAL_PROOF_ONLY`;
- `CONSOLIDATE_INTO_V2_GATE`;
- `RETIRE_AFTER_CAPABILITY_IMPORT`.

A historical workflow may be removed from the active workflow directory after its evidence/role is indexed; Git history remains the replay surface. Keeping dozens of obsolete active workflows is itself an authority hazard.

---

## 9. Branch classes for the deep cleanup

CP12 replaces the shallow CP11 classes with semantic classes:

### `LIVE_RUNTIME_V1`
Running V1 state/runtime. Do not alter as hygiene.

### `LIVE_V2_BUILD`
Current V2 architecture/build rail. Protect while active.

### `LIVE_PARALLEL_PRODUCT`
Current product work such as Live Lab until reconciled.

### `SOURCE_IMPORT_REQUIRED`
Contains capability not yet proven absorbed by V2. Cannot be deleted merely after tagging.

### `SCIENTIFIC_MEMORY_REQUIRED`
Contains positive/negative/blocked/unexecuted research state that must first be represented in canonical V2 scientific memory.

### `OWNER_GOVERNANCE_REQUIRED`
Contains Owner decisions/authorities/drafts whose status must be normalized before branch retirement.

### `ABSORBED_REF_DELETE_READY`
Tip is a strict ancestor of retained authority and no unique semantic role remains. This is an informational classification only; CP12 does not authorize deletion.

### `ARCHIVE_AFTER_IMPORT`
Unique historical branch may lose its branch ref only after its material capabilities/results/decisions have been imported or explicitly rejected, and the exact tip remains reachable.

### `SUPERSEDED_ROUTING`
Old routers/handoffs that should not remain current navigation authority.

### `UNKNOWN_REVIEW_REQUIRED`
No destructive action until reviewed.

---

## 10. Known absorbed refs

The following modern Research OS rails were independently verified earlier as strict ancestors of the retained modern Oracle line and remain candidates for `ABSORBED_REF_DELETE_READY` after the semantic registry is complete:

- `builder/research-os-autonomous-loop-20261015`;
- `builder/research-os-autonomous-econ-readiness-port-20261016`;
- `builder/research-os-econ-readiness-activation-20261017`;
- `builder/econ-test-flow-ust-auction-20261019`.

This classification does not grant destructive authorization.

---

## 11. Default branch and routing debt

The repository default branch remains:

`blue/master-v2-2026-09-20`

It has accumulated later routing updates but remains a historical Blue-named branch rather than a clean V2 trunk.

Do not solve this by simply pointing the default branch at Oracle V1. V1 is a subsystem. Do not solve it by renaming an arbitrary V2 work branch either.

Required sequence:

1. complete source/memory/governance reconciliation;
2. identify the smallest coherent V2 canonical tree;
3. declare a V2 canonical trunk explicitly;
4. ensure V1 live runtime remains independently recoverable;
5. migrate project routing/default branch deliberately;
6. only then retire superseded routing refs.

---

## 12. Branch lifecycle rule required for V2

A new permanent governance rule is recommended for Owner adoption:

Every temporary Builder/Astra/Blue/Research branch MUST end in exactly one durable disposition:

- `MERGED_OR_ABSORBED`;
- `CAPABILITY_IMPORTED`;
- `SCIENTIFIC_MEMORY_INDEXED`;
- `OWNER_DECISION_INDEXED`;
- `EXPLICITLY_REJECTED_WITH_REASON`;
- `ACTIVE_AND_NAMED_IN_CURRENT_WORKSTREAM_INDEX`.

No completed workstream may leave an indefinite tree of intermediate branches without a consolidation checkpoint.

This is necessary because the branch count grew from roughly 40 to 229 despite the prior successful cleanup.

---

## 13. Authority boundaries

Nothing in CP12 opens any economic authority.

Remain CLOSED:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`;
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`;
- `REAL_CAPITAL_AUTHORIZED = FALSE`;
- `LIVE_TRADING_AUTHORIZED = FALSE`;
- real capital allocation / position sizing / order authority = FALSE.

Current V2 policy also explicitly states:

`destructive_git_operations_authorized = false`

Therefore CP12 prepares a cleanup and consolidation program but does NOT authorize agents to physically delete branch refs.

The prior P0-D requirement for mandatory server-side branch protection/rulesets has been lifted by explicit Owner decision in current V2 governance. That does not weaken scientific review/audit requirements and does not imply destructive branch cleanup authority.

---

## 14. CP12 verdict

`V1_LIVE_BASELINE = PRESERVE`

`V2_CORE = LIVE_BUILD_BUT_NOT_FULL_HISTORICAL_CAPABILITY_ABSORPTION`

`LIVE_LAB = RECONCILIATION_REQUIRED`

`WEATHER_V4 = CONSOLIDATE_OWNER_AND_SCIENTIFIC_MEMORY_BEFORE_REF_RETIREMENT`

`EDGE_LAB = IMPORT_SCIENTIFIC_MEMORY_BEFORE_REF_RETIREMENT`

`LEGACY_RECONCILIATION = IMPORT_REQUIRED / STILL_PARTIAL_WITH_EXPLICIT_GAPS`

`RESEARCH_FACTORY_CORE = SOURCE_IMPORT_REQUIRED`

`EVIDENCE_IDENTITY_DATA_PLANE = SOURCE_IMPORT_REQUIRED`

`SEC_FORM4_CENSUS = SOURCE_IMPORT_REQUIRED`

`OPEN_EDGE_PRS = DURABLE_EVIDENCE_TO_INDEX, NOT ACTIVE_PROJECT_ROUTING`

`ACTIVE_WORKFLOW_SPRAWL = GOVERNANCE_DEBT`

`CURRENT_BRANCH_COUNT = 229`

`CP11_ONE_SHOT_BRANCH_DELETE = DO_NOT_RUN`

`NEXT_PHASE = BUILD_CANONICAL_REGISTRIES -> IMPORT/REJECT UNIQUE CAPABILITIES -> CONSOLIDATE SCIENTIFIC_MEMORY/OWNER_DECISIONS -> DECLARE V2 TRUNK -> PREPARE OWNER-EXECUTED DELETION PLAN`

The final cleanup target is not a specific branch count. The target is a repository where every remaining active branch has an explicit current role, every retired branch's unique information is durably represented, project routing is singular, and V2 can progress without rediscovering or accidentally discarding prior work.