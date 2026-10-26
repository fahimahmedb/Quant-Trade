---
name: quant-proof
description: Run the project verification gate and challenge the current milestone with adversarial evidence before it is called complete.
disable-model-invocation: true
context: fork
effort: high
---

Verify the current milestone rather than summarizing it.

1. Read `CLAUDE_CURRENT_MISSION.md` and identify each explicit invariant.
2. Run the repository's normal verification commands.
3. Inspect the tests that claim to prove each invariant; distinguish existence tests from behavioral/adversarial proof.
4. Reproduce the most dangerous restart, timeline, attribution, transformation and liveness edge cases relevant to the mission.
5. Compare generated status/brief claims against persistent state.
6. Return PASS / FAIL / UNPROVEN for every mission invariant, with the exact evidence or failing test.

Do not modify code during this skill. Its purpose is independent proof.
