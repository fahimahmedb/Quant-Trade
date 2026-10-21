# Horizontal CP002 — task-state closure and regression

BASE_SHA=01c2e520fa4116645870f96acf6770ea83f1881c
HEAD_SHA=30bd72452273afb3e8177939b969e4d3a540caf7
REPAIR_SHA=2fdf893568352966a8e20106ec940e1fb1688620
BRANCH=codex/horizontal-completeness-prewave2-20261021

Modules reviewed: control plane, task/lease/permission/budget, worker, durable
receipts and recovery. Expected surfaces and baseline reproduction are in CP001.

Surfaces found: existing generation-fenced task ledger, canonical routes,
capability/authority checks, bounded model budget, stage prefix/retry history,
atomic event/artifact/receipt/task publication, no-work wake persistence and
source-aware frontier stewardship. The V2 worker reuses those mechanics.

Current missing surfaces: H001/H002 are closed. FAILED now contributes to terminal
accounting. Unknown/unsupported/missing task state contributes to `unknown_count`
and yields `BLOCKED_UNKNOWN_TASK_STATUS` from refill, with no derived task. The
existing idle path durably records this refusal. Known active work selection is
unchanged; the new guard is scoped to an attempted refill. Historical KILLED stays
recognized; CANCELLED is represented but no cancellation producer is inferred.

Repairs: one existing queue module, six meaningful new test methods across three
existing test modules; no new runtime authority or orchestration implementation.
The real-Git test proves block persistence, restart and later legitimate followup
after recognized-state correction. The V2 test proves the source-aware path also
persists the block without ideation or artifact production.

Future Wave-2 surfaces: E cancellation production, final task/runtime operations,
restart outbox and whole-lifecycle operational recovery remain review questions.
Do not infer these are delivered by terminal enum presence.

Cross-axis findings: no new confirmed Vertical or Longitudinal defect. Existing
lease/replay mechanics were inspected only far enough to establish their surfaces.

Validation:

| Check | Result |
| --- | --- |
| Pre-repair contract/unknown/durable-state controls | Expected failure, 5 methods; archived log includes subtest failures |
| Focused queue, worker, V2 worker and source planner | 52 passed |
| Full root suite | 809 passed |
| Broader Research OS | 273 passed |
| Shared Python Live Lab contract | 2 passed; overlaps broader suite |
| Live Lab JavaScript | 57 passed |
| Existing V1 disposable end-to-end replay | 35/35 checks passed |
| Generated schemas | No drift |
| Generated status | Fresh STATE.md and CHIEF_BRIEF.md |
| Changed Python compile / Git whitespace | Passed |

Root and Research OS suites overlap through invoked helpers; counts are not an
independent sample and must not be summed into a qualification claim. Test
results, source hashes, exact commands and gzip logs are in
`HORIZONTAL_VALIDATION_20261021.json` and `evidence/`.

The initial Research OS run had 1 failure, 3 errors and 1 skip because the pinned
historical ledger had not been materialized. Its exact source/blob was fetched
and verified using the existing workflow prerequisite; all 273 then passed with
no skip. The first post-change root run exposed the expected stale proof count.
`scripts/status_artifacts.py --write` changed only 808 to 809 in STATE.md;
CHIEF_BRIEF.md and every economic/status value stayed byte-identical. The final
full root suite and freshness check passed. These setup failures are preserved,
not recast as current architectural gaps.

Reproduction prerequisite (repository root):

```sh
git fetch --no-tags origin 183ad65ff260b903a16548ce37948f54d47a9ec8
git show 183ad65ff260b903a16548ce37948f54d47a9ec8:LEGACY_RESEARCH_LEDGER.json > research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json
git hash-object research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json
# Must equal ba9b165aaf96956776672df51233bb9bf1e6cbc9 before testing.
PYTHONPATH=src:. python -m unittest discover -s tests -v
PYTHONPATH=src:. python -m unittest discover -s research/research_os/tests -v
node --test research/live_lab_ux/tests/*.test.js
```

The temporary ledger is a test prerequisite, not a new canonical-memory import.
The run did not deploy a release, mutate live scientific state, call a production
model, acquire market observations or enable economic dispatch. Exact local source
qualification does not imply a hosted CI result on this branch.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
SAFE_TO_CONTINUE=TRUE
