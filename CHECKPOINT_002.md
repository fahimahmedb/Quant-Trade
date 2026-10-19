# Forensic Audit Continuation — Checkpoint 002

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent checkpoint: `d95b52feb0c0fd75b33d1140c89ed4fc9c355489`
Status: `PARTIAL_IN_PROGRESS`

## Purpose

Continue the independent forensic audit after the original Codex workspace became unavailable. This checkpoint is a remote reconstruction and delta review. It does **not** claim recovery of the unpublished local mirror/bundle or the raw GitHub collections referenced by checkpoint 001.

No project code, scheduler, worker, workflow, experiment, live host or trading authorization is added by this checkpoint.

## Governance preserved

- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- No new economic experiment is authorized by this audit.
- No sealed outcome was intentionally opened by this continuation.
- No project script or economic backtest was executed by this continuation.
- This audit branch remains non-operational and MUST NOT be merged as project runtime.

## Remote branch delta since checkpoint 001

Checkpoint 001 recorded 221 branches. A complete current GitHub branch listing now ends on page 3 (page 4 is empty) and contains 226 branches.

The five branch names absent from the initial 221-branch inventory and now present are:

1. `audit/forensic-checkpoint-20261019`
   - prior published audit head: `d95b52feb0c0fd75b33d1140c89ed4fc9c355489`
2. `ops/oci-one-shot-install-20261019`
   - current head observed: `6e8ea155b05086f8e5eabcf830a5f835d3e3d09c`
3. `builder/research-os-vm-autonomy-20261019`
   - current head observed: `8a1bdadc9bc52c4889ee19d0472bcee61fe24318`
4. `builder/econ-test-flow-ust-auction-20261019`
   - current head observed: `ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`
5. `builder/oracle-economic-loop-recovery-20261019`
   - current head observed: `d69298b70c832955cf3bac7e0475dc7208412fc5`

No deletion is inferred from the branch-count delta: 221 + 5 = 226. A later final delta must still re-read all refs before closure.

### Existing moving data branch

`claude/data-feeds-6vr22g` existed in checkpoint 001 at:

`55066ed4322f51798a3252a90e976e01d3281276`

It is currently observed at:

`fc243f9a786e13220fe283c5bd0a6d74f7def5b5`

The two-commit delta observed between those SHAs modifies only append-style feed data / run-log files, not code:

- `data/feeds/_runs.jsonl`
- `data/feeds/odds/pinnacle_h2h/2026-10.jsonl`
- `data/feeds/odds/plans/2026-10.jsonl`
- `data/feeds/odds/requests/2026-10.jsonl`
- `data/feeds/sports_quotes/kalshi/2026-10.jsonl`
- `data/feeds/sports_quotes/matches/2026-10.jsonl`
- `data/feeds/sports_quotes/polymarket/2026-10.jsonl`

Classification at this checkpoint: **data-acquisition delta, not code evolution**, while the branch remains operationally relevant because existing workflow surfaces may consume it.

## OCI branch: ancestry risk confirmed

Compared with modern Research OS commit:

