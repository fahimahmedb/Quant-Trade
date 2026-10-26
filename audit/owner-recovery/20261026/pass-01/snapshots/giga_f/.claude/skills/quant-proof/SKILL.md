---
name: quant-proof
description: Run the project verification gate and challenge the current milestone with adversarial evidence before it is called complete.
disable-model-invocation: true
context: fork
effort: high
---

Verify the current milestone rather than summarizing it.

1. Read current Blue governance, resolve the exact branch-specific mission/handoff and identify each explicit invariant. `CLAUDE_CURRENT_MISSION.md` may help route but is not the authority.
2. Bind every proof claim to the exact candidate SHA/proof domain before running verification.
3. Run the repository's normal verification commands.
4. Inspect the tests that claim to prove each invariant; distinguish existence tests from behavioral/adversarial proof.
5. Reproduce the most dangerous restart, timeline, attribution, transformation and liveness edge cases relevant to the mission.
6. Compare generated status/brief claims against persistent state where relevant.
7. Return PASS / FAIL / UNPROVEN for every mission invariant, with exact SHA, proof domain, evidence or failing test.

Do not modify code during this skill. Its purpose is independent proof.
