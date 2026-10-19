# Forensic Audit Continuation — Checkpoint 006

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent audit head: `acf6bbf7adc4d091c9716423cc4178b6f400493f`
Status: `PARTIAL_IN_PROGRESS`

## Correction to Checkpoint 005

Checkpoint 005 correctly established that the Git tree at `d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec` does not contain `research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json`, and that `LegacyKnowledgeBase.load()` silently falls back to an empty record set when the file is absent.

However, the broad implication that the modern automated gate is necessarily unpopulated at runtime is **too strong** and is corrected here.

The CI workflows prove an intended ephemeral materialization path that was not yet included in CP5's first conclusion.

This checkpoint supersedes CP5 only on that runtime-population interpretation. All other CP5 findings remain in force unless explicitly changed below.

## 1. Multi-engine CI explicitly materializes the pinned Legacy ledger

Workflow:

`.github/workflows/research-os-multi-engine-ci.yml`

At modern Research OS reference `d0dc70f...`, it performs the following before running the multi-engine pipeline:

1. shallow-fetch exact Legacy commit:
   `183ad65ff260b903a16548ce37948f54d47a9ec8`
2. materialize:
   `LEGACY_RESEARCH_LEDGER.json`
   into:
   `research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json`
3. verify Git blob hash exactly equals:
   `ba9b165aaf96956776672df51233bb9bf1e6cbc9`
4. parse JSON and assert:
   - schema version is `legacy-research-ledger-v1`
   - historical result immutability is `true`
   - `REAL_CAPITAL_AUTHORIZED` is `false`
   - `LIVE_TRADING_AUTHORIZED` is `false`
5. run the multi-engine pipeline
6. assert the generated pipeline result has:
   `legacy.summary.loaded_record_count > 0`

Therefore:

`MULTI_ENGINE_CI_LEGACY_BOOTSTRAP = PROVEN`

and:

`MULTI_ENGINE_CI_EMPTY_LEGACY_GATE = FALSE`

## 2. Economic-readiness integration CI independently uses the same bootstrap

Workflow:

`.github/workflows/economic-readiness-integration-ci.yml`

It also:

- fetches exact commit `183ad65...`;
- materializes the same `LEGACY_RESEARCH_LEDGER.imported.json`;
- verifies the exact same ledger blob SHA `ba9b165...`;
- then runs B1-B5 integration/regression tests.

This independently confirms that the absent file in the Git tree is an **ephemeral runtime dependency in CI**, not sufficient evidence that all automated executions used an empty ledger.

## 3. Source-manifest / loader design chronology

The manifest was introduced in commit:

`390607ace4f4ec2f833227d31fed38266f234a53`

message:

`research os: pin reconciled legacy corpus`

That commit added only:

`research/research_os/legacy/source_manifest.json`

The next commit:

`fa0486291ca13821a667250f8a5ac2a02abc6713`

message:

`research os: add pinned legacy anti-restart gate`

added only:

`research/research_os/legacy.py`

The ledger itself was intentionally/notably not committed into this lineage, while later CI materializes it from the pinned commit.

Forensic interpretation:

`LEGACY_STORAGE_MODEL = PINNED_EXTERNAL_COMMIT_PLUS_EPHEMERAL_MATERIALIZATION`

## 4. Residual fail-open defect remains real

The correction above does **not** remove the loader defect.

`LegacyKnowledgeBase.load()` still behaves as follows when the expected materialized ledger is absent:

- no exception;
- `ledger = None`;
- constructor substitutes empty records;
- screening proceeds with zero historical records.

It does not enforce:

- the manifest's declared `historical_research_items_found = 33`;
- exact manifest blob materialization before screen;
- nonzero record count as a loader invariant.

Therefore:

`LEGACY_LOADER_MISSING_LEDGER_FAIL_CLOSED = FALSE`

This matters anywhere the caller is **not** one of the proven CI jobs that explicitly materialize and verify the corpus first.

## 5. Scheduled external-worker protocol does not encode the bootstrap

`research/research_os/runtime/SCHEDULED_WORKER_PROTOCOL.md` explicitly requires:

- fresh GitHub reconstruction on every wake;
- Legacy screening before a CandidateHypothesis freeze;
- all authority boundaries to remain closed.