`d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

`ops/oci-one-shot-install-20261019` at `6e8ea155...` is **diverged**:

- merge base: `e980d201d3c84d16d7d91fde0d27a06c9a2c3121`
- OCI side ahead: 3 commits
- OCI side behind modern Research OS: 55 commits
- OCI-specific changed files observed from the merge base:
  - `deploy/oci_one_shot.py`
  - `tests/test_oci_one_shot_install.py`

Forensic implication: the OCI branch MUST NOT be treated as a canonical base or wholesale-merged into the modern Research OS. Its OCI surfaces must be reviewed as a selective patch set.

Observed useful properties in the latest OCI commits include fail-closed OCI CLI handling, explicit malformed/empty-response handling, instance-scoped Run Command IAM repair, reuse of checkpointed resources and tests against silent resource duplication. These are properties to preserve if later integration is authorized; this audit does not perform that integration.

## Modern Oracle / economic rails

### VM autonomy branch

Compared with `d0dc70f5...`, `builder/research-os-vm-autonomy-20261019` is exactly one commit ahead and adds only:

`research/research_os/runtime/VM_AUTONOMY_CHECKPOINT_20261019.md`

No runtime implementation is added by that branch relative to the modern Research OS baseline.

### UST economic-test branch

Compared with `d0dc70f5...`, `builder/econ-test-flow-ust-auction-20261019` is five commits ahead and adds only the following observed surfaces:

- `research/research_os/architecture/work_receipts/ECON_TEST_FLOW_UST_AUCTION_CP1_20261019.json`
- `research/research_os/architecture/work_receipts/ECON_TEST_FLOW_UST_AUCTION_CP2_POST_FREEZE.json`
- `research/research_os/artifacts/FLOW-UST-PRIMARY-DEALER-AUCTION-001/frozen-economic-screen-v1.json`
- `research/research_os/assessments/VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001.json`
- `research/research_os/tasks/VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001.json`

No Oracle scheduler/worker implementation is introduced by this five-commit delta.

### Oracle economic-loop recovery branch

`builder/oracle-economic-loop-recovery-20261019` is exactly one commit ahead of the UST branch and adds only:

`research/research_os/runtime/ORACLE_ECONOMIC_LOOP_RECOVERY_20261019.md`

Forensic implication at this checkpoint: the interrupted Oracle↔economic-loop work had reached documented intent / deployment preparation / economic artifacts, but the observed modern branches do not yet contain the final scheduler-to-canonical-economic-executor wiring.

## PR #1 scientific lineage — scope escalation

PR #1 is closed and not merged, with head:

`c60c8ab20b3f08add097e25e7295ba1196b0e4a6`

and base:

`35cf6d626e979e24b2784d9e2e8cc5ba94bb7f4e`

A direct Git comparison reports the PR head **700 commits ahead** of its base. This is therefore not a small discarded PR; it is a substantial historical scientific lineage containing research surfaces not reachable from current branch tips and it remains mandatory audit scope.

Observed scientific content includes a 110-cycle non-ML backlog, pre-registrations, backtest results, adversarial audits, PEAD work, SPA/DSR multiple-testing correction, robustness reports and older model research.

### PEAD chronology

Pre-registration path history identifies:

`64e95ff35d336c1641fa1550c91119f6ec7f104d`

at `2026-07-28T06:52:21Z`.

The result path history identifies:

`39d5f9c8e9112a067b1d32c5942373cfc7c2660d`

at `2026-07-28T07:57:33Z`.

Therefore the repository chronology supports the claim that PEAD was pre-registered before the recorded result.

However, the PEAD specification uses surprise tercile thresholds derived from the full 2021-2026 surprise distribution. Its own adversarial audit reports that 5.2% of comparable events change long/short/ignored assignment when causal expanding thresholds are used instead.

Audit classification at this checkpoint:

- pre-registration ordering: **SUPPORTED**
- strict point-in-time / causal cleanliness of the primary PEAD implementation: **NOT CLEAN / QUALIFIED**
- recorded primary verdict: **FAIL** (Sharpe positive but preregistered t-stat criterion not met)
- this qualification does not convert the historical FAIL into a PASS.

### SPA / DSR chronology and result

Family validation pre-registration:

`916e3d602f228cc0e671d533987fa59df29448f6`

Result:

`d0ea7155717811163016d2f3bdb2536099183cbd`

The result commit is the direct child of the pre-registration commit. Recorded family result: SPA p-value 0.1924 and DSR 0.8883 for the 13-member family, therefore no statistically established net edge against Buy & Hold at the declared thresholds.

The later adversarial report explicitly notes that `n_trials=13` is optimistic relative to approximately 110 adaptive research cycles on the same historical NDX data; increasing hypothetical trial counts lowers the reported DSR further. This strengthens, rather than weakens, the no-established-edge conclusion.

## Current audit verdict

`COVERAGE_COMPLETE = FALSE`

`SAFE_TO_CONSOLIDATE = FALSE`

`SAFE_TO_WHOLESALE_MERGE_OCI = FALSE`

`ORACLE_ECONOMIC_LOOP_FINAL_WIRING_OBSERVED = FALSE`

`PR1_INCLUDED_IN_SCOPE = TRUE`

`REMOTE_DELTA_RECONSTRUCTION_STARTED = TRUE`

The audit remains observational. No repair decision should be taken from this checkpoint alone.

## Next forensic work

1. Build a semantic inventory of PR #1 rather than treating all 700 commits equally: mechanisms, aliases, experiment families, verdicts, invalidated results, preserved unknowns and dependency consumers.
2. Verify pre-registration/result ordering for the highest-value PR #1 families beyond PEAD and SPA/DSR, including cycle #110 and any candidate later reused by Research OS.
3. Reconcile PR #1 scientific identities with `research/legacy-economic-reconciliation-20261015` and current Research OS candidate identities to prevent accidental retesting/rebranding.
4. Audit the exact modern queue/control-plane/executor path and the VM/OCI deployment assumptions without changing them.
5. Audit data-feed provenance/consumer dependencies and distinguish raw observations, restatements, duplicates and downstream economic use.
6. Re-read all refs at final closure and publish a final remote delta. Do not claim restoration of the missing original local bundle unless it is independently recovered and hash-verified.
