# BUILDER — GATE B V4 MATERIALIZATION / ACTIVATION PRESTAGE — 2026-09-21

MISSION_TYPE = READ_ONLY_ANALYSIS + HANDOFF_ONLY

Expected start SHA:
ba510bd5e3077c7e29b35aef9cf45c98a5fd128c

Read first:
1. QUANT_NORTH_STAR.md
2. governance/BLUE_GATE_B_PARALLEL_PREPARATION_DISPATCH_2026-09-21.md
3. governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md
4. governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md
5. governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md
6. governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md
7. governance/TARGET_HOST_V4_RELEASE_MATERIALIZATION_2026-09-21.md
8. operator preflight handoff at operator/gate-b-read-only-preflight-2026-09-21@44285788fce3d5d048b037dd8d1089e1f08f43e9

FACTS FROM PREFLIGHT:
- expected V4 release path absent;
- fixed service view still points to rejected V3;
- service failed/disabled;
- unit bytes match frozen V4;
- durable state mount visible;
- evidence root not yet bound;
- no mutation occurred.

OBJECTIVE:
Prepare the exact mutation/activation plan needed to resolve ONLY those blockers and enter Gate B safely.

MUST BIND:
- frozen V4 SHA/tree/input-tree;
- exact source/object authority for release materialization;
- staging -> verification -> final immutable release procedure;
- self-contained Git/no alternates/no linked worktree checks;
- exact fixed service-view transition from V3 to V4;
- state-root preservation and mount ordering;
- missing-mount fail-closed boundary;
- evidence-root binding proposal;
- activation-time host/time/network/resource fields;
- explicit mutation-capability matrix;
- rollback/terminal-failure semantics;
- first command that would require GATE_B_MUTATION_AUTHORIZED=TRUE;
- exact evidence artifacts/digests to collect.

FORBIDDEN:
- touching target host;
- materializing release;
- changing mounts/systemd/state;
- modifying src/tests/scripts/schemas/workflows;
- declaring Gate B PASS;
- creating t0.

OUTPUT:
handoff/BUILDER_GATE_B_V4_MATERIALIZATION_ACTIVATION_PRESTAGE_2026-09-21.md

Final status:
GATE_B_ACTIVATION_PRESTAGE = READY_FOR_BLUE_REVIEW
or precise blocker.

Only mission/handoff docs may be committed.
Return to Blue.