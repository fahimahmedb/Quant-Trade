# REPOSITORY HYGIENE V2 — 2026-10-20

Authority: current repository-hygiene procedure under `governance/CURRENT_PROJECT_STATE_2026-10-20.md`.

## Objective

Reduce the active GitHub branch namespace as far as reasonably possible **without losing reconstructable scientific, governance, audit or implementation history**.

This cleanup is intentionally more aggressive than the September pass because the repository has re-expanded to roughly 227 branches.

The goal is not to preserve branch names. The goal is to preserve information.

## Core rule

For every non-retained branch, exactly one of these must be true before its remote branch ref is deleted:

1. its tip is already reachable from a retained branch (`ABSORBED`), or
2. the same tip is reachable from another retained ref (`REDUNDANT_REF`), or
3. its exact tip is first preserved by an immutable archive tag (`ARCHIVE_THEN_DELETE`).

A branch that changes after planning is skipped rather than deleted.

## Retained active/source branches

The first cleanup pass intentionally keeps this compact set as branch refs:

- `blue/master-v2-2026-09-20` — current default/routing portal during migration
- `builder/oracle-economic-loop-recovery-20261019` — live Oracle V1 runtime line
- `audit/forensic-checkpoint-20261019` — independent audit / V2 forensic baseline
- `builder/research-os-aggressive-architecture-20261015` — unique Research OS architecture source
- `builder/research-factory-core-v2` — unique Research Factory/product capability source
- `research/edge-lab-continuous` — unique Edge Lab research history
- `research/legacy-economic-reconciliation-20261015` — unique Legacy reconciliation source
- `research/design-v1` — design / Alpha Factory reference
- `codex/test` — negative economic/scientific memory
- `builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08` — compact Weather V4 source branch while V2 extraction is unresolved
- `claude/restaurant-stock-management-mvp-6oq43e` — explicit historical Owner retention override, if the branch still exists

This keep-set is deliberately small. Other historical Blue/Astra/Builder/Owner/parallel branches are not assumed worthless; unique tips are archived before branch deletion.

## Already verified absorbed modern rails

The 2026-10-20 audit independently verified these as strict ancestors of the modern Oracle line and therefore branch-ref deletion candidates without an archive tag:

- `builder/research-os-autonomous-loop-20261015`
- `builder/research-os-autonomous-econ-readiness-port-20261016`
- `builder/research-os-econ-readiness-activation-20261017`
- `builder/econ-test-flow-ust-auction-20261019`

Additional absorbed branches are discovered dynamically by the cleanup script against the retained branch set.

## Known diverged source rails

Do not treat these as absorbed merely because newer work exists:

- `builder/research-os-aggressive-architecture-20261015`
- `builder/research-factory-core-v2`
- `research/edge-lab-continuous`
- `research/legacy-economic-reconciliation-20261015`

They remain retained V2 sources.

Historical side rails such as:

- `ops/oci-one-shot-install-20261019`
- `builder/research-os-vm-autonomy-20261019`

may still have unique commits. The cleanup script therefore archives their exact tips before deleting their branch refs unless ancestry proves them absorbed at execution time.

## Why archive tags are used

A branch is a working namespace. A historical proof does not need to remain a working branch forever.

For a unique historical tip, the cleanup script creates a lightweight tag under:

`archive/20261020/tip-<sha12>`

The generated TSV manifest maps every deleted branch to its exact pre-delete SHA and archive tag/classification.

This preserves Git reachability while removing the branch from the active namespace.

Archive tags do **not** convert historical work into current authority.

## Execution tool

Use:

`scripts/repository_hygiene_20261020.sh`

The script is dry-run by default.

### 1. Refresh your local clone

```bash
git fetch origin --prune --tags
```

### 2. Review the plan

```bash
bash scripts/repository_hygiene_20261020.sh
```

The script emits a TSV plan containing:

- branch
- expected tip SHA
- classification
- retained witness or archive tag

### 3. Apply

Only after reviewing the dry run:

```bash
APPLY=1 bash scripts/repository_hygiene_20261020.sh
```

For every deletion the script re-reads the remote branch tip. If it differs from the planned SHA, it prints `SKIP_CHANGED` and refuses deletion.

For every `ARCHIVE_THEN_DELETE` branch, the archive tag is pushed and verified before the branch deletion is attempted.

## Expected outcome

The active branch namespace should collapse from roughly 227 branches to approximately the explicit keep-set plus any branch that cannot be safely processed due to concurrent movement or server protection.

This is intentionally **not** a deletion of Git history. It is a deletion/consolidation of branch refs.

## After cleanup

1. commit the generated cleanup TSV under `governance/cleanup_receipts/`;
2. record the final branch count;
3. re-run CP10/CP11 branch-source checks;
4. decide the canonical V2 trunk only after V2-source reconciliation;
5. once V2 has imported or explicitly rejected the retained source branches, a second cleanup can archive/delete those source refs too;
6. migrate the GitHub default branch only after the V2 trunk is explicitly declared.

## Non-goals / safety

This cleanup does not:

- change economic/scientific verdicts;
- authorize experiments or prospective observation;
- authorize real capital or live trading;
- rewrite Legacy history;
- merge Oracle V1 into a future V2 trunk;
- declare V2 complete;
- treat branch deletion as evidence deletion.
