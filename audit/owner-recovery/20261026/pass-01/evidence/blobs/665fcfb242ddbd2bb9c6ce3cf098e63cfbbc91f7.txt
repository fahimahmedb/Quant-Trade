# Claude Current Mission Router

This file is deliberately a **router**, not a task specification or a state snapshot.
It must never carry a point-in-time workstream summary; state lives only in the files below.

## Resolve current work

Read in this order:

1. `QUANT_NORTH_STAR.md`
2. `NEXT_BUILD_MISSION.md`
3. `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`
4. `handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md`
5. pending owner-delegated decisions awaiting ratification:
   `handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md`
6. the exact mission/handoff referenced there for the branch you are on

Always resolve:
- current branch;
- exact HEAD;
- relation to the pinned mission base;
- current Blue HEAD and any newer branch heads not yet received on master;
- exact CI evidence relevant to that SHA.

Do not infer the mission from:
- `STATE.md`;
- `CHIEF_BRIEF.md`;
- repository default branch;
- old PR/issue text;
- this file's historical Git versions.

Safety constants (change only through Blue governance or the project owner):
`REAL_CAPITAL_AUTHORIZED = FALSE`.
