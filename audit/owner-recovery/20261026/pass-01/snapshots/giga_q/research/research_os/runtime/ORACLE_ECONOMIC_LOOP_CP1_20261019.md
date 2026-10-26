# Oracle Economic Loop Recovery — CP1 Verified Deployment Reconciliation

Date: 2026-10-19
Branch: `builder/oracle-economic-loop-recovery-20261019`

## Status

`CP1 = VERIFIED_FOR_CODE_AND_CI`

`LIVE_OCI_INSTALL_EXECUTED = FALSE`

`SCHEDULER_STARTED = FALSE`

`ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`LIVE_TRADING_AUTHORIZED = FALSE`

## Exact verified head

The dedicated Oracle recovery CI executed on:

`2539fb5c27ca526298f78a1daa71027dea66b791`

GitHub Actions run:

`39260609874`

Job:

`cp1-static-and-regression`

Conclusion:

`success`

## What the CI proved

The exact-head job completed successfully for all of the following:

1. Python 3.12 setup.
2. `py_compile` for:
   - `deploy/oracle_release_install.py`
   - `deploy/oci_research_os_deploy.py`
   - `tests/test_oracle_release_install.py`
   - `tests/test_oci_research_os_deploy.py`
3. Oracle recovery unit tests.
4. Existing pre-outcome Research OS regression suites used by the installer:
   - implementability depth
   - frozen experiment protocol
   - economic readiness validation
   - economic identity / portfolio readiness
   - producer economic readiness
   - economic readiness integration
   - queue replenishment
5. Static assertion that CP1 deploy scripts contain no scheduler activation surface.

No live Oracle host execution is claimed by this checkpoint.

## Reconciled deployment design

CP1 deliberately did not merge `ops/oci-one-shot-install-20261019` wholesale.

Reusable properties were selectively carried forward:

- content-addressed release by exact Git SHA;
- exclusive installation lock;
- OCI CLI error handling that does not convert failed/empty GETs into success;
- VM-bound narrow Run Command IAM design;
- durable command resume state;
- atomic receipts;
- pre-outcome verification before publication.

Stale properties were removed:

- no hard-coded old deployment SHA;
- no hard-coded VM OCID;
- no synthetic Legacy fixture as a substitute for the real pinned Legacy corpus;
- no oversized embedded full installer payload;
- no scheduler activation.

## Release installer contract

`deploy/oracle_release_install.py`

requires an exact 40-hex SHA and performs, before release publication:

1. download exact repository archive;
2. read `research/research_os/legacy/source_manifest.json`;
3. fetch the exact pinned Legacy ledger from its pinned source commit;
4. verify Git blob SHA exactly;
5. verify Legacy schema;
6. verify historical-result immutability;
7. verify real-capital and live-trading governance remain false;
8. require a non-empty materialized Legacy ledger;
9. materialize `LEGACY_RESEARCH_LEDGER.imported.json`;
10. validate current control-plane authority;
11. run bounded pre-outcome Research OS regression tests;
12. run a readiness smoke using the real materialized Legacy corpus;
13. write a release-local verified receipt;
14. atomically publish the SHA-addressed release;
15. atomically publish/recover the global installation pointer.

The manifest field `historical_research_items_found = 33` is preserved as a reconciliation-census fact. It is **not** incorrectly treated as a proven one-to-one record count. The receipt records both the manifest census and the actual parsed record count.

## Crash-recovery property

The release-local receipt is written before the release directory is atomically renamed into place.

Therefore, if interruption occurs after release publication but before the global `installed.json` pointer is updated, a later invocation can validate the release-local receipt and reconstruct the global pointer without reinstalling or silently accepting unknown state.

## OCI orchestrator contract

`deploy/oci_research_os_deploy.py`

requires explicit:

- `--vm <instance OCID>`
- `--sha <exact 40-hex commit>`
- region

and preserves:

- narrow per-instance Run Command IAM;
- command-state reuse keyed by VM + SHA;
- fail-closed OCI response handling;
- SSH-first optional delivery with OCI Run Command fallback;
- scheduler disabled.

The remote bootstrap is intentionally small and loads the versioned installer from the exact target SHA rather than embedding an independent deployment implementation.

## What CP1 does not prove

CP1 does **not** prove:

- that the current Oracle VM can download/install the new release in its actual network environment;
- that OCI IAM propagation is currently complete;
- that the Instance Agent accepts the new command on the real VM;
- that a scheduled worker service exists;
- that a scheduled worker can claim/execute Research OS tasks;
- that current-frozen hypothesis deduplication is complete;
- that PR #1 has been migrated into the operational Legacy corpus;
- that UST authority precedence has been repaired.

Those remain later-stage concerns.

## CP2 entry conditions

CP2 may now build the canonical scheduled-worker binding, but it must preserve all audit findings from CP7-CP9.

In particular, before a discovery/freeze-capable wake can proceed it must prove:

1. real pinned Legacy corpus loaded and verified;
2. current frozen hypothesis corpus snapshotted;
3. supported hypothesis schemas normalized or fail closed;
4. anti-redetection / same-exposure state resolved;
5. task authority and lease valid;
6. all four hard economic/live authority flags remain false.

A scheduler must not be enabled merely because CP1 is green.
