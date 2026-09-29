# WEATHER FORWARD — V1 → V2 DELTA — 2026-09-29

```text
V1     = claude/intelligent-gates-msidml @ 726070a199957a6fc05515ebb3027e945028fddc  (immutable; unchanged in this branch)
ASTRA  = claude/dreamy-franklin-1vki4t  @ e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250  (immutable)
FABLE  = claude/zen-einstein-9moyry     @ 5760ffa5b5da2a988cfe6d1503c86c561acf9b1f  (immutable, advisory)
V2     = WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md (+ manifest, state, power table, synthetic sim)
SUMMARY: OUTCOME_INFORMATION_USED = FALSE for every item · TRADING_RULE_CHANGED = FALSE for every item ·
         EXECUTION_MODEL_CHANGED = TRUE for one item (X1, CONSERVATIVE only) · COHORT_CHANGED = TRUE for one item (D7)
```

Each block: OLD / NEW / WHY / ASTRA_FINDING / FABLE_RECOMMENDATION / ARCHITECT_DECISION / OUTCOME_INFORMATION_USED / TRADING_RULE_CHANGED / EXECUTION_MODEL_CHANGED / BUILDER_IMPACT.

---

## D1 — Power / effect-size architecture (CRITICAL → CLOSED)

**D1.a Thresholds**
- OLD: single θ_MEUE = 0.02 used as the economic threshold, the REJECTED threshold (U95 < 0.02) and a FORWARD_SIGNAL criterion; power statement "≥ 1,000 trades, SE ≈ 0.05".
- NEW: θ_ERT = 0.02 (economic relevance, reporting threshold, not powered); θ_PCE by a frozen price-implied formula populated in an outcome-free observation phase; PCE_CEILING = 0.10 and SE_KAPPA_CEILING = 0.020 as a pre-t0 GO/NO_GO; the band [θ_ERT, θ_PCE) is declared unresolved.
- WHY: confirming or excluding 0.02 needs SE ≤ 0.008 (≈ 15,500 independent trades at σ = 1), ≈ 1,340 dates at 35 trades/day; 120 dates hold ≈ 1,100–2,400 effective trades.
- ASTRA_FINDING: D1 CRITICAL; MDE 0.06–0.10 (0.15–0.25 with lottery legs).
- FABLE_RECOMMENDATION: Family B two-threshold labels; PCE from pre-t0 prices; PCE ceiling (CD11).
- ARCHITECT_DECISION: adopted; ceiling fixed at 0.10 = 5 × θ_ERT = lower end of V1's own disclosed confirmable range.
- OUTCOME_INFORMATION_USED: FALSE (prices, depth and counts only). TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: implement the OP computation (spec §10.2) and the GO/NO_GO report; no scientific choice.

**D1.b Architecture**
- OLD: fixed 60/90/120-date window, one primary test on θ, percentile date-block bootstrap.
- NEW: Family D + B hybrid: θ (economic) and a stratified information axis (κ_core, tail win count) tested in **parallel**; fixed 120 counted dates; no interim.
- WHY: the only design with a real negative result at 120 dates that is immune to lottery-leg variance on the information axis and honest about the unresolved band.
- ASTRA_FINDING: D1 minimum closure option (a) "declare the estimand the design can test".
- FABLE_RECOMMENDATION: Family D with fixed-sequence gatekeeping (θ only after the information gate).
- ARCHITECT_DECISION: Family D **without the gate** (D1-GATE). SIMULATED: an edge concentrated in the cheapest legs (true θ = 0.44) is seen by the θ engine 0.535–0.61 of the time, but only 0.21–0.30 of runs would pass a count-based gate (runs A/B); joint claims are controlled by intersection-union instead. Families A and C rejected (spec §4).
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: stratum field at decision time; κ_core, W_tail, Λ_tail computations; product state machine.

## D2 — Terminal state machine (CRITICAL → CLOSED)

