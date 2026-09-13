---
name: quant-orient
description: Reconstruct the current Quant branch, mission and highest-value next action without rereading the whole repository.
disable-model-invocation: true
context: fork
effort: medium
---

Orient on the current repository state efficiently.

1. Inspect branch, HEAD and working-tree status.
2. Read `QUANT_NORTH_STAR.md`, `STATE.md`, and `CLAUDE_CURRENT_MISSION.md` when present.
3. Inspect the current diff or recent commits relevant to the mission.
4. Read only the code/tests needed to understand the active work.
5. Return a compact orientation: current branch/HEAD, mission, proven capabilities, known blockers, files likely to change, and next action.

Do not propose a new architecture unless the current implementation conflicts with the North Star.
