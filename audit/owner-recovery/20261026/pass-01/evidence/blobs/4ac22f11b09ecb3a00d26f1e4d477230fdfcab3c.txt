# BUILDER — GATE C PROSPECTIVE EVENT PLAN PRESTAGE — 2026-09-21

MISSION_TYPE = READ_ONLY_ANALYSIS + HANDOFF_ONLY

Expected start SHA:
ba510bd5e3077c7e29b35aef9cf45c98a5fd128c

Read first:
1. QUANT_NORTH_STAR.md
2. governance/BLUE_GATE_B_PARALLEL_PREPARATION_DISPATCH_2026-09-21.md
3. governance/P0_HYBRID_EVENT_BASED_QUALIFICATION_AMENDMENT_2026-09-21.md
4. governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md
5. governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md
6. frozen V4 source-calendar implementation/tests at 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
7. governance/BLUE_P0_FINGERPRINT_AND_SOURCE_CALENDAR_BINDING_2026-09-21.md

OBJECTIVE:
Prepare a prospective Gate-C calendar/event template usable immediately after a future Gate-B PASS.

MUST DEFINE:
- ordinary source-closed interval rule;
- next expected live-acquisition window;
- complete-weekend closure rule;
- first post-weekend required acquisition;
- daily-index reconciliation under the bound 30h settle rule;
- obligation accounting;
- heartbeat/attempt-hole rules;
- runtime/service/fingerprint/state-mount invariants;
- resource before/after evidence;
- reset/invalidation conditions;
- exact fields Blue must fill BEFORE t0 launch.

May identify the nearest candidate windows relative to 2026-09-21 as PRELIMINARY ONLY, but must require refresh at t0-precommit time.

FORBIDDEN:
- declaring t0;
- selecting a launch retrospectively;
- target-host mutation;
- network requests;
- changing calendar code;
- treating elapsed days alone as Gate C.

OUTPUT:
handoff/BUILDER_GATE_C_PROSPECTIVE_EVENT_PLAN_PRESTAGE_2026-09-21.md

Final status:
GATE_C_EVENT_PLAN_PRESTAGE = READY_FOR_BLUE_REVIEW
or precise blocker.

Return to Blue.