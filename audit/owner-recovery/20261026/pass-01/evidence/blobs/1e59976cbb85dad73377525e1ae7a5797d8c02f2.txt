# BUILDER CP012 — Bound producer-task observation

BRANCH: builder/v2-forward-20261020
BASE_SHA: 99bba9e16fa2bf830e3e13da7bcb4cd91dd77b58
GAP_CHECKPOINT: 0fbdfa382739986152256615885391d450ea8a2c
IMPLEMENTATION_SHA: b8d41b8a9111cc16ac1a7b3fb3ef129f4addcae7
QUALIFIED_CODE_SHA: 347e49ccd14ae595a8d9e99e0bcf5884698882d3
OBSERVED_ORACLE_HEAD: 076cf79013e3430fb86b7d9ab1d5bfd4c03c79fa
SAFE_TO_CONTINUE: TRUE

## Capability and scope

CP011 proved the collector gap left by CP002/CP010. Added
`expansion/edge_observation_reader_v2.py` and `scripts/observe_edge_task_v2.py`,
with 14 adversarial tests and inclusion in the existing Oracle V2 workflow.
The unused-import correction is the only change between the implementation and
qualified code commits. Existing worker/runtime/Site code was not modified.

The reader reuses Snapshot blob verification, V2StateStore's epoch/policy
preflight, canonical worker publication contracts, producer readiness and CP010.
It reads one producer task at one exact commit, its canonical research artifact
and, for an uncompleted/blocked stage, its own generation/session-bound receipt.
It verifies completed-stage content hashes, epoch and source-blob bindings,
candidate/family/lineage identity and closed authority. Source tree metadata may
be indexed; source content and evaluation paths are never read. There is no
handoff traversal or inference of Validator, portfolio or Site completion.

Blocked research, absent research, absent dossier and unsupported producer
readiness families remain explicit incomplete states. No dossier, route,
adapter, task or scientific support is invented. Explicit catalogs are optional
and cannot activate acquisition. Observation hashes bind HEAD, all consumed blob
identities, epoch/policy and the derived projection.

Offline usage (the state commit must already exist locally):

```sh
python scripts/observe_edge_task_v2.py --commit <full-state-SHA> --task-id <producer-task-ID>
```

Optional `--repository` selects another local checkout; `--catalog` supplies
explicit local route/validated-adapter JSON. The Git adapter issues only
rev-parse, ls-tree and cat-file. It neither fetches nor writes.

## Executed evidence

- Focused composition/bridge/reader suites: 41 PASS.
- Existing V2 workflow run steps locally on clean code SHA 347e49c: compilation,
  91/91 tests, closed policy, claim ceiling, fixture qualification and real
  GitHub-state dry-run all PASS. Dry-run: two fetches, zero state writes, zero
  push attempts or hosted-model calls.
- Independent hosted Oracle V2 run **39456856043**, job **118745886473**, exact
  SHA 347e49c: SUCCESS, all 13 job steps successful (including setup/upload).
- CP010's formerly unconfirmed Oracle V2 run **39453346342** on 4ffb880 is also
  confirmed SUCCESS. The API remains inaccessible, but the normal permitted
  github.com Actions pages expose exact commit IDs and step conclusions.
  No API proxy/policy bypass or new credentials were used; a network change is
  no longer required to inspect these public checks.
- Actual pinned Oracle tasks EVENT_DOCUMENT-010 and FUNDAMENTAL-010 project as
  upstream-blocked; INST-FLOW-010 changed from artifact-absent at 1e79d03 to
  upstream-blocked at 076cf79. Both observations are honest snapshot-specific
  facts. Traced Git commands and reads prove no network/write command and no
  source/evaluation content read; checkout HEAD and working tree were unchanged.
- One live test exposed the engine naming convention FUNDAMENTAL versus task
  type FUNDAMENTAL_RESEARCH. Fixed by consulting the existing engine registry,
  rather than introducing a parallel family map. Fixture regression passes.
- Real temporary Git repository/CLI test, blob tampering, stale/misrouted
  receipts, traversal, mixed epoch/policy, candidate/source mismatch,
  outcome/open authority, absent artifacts, determinism and immutability covered.
- Targeted Pyflakes and git diff whitespace checks PASS.

Evidence is in `BUILDER_CP_012_LOCAL_VALIDATION_20261020.json`; local command logs
remain in `/workspace/.setup/cp012-validation/`.

## SEC freshness failure and correction

Hosted SEC run 39456856070 failed specifically at **Status artifact freshness**;
its later full suite/demo steps were skipped, not failed or passed. The broad
local suite executed 651 tests: 650 passed, one detected that STATE.md still
advertised 602 tests. This inherited/generated inventory was already stale on
CP010 and became further stale after the new tests.

Use the repository's `scripts/status_artifacts.py --write` to refresh generated
reports, then rerun the failing gate/full regression. Do not weaken assertions,
disable the SEC workflow or change scientific data to manufacture success.
The subsequent qualification receipt records final outcomes separately.

## Authority and handoff

All four authorities FALSE; OUTCOME_ACCESSED FALSE; ECONOMIC_RESULT NOT_OBSERVED.
No Oracle/Site deployment, secret operation, source acquisition or autonomous
state mutation. Builder pushes persist code and evidence only. The Owner's
parallel Oracle → Site closure remains separate under CP16.

Final Integrator may import this read-only capability after checks complete.
It remains a producer-task view, not full lineage or deployed Site observability.
Do not silently normalize the conservative CP008 requirement-text firewall or
extend the unsupported Fundamental readiness contract in this increment.
Next: finish the generated inventory correction and qualify the resulting exact
commit, preserving the distinction between local and hosted checks.
