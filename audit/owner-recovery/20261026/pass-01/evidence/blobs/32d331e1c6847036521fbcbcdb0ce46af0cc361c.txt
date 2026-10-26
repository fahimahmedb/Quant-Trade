# WEATHER FORWARD ARCHITECT STATE — V2 — 2026-09-29

```text
ROLE                          = Weather Forward V2 Architect / convergence authority
STATUS                        = DONE (V2 spec, manifest, delta, power table, synthetic sim, this state: committed and pushed)
BRANCH                        = claude/charming-allen-948kd8
WEATHER_FORWARD_SPEC_V2       = READY_FOR_INDEPENDENT_REAUDIT
WEATHER_FORWARD_SPEC_V1       = HISTORICAL_FROZEN_OBJECT (726070a, byte-identical in this branch)
EXPERIMENT_FEASIBILITY        = BLOCKED_POWER_BELOW_DECLARED_MEUE   (Astra's; unchanged until Astra re-audits)
HURDLE_SAMPLE_INCOMPATIBILITY = FALSE
FABLE_DESIGN_CHALLENGE        = DONE_ADVISORY
BUILDER_AUTHORIZED            = FALSE
REAL_CAPITAL_AUTHORIZED       = FALSE
LIVE_TRADING_AUTHORIZED       = FALSE
t0                            = NOT_DECLARED
ACCESS_USER_REPORTED          = TRUE
LEGAL_ACCESS_CONFIRMED        = UNKNOWN
TRADING_RULE_CHANGED          = FALSE
EXECUTION_MODEL_CHANGED       = TRUE (CONSERVATIVE slippage only)
OUTCOME_INFORMATION_USED      = FALSE
NEXT_AUTHORIZED_ACTION        = INDEPENDENT ASTRA RE-AUDIT OF THE EXACT V2 COMMIT (not Builder, not t0, not capital)
```

## Inputs read (exact objects; none modified)

- `QUANT_NORTH_STAR.md`.
- V1 spec, manifest, architect state @ `726070a199957a6fc05515ebb3027e945028fddc` (brought into this branch by fast-forward; blobs byte-identical).
- Astra feasibility review @ `e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250` (fast-forward; byte-identical).
- Fable design challenge @ `5760ffa5b5da2a988cfe6d1503c86c561acf9b1f` (merged without change; byte-identical).

## Live data read by this Architect (pre-outcome metadata only)

`gamma-api.polymarket.com/events?tag_slug=weather&closed=false` (4 pages, 357 events, 2026-09-29 ≈ 17:58 UTC): titles, market `groupItemTitle`, descriptions, `resolutionSource`, `orderPriceMinTickSize`, `orderMinSize`, `negRisk`, `feeSchedule`. Findings used: 66/66 °F ladders = 2 tails + nine contiguous 2 °F buckets, NOAA template in whole °F, 11 °F stations; 191 NOAA °C ladders = 11 legs with nine single-degree buckets, 37 °C stations; non-NOAA: Hong Kong, Jinan, Taipei, Zhengzhou; tick 0.001 on 1,550 and 0.01 on 1,431 of 2,981 temperature markets; `feeSchedule` {rate 0.05, takerOnly, exponent 1, rebateRate 0.25}. No price, book, settlement, resolution, trade, wallet, leaderboard or P&L field was read or computed.

## Decisions frozen (see manifest V2 section A)

Route = Family D + B hybrid, **without the gate**: θ (economic, unchanged, two-way CR) and a stratified information axis (κ_core by two-way CR; tail win count by PINM) tested in parallel; θ_ERT = 0.02; θ_PCE by frozen price-implied formula from a 14-date outcome-free observation phase; PCE_CEILING 0.10 and SE_KAPPA_CEILING 0.020 → GO/NO_GO; structured model-conditional upper bound for exclusions; two-way (5-date block × ICAO) dependence, max-of-three SE; readiness by usable resolved dates; capture-time book contract; °F included by exact interval arithmetic; CONSERVATIVE slippage one tick; T_entry allocation with hash tie-break; mechanics codes over a baseline; one analysis at D_120 + 10 days; no interim; VALIDITY × SCIENTIFIC (INFORMATION × ECONOMIC) × OPERABILITY state machine.

## Independent checks performed

- Analytic: N_naive, MDE, date ceiling, label probabilities (power table §2–3), reproducing Astra §6.3 and Fable §1.1 exactly.
- Synthetic Monte Carlo (script committed; no market data): engine sizes and powers, PINM vs CR, date-only vs two-way, gate cost, tail detection, structured-bound coverage, false-exclusion rates, state distributions (power table §4).

## Remaining limitations (none CRITICAL)

1. **MAJOR (disclosed, non-blocking):** exclusion claims on pooled θ are conditional on the tail models (TPM ∨ SHR); an edge concentrated in the cheapest legs beyond both models can be under-bounded (SIMULATED hidden-lottery coverage 0.86–0.89 vs 0.95 nominal; false LARGE_VALUE exclusion 0.04–0.06).
2. **MINOR:** GO/NO_GO will likely be NO_GO if the post-bias-correction leg mix resembles Astra's b = 0 cross-section (σ_eff ≈ 2.9 → θ_PCE ≈ 0.18–0.22); that is an honest pre-declared outcome.
3. **MINOR:** CR engine size with ≈ 24 date blocks and ≈ 40 stations is near nominal but may run ≈ 1–2 points high in some configurations (power table §4).
4. **MINOR:** D10 bias contamination by NO_DATA_LOWEST settlements accepted as frozen and disclosed.
5. **MINOR:** PINM dependence is ASSUMED (gates only rare tail counts).

## Blockers

None scientific. Procedure items before t0: manifest V2 section B.

## Next action

Independent Astra re-audit of this exact V2 commit. Builder remains unauthorised; t0 is not declared; no capital.
