# BUILDER — GATE B RUN AUTHORITY MECHANISMS — 2026-09-21

MISSION_TYPE = IMPLEMENTATION + TESTS + HANDOFF

Expected starting HEAD:
366d9b5ccb2a0ce7dfae3a923d3e93beceb93aab

Read first:
1. QUANT_NORTH_STAR.md
2. governance/BLUE_GATE_B_RUN_AUTHORITY_MECHANISMS_SPEC_2026-09-21.md
3. handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md
4. handoff/BLUE_GATE_B_PARALLEL_PREPARATION_CONVERGENCE_2026-09-21.md

Implement ONLY M1-M4 from the Blue spec:
- append-only run registry;
- authority consumer;
- revocation/freshness;
- index-independent deployed-byte verifier.

No frozen V4 src changes.
No target-host mutation.
No F5 work.
No Gate-B/t0 declaration.

Provide reproducible discriminants and final handoff:
handoff/BUILDER_GATE_B_RUN_AUTHORITY_MECHANISMS_2026-09-21.md

Final status:
GATE_B_RUN_AUTHORITY_MECHANISMS = READY_FOR_INDEPENDENT_REVIEW

Commit and push to same branch.
Return control to Blue.