# Weather V3 — AGENTS.md

Applies to `research/weather_forward/v3/**`.

## Authority
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED
BUILDER_AUTHORIZED = FALSE

Read `V3_CURRENT.md` first. Do not infer current state from chat.

## Bounded autonomy
You MAY refactor implementation, add diagnostics/stress cases, split compute, kill a structurally invalid candidate, or tighten a claim.
You MUST log any material deviation as: WHY / SCIENTIFIC_EFFECT / FROZEN_SURFACE_TOUCHED / NEW_REAUDIT_SURFACE.
You MAY NOT inspect forward-holdout outcomes, lower standards after results, tune to force PASS, silently change an estimand, or authorize deployment/capital.

## Token discipline
- Read paths + targeted sections, not whole long specs.
- Never paste source text into handoffs; cite path/section/SHA.
- One question per task/worktree.
- Durable details go in files; chat handback <= 8 lines.
- Reuse summaries/digests and content hashes; do not re-derive closed surfaces.
- Do not open raw JSONL unless a summary is insufficient.
- Stop exploration once the mission decision is supported.

## NumPy / compute contract
- Vectorize over replications; Python loops only over small cell/plan dimensions.
- No pandas in inner simulation loops.
- Use preallocation, broadcasting, indexed reductions; chunk only for RAM.
- RNG: `SeedSequence([BASE_SEED, PLAN_ID, CELL_ID, STREAM_ID])`; results independent of slice/order/CPU count.
- Prefer common random numbers for candidate-vs-baseline comparisons when mathematically valid.
- SMOKE=1k is code-only; RESEARCH=20k/cell; CONFIRM>=100k only for boundary/worst cells.
- Cache/reuse unchanged baseline outputs by exact code+plan hash.
- Equivalence before replacing an engine; scientific decisions must match.
- Every heavy plan must be sliceable/resume-safe with duplicate/missing/seed/schema checks.

## Pruning
Do not create research tails with low decision value.
Kill or defer a candidate when any applies:
- no verified point-in-time data;
- adds correlated contracts but no new independent date/event information;
- incompatible settlement semantics;
- changes the estimand and has not been split into a separate candidate family;
- fails calibration/equivalence materially;
- adds complexity without measurable calibrated variance/information gain.

At most 3 live candidate families per scientific work package.
Do not optimize Kelly/bandits/capital sizing before a scientific edge candidate survives.

## Git/worktree
Use the Codex task/worktree state natively. Commit each durable phase. A task is complete only when its artifacts + progress ledger are committed and the final commit SHA is reported.
