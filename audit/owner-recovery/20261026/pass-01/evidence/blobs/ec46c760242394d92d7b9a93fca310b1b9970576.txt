# ASTRA GATE A V4 INDEPENDENT AUDIT — DURABLE CHECKPOINT — 2026-09-21

Frozen candidate:
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

Evidence HEAD before final handoff:
1744a897d57dddef524a880d317557c660a17897

Ancestry:
merge-base(candidate, evidence HEAD) = candidate.

Audit-only paths at the evidence HEAD:
- handoff/ASTRA_GATE_A_V4_MISSION_2026-09-20.md
- audit/astra_gate_a_v4_independent_probe.py
- .github/workflows/astra-gate-a-v4-independent-audit.yml

Independent audit run:
35544664445 = COMPLETED / SUCCESS

Focused replay:
Phase5 + Phase7 + Phase8 = 22 tests, OK.

Independent probe:
A1–A10 current-unit repository discriminants = PASS, zero probe failures.

Key classifications:
- v3 raw ExecStart digest instability independently reproduced;
- v4 transient start_time/stop_time/pid/code/status stability = PASS;
- real command drift rejected or different digest = PASS;
- qualifying lookalikes = rejected;
- systemd contract drift/unavailable output = fail closed;
- unknown stable fields = bound;
- tested canonicalization ordering = stable;
- authority replay = rejected;
- stale materialization = rejected;
- no child/launch event before materialization validation;
- Builder lifecycle-named Phase8 test = TEST_DEFECT / NON_BLOCKING because it checks only effective-environment digest stability, not the full authority lifecycle;
- five parser representation limitations = NON_ISSUE / HYPOTHETICAL_FUTURE-UNIT_LIMITATION for the frozen unit;
- no current-unit repository REAL_DEFECT reproduced.

Residual:
actual v4 target-host execution remains TARGET_HOST_ONLY.

Next:
push final handoff, observe both exact-head Astra audit workflow and exact-head SEC P0 pre-t0 gate, then stop and return control to Blue.