- OLD: five labels evaluated in order, with gaps S1–S4, ambiguities S5–S6, misleading precedence S7–S8 (Astra §9) and an unpinned 90/120 analysis date.
- NEW: VALIDITY (8 ordered rows) × SCIENTIFIC (NOT_EVALUATED | INFORMATION_INSUFFICIENT | INFORMATION_RESULT × ECONOMIC_RESULT = 3 × 4) × OPERABILITY (6 ordered rows); report fields ECONOMIC_BOUND, INFO_SOURCE, CORE_ADVERSE; forward-signal and rejection rules defined on the axes; one ANALYSIS_TIME = D_120 + 10 days.
- WHY: every axis is an ordered list ending in "otherwise", so each is a total, mutually exclusive partition by construction.
- ASTRA_FINDING: D2 CRITICAL.
- FABLE_RECOMMENDATION: six-label partition + orthogonal VALID / ACCESSIBLE.
- ARCHITECT_DECISION: **modified** — Fable's six labels are six of V2's twelve product cells; the economic column is also evaluated when no information is detected; INFORMATION_INSUFFICIENT added; relevance exclusion ordered before confirmation (a positive but irrelevant θ is never "confirmed").
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: implement three ordered tables exactly; synthetic tests must reach every row.

## D3 — Book timestamp / observation contract (CRITICAL operational → CLOSED)

- OLD: E6 / invariant 11 `book_timestamp ∈ [T_entry − 5 min, T_entry]` for 22 tokens.
- NEW: window on `captured_at ∈ [T_entry − 300 s, T_entry]`; `exchange_book_timestamp ≤ captured_at + 2 s`; no lower bound; retries every 20 s; per-token last valid capture; provenance fields; NTP ≤ 250 ms; completeness = complete / entry-expected (E1–E5, E7, E8 true).
- WHY: the CLOB `timestamp` is the book's last change; ≈ 28–33% of weather tokens are quiet for > 5 min (Astra X3); a quiet book is a valid book.
- ASTRA_FINDING: D3. FABLE_RECOMMENDATION: test on captured_at (Fable §5.2 GR condition).
- ARCHITECT_DECISION: adopted with exact windows, tolerance and denominator.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE (same book, correctly timed).
- BUILDER_IMPACT: capture scheduler, retry loop, VALID_CAPTURE predicate, new snapshot fields, invariant 24.

## D4 — Heavy-tail inference (MAJOR → CLOSED)

**D4.a Estimand layer**
- OLD: θ only; per-trade SD assumed 1.2.
- NEW: θ unchanged and never winsorised; price strata (TAIL iff chosen best ask < 0.04, frozen constant); κ_core and λ_tail information estimands; θ_core / θ_tail decomposition reported.
- WHY: θ's ratio-of-means weights each leg's surprise by shares (a 0.001 leg carries ≈ 600× the weight of a 0.6 leg); no resampling method represents unobserved 1,000× wins.
- ASTRA_FINDING: D4 MAJOR. FABLE_RECOMMENDATION: κ_core + W_tail vs Λ_tail, strata by the tick regime.
- ARCHITECT_DECISION: adopted; κ uses all-in executable cost (net per share); strata by price, not by the live tick field (MEASURED: tick is market-level, shared by YES and NO; 1,550 / 2,981 markets at 0.001).
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: `stratum`, `best_ask_chosen`, `q_chosen` stored at decision time (invariant 23).

**D4.b Engines**
- OLD: moving-block percentile bootstrap over dates (primary).
- NEW: two-way cluster-robust t (max-of-three SE, df = min(G_B, G_S) − 1) primary for κ_core, θ_core, θ; PINM (declared copula ρ = 0.10 / 0.10 / 0.10, B = 20,000, fixed seed) gating only the tail count (T1b) and the tail part of the upper bound; PINM on θ and κ reported; percentile bootstrap a sensitivity row.
- WHY (SIMULATED): PINM with a declared (not oracle) dependence is either anti-conservative (Fable: 0.13–0.21) or power-destroying (core-only θ = 0.10: 0.73–0.755 vs 0.855–0.91 for CR); CR is conservative for positive θ claims when tails are present (null 0.000–0.020); rare-event counts are nearly insensitive to the declared dependence.
- ASTRA_FINDING: D4 (studentised / BCa / stratified). FABLE_RECOMMENDATION: PINM primary + two-way studentised bootstrap, reject only if both reject.
- ARCHITECT_DECISION: **modified** — engines assigned by domain of validity; no agreement requirement.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: CR engine; PINM with exact seed and draw order; bisection for λ_U, μ_U.

**D4.c Exclusion bound**
- OLD: U95 of the percentile bootstrap used for REJECTED.
- NEW: structured bound `U(θ) = w_core U_core + w_tail max(θ^TPM, θ^SHR)`, tagged MODEL_CONDITIONAL_TAIL.
- WHY (SIMULATED): naive pooled U95 covers 0.79–0.91 with lottery legs; the structured bound ≥ 0.945 except in a deliberately adversarial hidden-lottery scenario (disclosed as a MAJOR non-blocking limitation).
- ASTRA_FINDING: D4. FABLE_RECOMMENDATION: not specified (Fable §4.2 documented the false-exclusion problem).
- ARCHITECT_DECISION: new; exclusions are model-conditional and labelled.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: implement spec §8.5 exactly.

