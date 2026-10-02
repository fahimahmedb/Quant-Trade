# Weather V3 — CODEX NATIVE ORCHESTRATOR — 2026-10-03

Use the current Codex task/worktree model. Do not emulate the old "one manually-created remote branch per prompt" workflow unless a durable Git checkpoint is actually needed.

## Bootstrap
Read only:
1. `research/weather_forward/v3/AGENTS.md`
2. `research/weather_forward/v3/V3_CURRENT.md`
3. `QUANT_NORTH_STAR.md`
Then read task-specific source paths only.

## Parent mission
Drive Weather V3 to one of:
- `V3_CANDIDATE_READY_FOR_FRESH_ASTRA`
- `V3_NOT_JUSTIFIED`

Do not target PASS. Optimize information gained per calendar day with honest inference.

## Native task graph
Run independent tasks in separate Codex worktrees/tasks.

Wave 1:
- COMPUTE_CLOSEOUT
- FORECAST_HINDCAST
- COHORT_EXPANSION

As soon as COMPUTE_CLOSEOUT passes:
- TAIL_PRICE

Then:
- VARRED only after TAIL_PRICE + FORECAST_HINDCAST have survivors.

Then:
- BLUE_SYNTHESIS after TAIL_PRICE + FORECAST_HINDCAST + COHORT_EXPANSION + VARRED.

Finally:
- FRESH_ASTRA in a new independent task/worktree.

## Worktree handoff contract
Each child receives:
- mission name;
- exact input commit(s);
- required output path;
- stop conditions.
No pasted spec bodies.

Each child returns only:
`TASK / SHA / STATUS / MAIN_RESULT / SURVIVORS / BLOCKER / NEXT`.

The parent reads committed summaries, not raw outputs.

## Adaptive discretion
The parent may:
- skip a downstream task whose prerequisite is falsified;
- merge two purely mechanical tasks if this reduces overhead;
- fork compute slices;
- stop a candidate family early on structural invalidity;
- request one bounded follow-up when a result is ambiguous.

The parent may not:
- add exploratory tails after seeing disappointing results;
- weaken a target;
- use future outcome information;
- collapse distinct estimands into one;
- let the same design task serve as the final independent Astra reviewer.

## Compute policy
All heavy work inherits AGENTS NumPy rules.
Use paired/common-random-number comparisons when valid.
Do not spend 100k reps everywhere: use 20k broadly, then >=100k only for predeclared worst/boundary cells.
Do not rerun unchanged baselines if code+plan hashes match committed evidence.

## Task cards

### COMPUTE_CLOSEOUT
Input: S0 remote WIP `1fa81100...`.
Only missing work: Layer-B distributional equivalence, honest old-vs-new speed/RAM benchmark, README/progress closeout.
If Layer-B fails, repair then rerun A+B. Otherwise stop.

### FORECAST_HINDCAST
Input: S1 DONE `697865d4...`.
Verify ECMWF/GEFS/NBM/MOS PIT feasibility. Prefer fixed hindcast/history correction over rolling-30 if supported.
Max 3 signal families including baseline. No market-outcome tuning.

### COHORT_EXPANSION
Input: S1 DONE `697865d4...`.
Search only for genuinely new independent event/date mass. Same-day correlated contracts do not count as new independent units.
Reject incompatible settlement/PIT candidates immediately.

### TAIL_PRICE
Input: COMPUTE_CLOSEOUT PASS.
Max 3 predeclared families. Report estimand changes explicitly.
Use NumPy engine and paired simulations where valid.

### VARRED
Input: surviving TAIL_PRICE + FORECAST_HINDCAST.
Simple pre-trade ANCOVA/CUPED first. Add hierarchical pooling only if justified by residual heterogeneity and calibrated gain.

### BLUE_SYNTHESIS
Freeze the smallest coherent design. Required outputs: estimand, signal, tail/sizing, cohort, inference, class, GO meaning, horizon, holdout, falsification, expected independent dates/month, MDE80, time-to-answer.

### FRESH_ASTRA
Fresh context. Audit exact frozen SHA only. Attack PIT leakage, candidate selection, calibration, dependence, estimand drift, transportability, correlated-count inflation, model-version breaks, holdout contamination.

## Hard authority
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED
BUILDER_AUTHORIZED = FALSE
