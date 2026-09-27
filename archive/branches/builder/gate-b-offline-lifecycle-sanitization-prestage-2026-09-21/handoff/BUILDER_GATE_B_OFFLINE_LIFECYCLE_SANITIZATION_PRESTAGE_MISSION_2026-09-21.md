# BUILDER — GATE B OFFLINE LIFECYCLE / SANITIZATION PRESTAGE — 2026-09-21

MISSION_TYPE = READ_ONLY_ANALYSIS + HANDOFF_ONLY

Expected starting HEAD:
2ee9e1d2d84b7c0ded400a56f64ad7d9e2a60651

Read first:
1. QUANT_NORTH_STAR.md
2. handoff/BLUE_GATE_B_PARALLEL_PREPARATION_CONVERGENCE_2026-09-21.md
3. governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md
4. governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md
5. governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md
6. frozen V4 implementation @ 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
7. Astra preactivation review @ aff6b7a2ca6355f518578c0ddbcac72fb49a356c

SCOPE:
Address ONLY Astra F5:
offline/synthetic destructive lifecycle campaign and post-campaign sanitization.

Do NOT:
- repair F1 schema;
- design run-ID registry/activation sealing (separate lane);
- own V3->V4 service-view transition (Lane A);
- mutate target host;
- alter production code in this mission.

OBJECTIVE:
Determine whether the CURRENT frozen V4 semantics already permit a safe,
reproducible Gate-B lifecycle campaign that:

- exercises real systemd/service-manager behavior;
- does NOT make real SEC requests;
- does NOT contaminate preserved qualifying state;
- does NOT substitute a materially different executable/service binding;
- preserves lifecycle provenance;
- can later sanitize/separate synthetic evidence from future Gate-C state.

Inspect exact V4:
- supervisor/collector startup path;
- requester initialization;
- network call boundary;
- state-root selection;
- environment/config dependencies;
- one-use deployment authority;
- lifecycle/journal semantics;
- fingerprint/materialization dependencies.

Produce one of:

A. EXISTING_SAFE_MECHANISM_FOUND
   - exact procedure;
   - why it exercises the correct service semantics;
   - why real network is impossible;
   - why qualifying state is protected;
   - exact sanitization and evidence boundaries.

B. EXISTING_SAFE_MECHANISM_NOT_PROVEN
   - exact missing primitive;
   - whether a minimal code/config/testability change is required;
   - what Blue must specify to Builder next;
   - why improvising with alternate paths/env/unit would invalidate proof.

Explicitly distinguish:
FACT / CLAIM / INFERENCE / RECOMMENDATION / UNKNOWN.

Do not invent a synthetic mechanism if current code does not support one.

OUTPUT:
handoff/BUILDER_GATE_B_OFFLINE_LIFECYCLE_SANITIZATION_PRESTAGE_2026-09-21.md

Final status:
GATE_B_OFFLINE_LIFECYCLE_PRESTAGE = READY_FOR_BLUE_REVIEW
or
GATE_B_OFFLINE_LIFECYCLE_PRESTAGE = BLOCKED_MISSING_MECHANISM

Only mission/handoff docs may be committed.
Return control to Blue.