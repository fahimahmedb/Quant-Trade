# QUANT-TRADE — CONVERGENCE #1 — CP079-FIRST — CP001 — 2026-10-21

## Mission identity

CANONICAL_ROOT_SHA: `cf593275e41d21435ac308a144570e1451148815`
MISSION_BRANCH: `builder/convergence-cp079-wave2-base-20261021`
NORTH_STAR_BLOB: `a328b4e6d7d71dafd532938888ebf9818b1b610f`
HISTORICAL_DIAGNOSTIC_BRANCH: `builder/convergence-cp069-wave2-base-20261021`
HISTORICAL_DIAGNOSTIC_HEAD: `2d86bca4ce9b72af3eaeecfdb16324e1afd5f10b`

Qualified source lanes admitted for semantic convergence:

- W1 Scientific Memory FINAL: `9d92c9f859efd39fdfd94372b10ba91ad73c31b4`
- W1 Data / Evidence / SEC qualified head: `c0fda9bd809594711ebaf2fa2422a0410812e1df`
- W1 Factory / Experiment Infrastructure FINAL: `dfaf0bd7be04926a2b16dc585ccb82699c6dd0e4`
- W1 Economic / Structural Portfolio FINAL: `83bb495104acf7de8617593bc737a8a204c99b32`
- MEGA A FINAL: `29c6faa4ac334d74f2c90d49897346047beaa5d0`
- MEGA A validated code SHA recorded by its seal: `75c3351b0ec4fefdc1c9d0e67efcef1a412c8501`

## CP079-first law

1. `cf593275e41d21435ac308a144570e1451148815` is the only canonical root for this convergence.
2. The old CP069 convergence is diagnostic evidence only; no merge or cherry-pick from it is permitted.
3. Each historical change must be re-evaluated against CP079 and imported only where its owning capability is still missing or compatible.
4. CP070–CP079 canonical scientific-subject attribution, native reconstruction, trial-lineage and V2 binding law must not be rolled back.
5. CP079 Control / Oracle / Lab behavior and all newer fail-closed repairs remain authoritative.
6. `UNKNOWN` remains `UNKNOWN`; no lane may infer missing evidence, outcomes, costs, capacity, authority or production readiness.
7. Four authorities remain literally FALSE: `ECONOMIC_EXPERIMENT_AUTHORIZED`, `PROSPECTIVE_OBSERVATION_AUTHORIZED`, `REAL_CAPITAL_AUTHORIZED`, `LIVE_TRADING_AUTHORIZED`.
8. `OUTCOME_ACCESSED=FALSE` remains mandatory during convergence.

## Historical CP069 evidence admitted

The historical branch established useful semantic classifications through CP003:

- CP001: lane admission and prohibition on whole-lane merges;
- CP002: Scientific Memory imported selectively while preserving the newer recovered-source-review law in `legacy.py`;
- CP003: Data/Evidence/PIT imported selectively while preserving source-admission fail-closed behavior;
- Data defect: W1 tests initially placed under root `tests/` changed the canonical V1 inventory and failed status freshness;
- Data repair: those assertions moved under `research/research_os/tests/`, were executed explicitly by CI, and `STATE.md` was not rewritten.

Those conclusions are hypotheses for CP079 porting, not inherited truth. They must be rechecked against the CP079 tree before reuse.

## CP079 overlap assessment

The ten commits from CP069 to CP079 modify canonical V2 subject attribution / reconstruction / trial-lineage surfaces plus `STATE.md` and the Oracle V2 workflow. They do not modify the Scientific Memory implementation files or Data/PIT implementation files selected by historical CP002/CP003. Therefore the old semantic ports can be reconsidered without overwriting CP070–CP079 source law.

`STATE.md` is explicitly excluded from W1 import and remains CP079-owned.

## Qualification strategy

For each lane:

1. classify exact source delta versus CP079;
2. port only capability-owned files or targeted adaptations;
3. run the smallest focused suite that proves the imported contract;
4. require the canonical exact-head CI gate to pass before advancing;
5. record any defect and repair as a new checkpoint.

Final closure additionally requires full regression, V2/Oracle coverage, clean exact-head qualification, and only then may this branch emit `WAVE2_IMMUTABLE_BASE_SHA=<sha>`.

ENTRY_GATE: `PASS`
SAFE_TO_CONTINUE: `TRUE`
SAFE_TO_INTEGRATE: `FALSE`