But the protocol does **not** specify the concrete Legacy-corpus bootstrap used by CI:

- no exact Legacy commit to fetch;
- no exact ledger path to materialize;
- no expected blob SHA;
- no required record count;
- no fail-closed behavior if materialization fails.

Thus the contract says **what scientific gate is required**, but not **how the external worker proves that the gate is actually populated**.

Forensic classification:

`EXTERNAL_WORKER_LEGACY_BOOTSTRAP_CONTRACT_COMPLETE = FALSE`

## 6. Queue-replenishment CI is not a substitute

`research-os-queue-replenishment-ci.yml` verifies that a derived producer task carries `legacy_gate_required = true` and that queue-refill authority stays closed.

It does not materialize the Legacy ledger, because it tests task derivation rather than candidate screening.

Therefore the presence of the flag in a derived task does not itself prove that a later external producer wake has loaded the historical corpus.

## 7. Corrected severity statement

Superseded CP5 statement:

`ANTI_RESTART_GATE_RUNTIME_POPULATED = FALSE`

Corrected statement:

- `ANTI_RESTART_GATE_POPULATED_IN_PROVEN_MULTI_ENGINE_CI = TRUE`
- `ANTI_RESTART_GATE_POPULATED_IN_PROVEN_ECON_READINESS_CI = TRUE`
- `ANTI_RESTART_GATE_POPULATED_FOR_ARBITRARY_EXTERNAL_WORKER_WAKE = NOT_PROVEN`
- `LEGACY_LOADER_FAILS_CLOSED_IF_BOOTSTRAP_MISSING = FALSE`

The blocker for Oracle is therefore **preflight completeness**, not absence of all functioning Legacy integration.

## 8. Oracle/OCI implication

Any future Oracle wake/bootstrap that executes Research OS candidate work must reproduce the proven CI safety preflight, at minimum:

1. fetch exact pinned Legacy commit;
2. materialize exact ledger path;
3. verify exact blob SHA;
4. verify schema/governance immutability flags;
5. verify expected/nonzero record count;
6. only then permit Legacy screening or candidate freeze;
7. fail closed on any mismatch or unavailable source.

This requirement is audit-derived. It is **not implemented by this audit**.

Oracle must not merely clone the modern branch and invoke `LegacyKnowledgeBase.load()`.

## 9. PR #1 remains outside the proven CI corpus

Even when the 33-record pinned corpus is correctly materialized, the manifest itself is:

`PARTIAL_WITH_EXPLICIT_GAPS`

and the reviewed PR #1 lineage is not represented by exact coverage of its major families.

Therefore successful 33-record materialization fixes only the old gate's availability. It does not solve PR #1 scientific-memory completeness.

## 10. Current corrected verdict

- `MULTI_ENGINE_CI_LEGACY_BOOTSTRAP = PROVEN`
- `ECON_READINESS_CI_LEGACY_BOOTSTRAP = PROVEN`
- `LEGACY_STORAGE_MODEL = PINNED_EXTERNAL_COMMIT_PLUS_EPHEMERAL_MATERIALIZATION`
- `LEGACY_LOADER_MISSING_LEDGER_FAIL_CLOSED = FALSE`
- `EXTERNAL_WORKER_LEGACY_BOOTSTRAP_CONTRACT_COMPLETE = FALSE`
- `ARBITRARY_EXTERNAL_WAKE_LEGACY_POPULATION = NOT_PROVEN`
- `PINNED_33_ITEM_CORPUS_COMPLETE_FOR_PR1 = FALSE`
- `PR1_OPERATIONAL_LEDGER_MIGRATION_AUTHORIZED = FALSE`
- `AUTHORITY_PRECEDENCE_CONFLICT = TRUE`
- `ORACLE_AUTONOMOUS_ACTIVATION_SAFE = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Next forensic work

1. Audit structural portfolio/economic-identity handling of the ASML collision and other related-exposure pairs.
2. Determine whether any Oracle/OCI or external-worker branch already contains the proven Legacy materialization preflight.
3. Build an audit-only proposed Legacy-v2 migration/crosswalk that includes PR #1 without changing historical verdicts.
4. Trace authority precedence for the UST post-freeze receipt separately from scientific-memory repair.
