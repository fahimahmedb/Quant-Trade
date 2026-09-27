# BUILDER — GATE B EVIDENCE SCHEMA FALSE-PASS FIX — 2026-09-21

## Mission type

`GOVERNANCE_SCHEMA_REPAIR + DISCRIMINANTS + HANDOFF`

Work only on:
`builder/gate-b-evidence-schema-false-pass-fix-2026-09-21`

Expected starting HEAD:
`2ee9e1d2d84b7c0ded400a56f64ad7d9e2a60651`

## Authority

Read first:

1. `QUANT_NORTH_STAR.md`
2. `handoff/BLUE_GATE_B_PARALLEL_PREPARATION_CONVERGENCE_2026-09-21.md`
3. `governance/BLUE_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_REPAIR_SPEC_2026-09-21.md`
4. `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`
5. Astra handoff:
   `astra/gate-b-v4-transition-independent-preactivation-review-2026-09-21@aff6b7a2ca6355f518578c0ddbcac72fb49a356c`

Do NOT treat Astra as implementation authority; Blue repair spec is normative.

## Scope

Fix only the authoritative Gate-B evidence-schema false-PASS defect and provide
reproducible discriminants.

Do not repair F2-F6 operational proof gaps unless a tiny schema-only structural
part is inseparable from F1 and explicitly documented.

Do NOT modify:
- frozen V4 production code;
- target host;
- `/opt/quant`;
- `/var/lib/quant-p0`;
- systemd/mounts/runtime;
- Product code.

## Required discriminants

The repaired schema must reject D1-D7 from the Blue spec and preserve all listed
negative controls.

A complete synthetic structurally-valid PASS fixture must validate.

Synthetic artifacts are test fixtures only, never Gate-B evidence.

## Required delivery

- repaired schema;
- governance-appropriate schema discriminant runner/fixtures;
- exact result table;
- changed-path scope;
- final handoff:
  `handoff/BUILDER_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_FIX_2026-09-21.md`

Final status:

`GATE_B_SCHEMA_REPAIR = READY_FOR_INDEPENDENT_RECHECK`

Builder must not claim independent correctness, Gate B PASS or t0.

Commit/push to same branch and return to Blue.
