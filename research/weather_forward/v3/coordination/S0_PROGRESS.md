# S0 PROGRESS (Weather V3 compute infrastructure)
CURRENT_PHASE: 2 - engine + layer-A kernel equivalence PASS (15 cells x 400 reps, 0 mismatches); next: plans/driver/merge/resume
CURRENT_HEAD: see git log
INPUT_SHA_SET: V2 candidate origin/claude/charming-allen-948kd8 (read-only worktree /tmp/v2ro); Blue plan @bfe58f3
OPEN_QUESTIONS: none
FAILED_CANDIDATES: none
SURVIVING_CANDIDATES: none yet
DEVIATIONS: none
SCOPE_DECISIONS (not deviations; recorded for re-audit):
 - Reference old engine = P1 `one_rep_p1` (proved identical to M2 `one_rep` by V2's own check()). M2 comparators H_B40/H_Q975 and PINM (T1b, rep-level B=2000 draws) are NOT ported in v1; LW_CAL (run G, EWC rule) is superseded by M2/P1 and not ported.
 - Old engine consumes RNG sequentially per rep (variable-length), so record-for-record equality with a vectorised generator is impossible by construction. Equivalence is therefore two-layer: (A) statistics kernel exact on identical injected inputs; (B) generator distributional equivalence vs old engine and committed V2 JSONL (declared tolerance + identical state decisions).
 - Profile: old engine ~1.0 ms/rep light cells, ~2.5 ms/rep heavy (m=96) => 20k reps ~20-50 s/cell/core.
NEXT_EXACT_ACTION: write wf_plans.py (port V2 plan builders), wf_run.py (--slice i/n, resume, confirm streams), wf_merge.py; then declare comparison set (COMPARISON_SET.json) and COMMIT before running layer B.

NOTES: speed so far ~0.8 ms/rep light cells vs old ~1.0 (per-trade work dominates; old already trade-vectorised). Honest benchmark to follow. Rep-block size is a pure function of the cell spec (part of the reproducibility contract).