## D5 — Science vs operability (MAJOR → CLOSED)

- OLD: OPERATIONALLY_INACCESSIBLE evaluated before REJECTED.
- NEW: OPERABILITY_STATE is an orthogonal axis (legal, mechanics, depth ≥ 25 USD share ≥ 0.80, ρ_30 at 1,000 tier ≥ 0.05) that never replaces or pre-empts the scientific label.
- WHY: a losing rule must not exit as "inaccessible"; depth is marginal (76% measured vs 80%).
- ASTRA_FINDING: D5. FABLE_RECOMMENDATION: orthogonal flag.
- ARCHITECT_DECISION: adopted; V1 criteria 7 and 8 moved here.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: separate state computation and report section.

## D6 — Burn-in / readiness (MAJOR → CLOSED)

- OLD: burn-in ≥ 30 consecutive days, then t0.
- NEW: USABLE / BIAS_HISTORY_READY per station-kind (30 usable resolved dates at T_entry, FINAL by our own capture time); FRESH_READY (span ≤ 40 days) for readiness; GLOBAL_READY (GR1–GR6); 14-date outcome-free observation phase; readiness report; t0 within 21 days of the OP.
- WHY: the first E8-eligible date is ≈ day 33–35; the frozen rule's trigger rate is unobservable in a 30-day burn-in.
- ASTRA_FINDING: D6. FABLE_RECOMMENDATION: READY / GLOBAL_READY / 14-date observation.
- ARCHITECT_DECISION: adopted with a stricter GR1 (80% of 48 stations, both kinds) and the 21-day t0 validity.
- OUTCOME_INFORMATION_USED: FALSE (settled values of past dates enter only the frozen bias term, as in V1; parser agreement is aggregate). TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: READINESS table, PHASE_LOG, phase flag, invariant 21.

## D7 — °F / 2 °F cohort (MAJOR → CLOSED)

- OLD: E4 "nine consecutive single-degree buckets" (excluded every °F ladder); bucket arithmetic single-degree only.
- NEW: °F included; four frozen title regexes; integer sets; half-open continuous intervals; E4 by width `w = 1` (°C) / `w = 2` (°F); °F bias target = bucket midpoint; exact unit conversion.
- WHY: MEASURED 66/66 °F ladders are 2 tails + nine contiguous 2 °F buckets with the same NOAA template in whole °F (no conversion chain); 48 vs 37 stations for the weakest inferential dimension; V1's σ = 1.8 °F and E13 show the intent.
- ASTRA_FINDING: D7. FABLE_RECOMMENDATION: Architect's call.
- ARCHITECT_DECISION: route B (generalise), fully specified.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE (same formula on a clarified domain). EXECUTION_MODEL_CHANGED: FALSE. COHORT_CHANGED: TRUE.
- BUILDER_IMPACT: parser, arithmetic tests (spec §26), unit field.

## D8 — Date × station dependence (MAJOR → CLOSED)

- OLD: date-block bootstrap primary; station and two-way as sensitivities.
- NEW: two-way (5-date calendar block × ICAO) cluster-robust primary, max-of-three SE, t(min G − 1), cluster floors, Kish reporting, DEFF reporting; PINM copula with date, station and station-day cell effects.
- WHY (SIMULATED here and by Fable): date-only κ test rejects 0.095–0.205 at nominal 0.025 under station dependence.
- ASTRA_FINDING: D8. FABLE_RECOMMENDATION: two-way, max of three.
- ARCHITECT_DECISION: adopted.
- OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE.
- BUILDER_IMPACT: CR engine; cluster keys in PNL rows.

## D9 — MIN_SAMPLE (MINOR → CLOSED)

- OLD: ≥ 1,000 trades as the power basis. NEW: information floor IF1–IF5 (dates, blocks, stations, SE, DEFF). WHY: 1,000 is reached by day 24–77 and is not where information binds. ASTRA: D9. FABLE: date ceiling §1.3. DECISION: retired. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: floor computation.

## D10 — NO_DATA_LOWEST in the bias history (MINOR → ACCEPTED, DISCLOSED)

