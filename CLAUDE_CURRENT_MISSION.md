# Claude Current Mission Router

This file is a router, not a frozen task specification.

## Resolve current work

Always begin by resolving the current branch and exact HEAD.

### Oracle V2 Core branch

If the branch is:

`builder/oracle-v2-core-20261020`

read in this order:

1. `QUANT_NORTH_STAR.md`
2. `CLAUDE.md`
3. `research/research_os/architecture/ORACLE_V2_CORE_SPEC.md`
4. `research/research_os/runtime/ORACLE_V2_CORE_ROADMAP.md`
5. `research/research_os/runtime/V2_CORE_POLICY.json`
6. the code/tests relevant to the current V2 work package
7. the V1 roadmap/checkpoints only when validating inherited V1 properties

Current mission: implement and qualify Oracle Research OS V2 Core as an autonomous **pre-outcome** research pipeline.

Owner implementation authorization is active.

Owner override: P0-D server-side branch protection is lifted and is not a V2 Definition-of-Done gate.

Permanent authority boundary during V2 Core:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Target system qualification:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`

Strongest candidate status:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY`

Neither is an economic-performance claim.

### Oracle V1 recovery branch

If the branch is:

`builder/oracle-economic-loop-recovery-20261019`

use `CLAUDE.md` and `research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md` as the current Oracle routing surfaces.

### Other branches

Use the branch-specific current governance/handoff. Historical September Blue files are relevant only when the current branch/governance explicitly routes to them.

## Never infer current mission from

- repository default branch;
- `STATE.md` alone;
- `CHIEF_BRIEF.md` alone;
- old PR/issue text;
- old chat summaries;
- this file's historical Git versions.

## Git / evidence discipline

Before any mutation reacquire fresh HEAD and relevant state. Preserve autonomous commits. Do not use force-push, reset, rewind or deletion of autonomous evidence as a conflict-recovery method.

P0-D being lifted removes the requirement for server-side branch protection; it does not authorize destructive Git operations.

Runtime evidence and repository evidence remain distinct. Model prose is never self-authenticating evidence.
