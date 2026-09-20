---
name: quant-orient
description: Reconstruct the current Quant branch, mission and highest-value next action without rereading the whole repository.
disable-model-invocation: true
context: fork
effort: medium
---

Orient on the current repository state efficiently.

1. Inspect branch, HEAD and working-tree status.
2. Read `QUANT_NORTH_STAR.md`, `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`, `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`, and `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md`.
3. Resolve the exact mission/handoff for the current branch and verify its pinned base/SHA.
4. Treat `STATE.md`, `CHIEF_BRIEF.md` and `CLAUDE_CURRENT_MISSION.md` as supporting/router surfaces, never as stronger authority than current Blue governance.
5. Inspect the current diff/recent commits and exact CI relevant to the mission.
6. Read only the code/tests needed to understand the active work.
7. Return a compact orientation: authority, current branch/HEAD, mission, proof domain, proven capabilities, known blockers, files likely to change, and next action.

Do not propose a new architecture unless the current implementation conflicts with the North Star.