- OLD: all settlements enter the bias mean (tail boundary). NEW: unchanged; `BIAS_CONTAMINATED` flag per decision; per-station counts; non-gating sensitivity on the uncontaminated subset.
- WHY: excluding non-meteorological settlements would change R*'s bias estimator (a rule change) and is not needed for validity.
- ASTRA: D10 (exclude). FABLE: exclusion is a rule change, Architect's call. DECISION: preserve the rule. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: flag and report fields.

## D11 — Mechanics-change baseline (MINOR → CLOSED)

- OLD: ≥ 50% of all daily temperature events ineligible / ambiguous for 14 dates → OPERATIONALLY_INACCESSIBLE.
- NEW: reason-code families; share over baseline-eligible events (structural and readiness codes excluded); M3 fee change → immediate; ≥ 50% on 14 dates → effective at the first; truncation with ≥ 60 counted dates → VALID_TRUNCATED, else INVALID.
- WHY: ≈ 28% structural ineligibility left ≈ 22 points of headroom. ASTRA: D11. FABLE: §5.6. DECISION: adopted. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: reason-family field, detectors M1–M6.

## D12 — Tier selection (MINOR → CLOSED)

- OLD: T_entry order, ties by event_id. NEW: T_entry order, ties by `sha256(event_id + ":WFV2")`; CAPACITY_CONSTRAINED_SUBSAMPLE label with regional composition.
- WHY: T_entry order is the causal constraint; a fixed event_id tie-break favours the same cities daily. ASTRA: D12. FABLE: CD5. DECISION: adopted. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: tie-break function, report labels.

## X1 — CONSERVATIVE slippage (cross-defect → CLOSED)

- OLD: level price + 0.01. NEW: level price + one tick (recorded `orderPriceMinTickSize`; fallback rule).
- WHY: + 0.01 on a 0.001 ask is an 11× cost; the robustness gate would fail mechanically whenever tail legs matter.
- ASTRA: §6.5. FABLE: CD9. DECISION: adopted. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. **EXECUTION_MODEL_CHANGED: TRUE (CONSERVATIVE only)**. BUILDER_IMPACT: tick lookup in the fill engine.

## X2 — Sequential design (CLOSED)

- OLD: "no early stopping" but a 60/90/120 window with an unpinned analysis date. NEW: one analysis at D_120 + 10 days; no interim; time-locked analysis module.
- WHY: efficacy stopping is useless in the plausible range; futility on θ is hazardous with rare tail wins; a paper experiment has no capital at risk. ASTRA: S4. FABLE: Family C, one futility look optional. DECISION: no interim. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: invariant 22.

## X3 — Attribution / placebo (CLOSED)

- OLD: criterion 9 "beats B4 and B5 by ≥ θ_MEUE" gating FORWARD_SIGNAL. NEW: descriptive; T1 carries information attribution; ATTRIBUTION_NOT_ESTABLISHED and PLACEBO_ANOMALY flags.
- WHY: SE of a difference of two θ̂ is 0.04–0.14. ASTRA: —. FABLE: CD13. DECISION: descriptive. OUTCOME_INFORMATION_USED: FALSE. TRADING_RULE_CHANGED: FALSE. EXECUTION_MODEL_CHANGED: FALSE. BUILDER_IMPACT: report fields.

## X4 — Other V1 gate criteria

| V1 criterion | V2 location |
|---|---|
| c1 L95 > 0 | T2 (two-way CR) |
| c2 θ̂_CONS > 0, θ̂ ≥ θ_MEUE | G1 (tick-aware) and `θ̂ ≥ θ_ERT` in E2 / E3 |
| c3 no leakage / replay | VALIDITY rows 1–3 |
| c4 minimum sample | MIN_INFORMATION IF1–IF5 |
| c5 L80 ≥ 0.01 | retired (created Astra's S3 gap; the relevance question is carried by U(θ) and ECONOMIC_BOUND); L80 printed descriptively |
| c6 concentration, settlement modes | G2, G3 |
| c7 accessibility | OPERABILITY row 4 |
| c8 capital efficiency | OPERABILITY row 5 |
| c9 attribution | descriptive (X3) |

## Unchanged (explicitly)

h = 0.10; W = 30; σ = 1.0 °C / 1.8 °F; model, provider, members, variables, cadence; T_entry; argmax and tie rule; hold to settlement; fee; S_ref = 50; tiers and stake fraction; REALISTIC fill model; accounting and full ledger; settlement controls; survivorship cohort; exploratory family E1–E15; anti-leakage invariants other than 11.
