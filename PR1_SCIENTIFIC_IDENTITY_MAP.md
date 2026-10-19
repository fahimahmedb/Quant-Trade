# PR #1 Scientific Identity Map — Forensic Audit

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
PR #1 head reviewed: `c60c8ab20b3f08add097e25e7295ba1196b0e4a6`
Status: `PARTIAL_SEMANTIC_RECONCILIATION`

## Purpose

This document maps the scientific history preserved in PR #1 into economic/mechanism families so that later Research OS work cannot accidentally present old experiments as novel merely because filenames, labels, instruments or surface syntax changed.

This is **not** a migration into the operational Legacy ledger. It is an audit-side semantic map only.

No historical verdict is changed here. No new backtest is run. No missing result is recreated.

## 1. Chronology inside PR #1

PR #1 does not have one single scientific verdict. It contains several successive campaigns.

### 2026-07-25 — early `FINAL_RESEARCH_REPORT.md`

This report summarizes an earlier 50+ hypothesis campaign and concludes that, after bug fixes and audit, no real directional edge beat Buy & Hold on NDX. It records critical failures including:

- invalid drawdown calculation;
- broken fractional-differentiation implementation;
- lookahead/full-sample threshold issues in several early hypotheses;
- weak classical/alternative signals;
- ML/fallback failures;
- vol-targeting as risk management rather than a universal alpha generator.

Important forensic rule: despite its filename, this is **not the last scientific state of PR #1**, because the branch later contains additional ML work and the 110-cycle non-ML backlog.

### 2026-07-26 — ML campaign state

`ITERATION_STATUS.md` records a 50-test parallel ML batch that failed because of a shared broadcasting bug and a later 10-test sequential campaign that was still running at that document's timestamp.

A failed run caused by code shape mismatch is operational/test-harness evidence, not 50 economic FAIL verdicts.

### 2026-07-28 to 2026-07-29 — non-ML adaptive backlog

`finance/trading/NONML_STRATEGY_BACKLOG.md` records completed cycles #0 through #110.

Cycles #111 and #112 are explicitly `à faire` and therefore **UNTESTED** in the reviewed PR #1 head.

The backlog uses repeated pre-registration/result/audit cycles, but later hypotheses are often informed by earlier PASS/FAIL findings. The campaign is therefore adaptive at the family level even where each individual cycle used `n_trials=1` internally.

### 2026-07-29 — formal family correction

A 13-member family of hierarchical vol-targeting gates was jointly tested with SPA/DSR:

- SPA p-value = `0.1924`
- DSR = `0.8883`
- H0 not rejected
- best member identity changes across three temporal folds
- audit notes that `n_trials=13` is optimistic relative to roughly 110 adaptive looks on the same historical NDX data

This family-level evidence outranks the individual PASS labels when the question is whether that shared mechanism is statistically established.

## 2. Semantic family map

### F01 — Earnings surprise / PEAD

Representative cycle:

- #0 PEAD, NDX-100 earnings surprise

Observed historical verdict:

- primary result: FAIL under the preregistered significance threshold
- preregistration ordering is supported by commit chronology
- strict PIT cleanliness is qualified because surprise tercile thresholds were derived from the full 2021-2026 distribution; the adversarial audit reports 5.2% assignment changes under causal expanding thresholds

Legacy crosswalk:

- no exact `earnings` / PEAD identity was found in the reviewed Legacy ledger

Duplicate hazard:

- HIGH. Any future NDX earnings-surprise/post-earnings-drift candidate must first reconcile this exact PR #1 lineage.

Import posture:

- `NEGATIVE_OR_QUALIFIED_HISTORICAL_KNOWLEDGE`
- do not mark as pristine/untested

---

### F02 — Short-horizon reversal / contrarian / post-shock rebound

Representative cycles:

- #5 short-term reversal stock-level — catastrophic FAIL
- #13 post-drawdown rebound — FAIL
- #22 short pullback rebound — FAIL
- #24 single-day shock rebound — FAIL
- #55 failed breakout contrarian — FAIL
- #62 failed breakdown rebound — FAIL
- #75 52-week-low contrarian tilt — FAIL

Legacy crosswalk:

- strong family overlap with existing Legacy record:
  - `RESEARCH_FAMILY_ID = equity-index-short-horizon-reversal`
  - `HYPOTHESIS_ID = TSR-NDX-001`
  - historical decision `KILL` for the fixed legacy expression

Important distinction:

- PR #1 contains several expressions/universes beyond the exact fixed `TSR-NDX-001` expression; they should not all be collapsed into one exact-ID duplicate.
- however, the mechanism family is heavily spent and negative across several constructions.

Duplicate hazard:

- VERY HIGH.

Import posture:

- `NEGATIVE_FAMILY_KNOWLEDGE_WITH_EXPRESSION_LEVEL_PROVENANCE`

---

### F03 — Cross-sectional momentum / price-strength selection

Representative cycles:

- #4 52-week-high stock-level momentum — individual PASS
- #14 short-term Winners momentum — individual PASS, strong caution because 2021-2026 bull/AI-semi regime
- #73 academic 12-1 momentum — individual PASS
- #82 momentum consistency — individual PASS
- combinations/overlays include #11, #18, #23, #33, #38, #42, #47/#48 style variants, #51, #74, #83, #85, #88

Observed pattern:

- momentum is one of the most repeatedly positive individual families in the backlog
- many later combinations are explicitly descendants of earlier successful momentum constructs
- the same 2021-2026 stock-level sample is repeatedly reused for several variants

Legacy crosswalk:

- reviewed Legacy contains `time-series-momentum-macro` / `B4-MACRO-TSMOM`, but that is a different mechanism expression and universe:
  - time-series trend
  - 3 ETFs
  - macro universe
  - family rejected under its own frozen gate
- therefore `B4-MACRO-TSMOM` is **related but not an exact identity** for PR #1 cross-sectional NDX-100 momentum.

Duplicate hazard:

- VERY HIGH for NDX-100 momentum selection and momentum-plus-overlay variants.

Import posture:

- `PROMISING_RETROSPECTIVE_BUT_HEAVILY_ADAPTIVE_AND_SAMPLE_SPENT`
- individual PASS must not be promoted to prospective edge without independent fresh evidence

---

### F04 — Index trend regime / long-horizon trend overlays

Representative cycles:

- #29 SMA200 trend overlay — PASS
- #34 Golden Cross — PASS
- #36 MACD — FAIL
- #37 index 52-week-high proximity — PASS
- #40 Donchian-20 breakout — FAIL
- #60 SMA50 — PASS
- #66 SMA200 slope — PASS
- #67 Golden Cross + vol-targeting — FAIL
- #68 slope + vol-targeting — PASS
- #91 days-since-high — FAIL
- #107 rolling Sharpe regime — FAIL
- #108 short streak regime — FAIL

Observed pattern:

- slower/longer trend definitions frequently outperform short/reactive trend definitions in this historical sample
- this insight generated multiple descendant hypotheses, increasing adaptive-trial dependence

Legacy crosswalk:

- related to `time-series-momentum-macro` / B4 at a broad mechanism level, but not exact because universe, instruments, expression and validation windows differ materially

Duplicate hazard:

- HIGH.

Import posture:

- `RETROSPECTIVE_PATTERN_NOT_PROSPECTIVE_EDGE`

---

### F05 — Calendar / seasonal equity overlays

Representative cycles and subfamilies:

- turn-of-month / month-end: #2, #8, #19, #21, #65, #71
- Halloween / seasonality: #17, #20, #21
- Santa Claus: #6, #64, #72
- day-of-week / weekend: #3, #25, #56, #105
- holidays: #7, #27, #70
- January: #12, #59, #76, #80, #86
- presidential cycle: #30
- triple witching: #26

Observed pattern:

- mixed individual PASS/FAIL
- later variants often explicitly adapt earlier successful windows or decompose them
- #71 identifies end-of-month, rather than beginning-of-month, as the stronger component in that historical sample

Legacy crosswalk:

- existing Legacy record `month-end-pension-rebalance` is economically related to month-end institutional-flow ideas, but it is not the same expression:
  - SPY/TLT contrarian flow proxy
  - different mechanism claim
  - different sample and execution
- no reviewed Legacy identity establishes exact coverage of the broader PR #1 calendar family

Duplicate hazard:

- HIGH for month-end and annual calendar expressions.

Import posture:

- `MIXED_RETROSPECTIVE_CALENDAR_FAMILY`

---

### F06 — Overnight / open-close / gap effects

Representative cycles:

- #1 overnight vs intraday — FAIL
- #49 gap overlay — FAIL
- #69 overnight-only decomposition — FAIL, costs structurally destructive and raw edge weak

Related but distinct Legacy item:

- `policy-calendar-pre-fomc` studies a specific event-conditioned overnight return and must not be conflated with unconditional overnight/session decomposition.

Duplicate hazard:

- MEDIUM-HIGH.

Import posture:

- `NEGATIVE_GENERAL_SESSION_EFFECT_KNOWLEDGE`

---

### F07 — Static leverage / continuous volatility scaling / risk targeting

Representative cycles:

- #9 calm-vol overlay — FAIL
- #10 continuously leveraged Buy & Hold — FAIL under Sharpe criterion
- #31 high-vol overlay — FAIL
- #43 continuous vol-target 15% — FAIL as alpha, large risk reduction
- #44 defensive vol-target <=1x — FAIL return criterion despite risk improvement
- #45 Leaders + 15% vol-target — FAIL
- #46 vol-target 20% — individual PASS
- #48 Leaders + 20% target — individual PASS with partial robustness
- #50 Parkinson-vol target — individual PASS

Earlier report context:

- the July 25 report already concluded that vol-targeting is primarily a risk-management tool and does not rescue weak base signals

Scientific identity rule:

- distinguish `risk management improvement` from `alpha/edge`.
- reduced MDD alone must not be imported as evidence of positive economic edge.

Duplicate hazard:

- VERY HIGH.

Import posture:

- `RISK_MANAGEMENT_KNOWLEDGE; ALPHA_NOT_ESTABLISHED_AS_A_GENERAL_MECHANISM`

---

### F08 — Hierarchical vol-targeting gated by state signals

This is the most important adaptive subfamily for anti-restart purposes.

Representative earlier descendants include trend/calendar/breadth gates such as #47, #54, #57, #68, #72, #80 and later state-gate variants.

The formal 13-member family correction specifically covers:

- internal breadth (#77 family member)
- #78 dispersion
- #89 weakness breadth
- #90 correlation regime
- #94 momentum breadth
- #96 SMA200 breadth
- #97 net breadth
- #98 SMA200 + momentum breadth AND
- #99 concentration
- #100 momentum dispersion
- #104 range position
- #106 momentum-dispersion + trend AND
- #109 beta dispersion

Formal family verdict:

- SPA p = 0.1924
- H0 not rejected
- best member momentum-dispersion DSR = 0.8883 < 0.95
- temporal best-member identity changes across all three folds
- adversarial audit states `n_trials=13` is likely optimistic because these members arose after roughly 110 adaptive cycles on the same historical data

Import posture:

- `FAMILY_EDGE_NOT_STATISTICALLY_ESTABLISHED`

Critical anti-restart rule:

- NO later Research OS candidate that merely changes the gate (breadth, dispersion, correlation, concentration, trend, range position, beta dispersion, etc.) around the same NDX vol-targeting core may be treated as a fresh mechanism without proving material economic distinctness.

Duplicate hazard:

- MAXIMUM.

---

### F09 — Cross-sectional breadth / dispersion / correlation / concentration state

Representative cycles:

- #52/#57 cross-index breadth
- #63 international breadth
- #77 internal breadth
- #78 return dispersion
- #81 dispersion + trend AND
- #89 weakness breadth
- #90 correlation regime
- #94 momentum breadth
- #96 SMA200 breadth
- #97 net breadth
- #98 breadth AND
- #99 concentration
- #100 momentum-score dispersion
- #103 five-market breadth
- #104 range position
- #106 dispersion + trend AND
- #109 beta dispersion

Relationship to F08:

- many of these signals are not standalone P&L strategies; they are gates for the same hierarchical vol-targeting mechanism
- their statistical identity therefore includes both the gate signal and the shared underlying exposure engine

Import posture:

- `STATE_SIGNAL_LIBRARY_WITH_SHARED_EXPOSURE_DEPENDENCE`

Critical identity rule:

- different gate observables do not automatically imply independent economic exposures.

---

### F10 — Multi-market confirmation / lead-lag

Representative cycles:

- #52 NDX + Russell confirmation — marginal/fragile individual PASS
- #57 breadth + vol-targeting — PASS
- #63 NDX + DAX simultaneous trend confirmation — PASS
- #103 broad five-market trend breadth — PASS
- #110 DAX→NDX lagged spillover — FAIL after correcting the timing premise

Important #110 correction:

- initial same-day DAX-return implementation produced an absurd result because Xetra remained open after Nasdaq's open
- corrected expression uses prior DAX session `t-1`
- corrected result is a clear FAIL

Import posture:

- simultaneous regime confirmation and true lead-lag must remain separate identities
- `DAX_PREVIOUS_SESSION_TO_NDX = NEGATIVE_HISTORICAL_RESULT`

Duplicate hazard:

- HIGH.

---

### F11 — Low-volatility / defensive stock selection and distributional tilts

Representative cycles:

- #15 low-vol stock tilt — FAIL versus reference despite lower MDD
- #28 low-vol + calendar — FAIL
- #35 low-vol + SMA200 — PASS
- #39 low-vol + index 52w-high — PASS
- #53 low-vol + hierarchical trend/vol target — PASS
- #79 momentum + low-vol double sort — FAIL
- #84 skewness stock tilt — FAIL

Observed pattern:

- defensive tilts can improve drawdown while sacrificing return
- some combinations pass only after adding another successful trend/leverage mechanism

Import posture:

- `MIXED; DO_NOT_ATTRIBUTE_COMBINATION_SUCCESS_TO_LOW_VOL_COMPONENT_WITHOUT_DECOMPOSITION`

---

### F12 — Distribution-shape / volatility-regime diagnostics used as gates

Representative cycles:

- #58 low-realized-vol regime — FAIL
- #87 intraday-range calm regime — PASS
- #92 index skewness regime — FAIL
- #93 kurtosis defensive gate — FAIL
- #95 autocorrelation regime — FAIL
- #102 vol-of-vol regime — FAIL
- #107 rolling Sharpe regime — FAIL

Observed pattern:

- many higher-moment or short-window regime descriptors do not establish a stable directional edge
- #87 is an exception on the historical sample but belongs to the same adaptive regime-gating research context

Import posture:

- `MOSTLY_NEGATIVE_OR_UNDERPROVED_REGIME_GATE_LIBRARY`

---

### F13 — Event / calendar decomposition of known positive subfamilies

Representative cycles:

- #71 decomposes ToM into end-of-month vs beginning-of-month and finds only the end-of-month variant passes
- #72 applies vol-targeting inside Santa window
- #80 applies vol-targeting to January Barometer

Scientific identity implication:

- these are descendants/conditioned versions of already tested parent families, not independent discoveries.

Import posture:

- preserve explicit parent-child lineage.

---

### F14 — Early classical / exotic / ML search before the non-ML backlog

From the July 25 report:

- classical indicators
- FracDiff
- regime-gated mean reversion
- alternative indicators
- ensemble strategies
- ML/gradient boosting/LSTM-related work

Key preserved negative knowledge:

- several apparent edges disappeared after implementation bugs were fixed
- `FracDiff` positive claims were invalid artifacts
- `H12 Vol-Adjusted FracDiff` positive claim was invalid
- early full-sample thresholds/lookahead existed in several hypotheses
- Buy & Hold remained best under the corrected campaign's own criteria

From July 26 ML status:

- first 50-test parallel batch failed due one systematic shape-mismatch bug
- those 50 failed executions are **not** 50 clean economic falsifications

Import posture:

- separate `INVALID_EXECUTION`, `NEGATIVE_ECONOMIC_RESULT`, and `UNRESOLVED/RUNNING` states.

## 3. High-value anomalies / special cases that must survive migration

### A. Individual PASS is not family proof

PR #1 contains many individual `PASS` labels. These labels are local to each predeclared cycle and must not be interpreted as independent confirmations because later cycles repeatedly reuse the same datasets and are adaptively inspired by prior results.

### B. Formal multiple-testing result is negative for the 13-member hierarchical family

The 13-member SPA/DSR family result is stronger evidence about that family than any one member's local PASS.

### C. #89 is a technical PASS but scientifically non-informative

Weakness breadth activates only 5 days in 1385 (~0.36%). The backlog itself says the formal PASS does not validate the capitulation hypothesis.

### D. #41 is PASS without incremental identity

The union of SMA200 and 52-week-high signals is mathematically identical to the wider SMA200 signal on that data because one signal is a strict subset of the other. It must not count as an independent edge.

### E. #110 corrected result only

The same-day DAX→NDX construction was invalid because of overlapping market hours. Only the corrected prior-DAX-session result should enter scientific memory.

### F. #111 and #112 remain UNTESTED

Do not infer, execute, or backfill their verdicts during reconciliation.

### G. `FINAL_RESEARCH_REPORT.md` is not chronologically final

It predates later July 28-29 backlog work. Preserve it as an earlier campaign summary, not the final state of all PR #1 science.

## 4. Crosswalk against the reviewed Legacy ledger

### Exact / strong family overlap observed

1. PR #1 short-horizon reversal family ↔ `equity-index-short-horizon-reversal` / `TSR-NDX-001`
   - not every PR #1 expression is exact, but mechanism duplication risk is direct.

### Related but not exact

2. PR #1 trend/momentum overlays ↔ `time-series-momentum-macro` / `B4-MACRO-TSMOM`
   - related trend mechanism, materially different universe and expression.

3. PR #1 month-end/ToM effects ↔ `month-end-pension-rebalance`
   - related institutional/calendar mechanism, materially different asset pair and flow claim.

4. PR #1 general overnight/session effects ↔ `policy-calendar-pre-fomc`
   - both use overnight returns, but event conditioning is economically distinct.

### Material families not represented by an exact reviewed Legacy identity

At minimum:

- PEAD / earnings surprise
- NDX-100 cross-sectional 52-week-high momentum
- NDX-100 12-1 momentum
- momentum consistency
- long-horizon index trend overlays specific to NDX/multi-index daily data
- broad PR #1 calendar overlay family
- hierarchical NDX vol-targeting gate family
- breadth/dispersion/concentration state gates
- corrected DAX→NDX prior-session spillover
- intraday-range regime gate

Therefore the reviewed Legacy reconciliation does not yet fully protect Research OS against restarting PR #1 science under aliases.

## 5. Required anti-restart normalization fields

Any future migration of PR #1 families into operational scientific memory should preserve at least:

- historical source = PR #1 head / exact result artifact
- cycle number
- parent/descendant cycle IDs
- mechanism family
- universe
- base exposure
- gate / conditioning signal
- clock / lag convention
- sample window
- whether the same historical sample was already spent in parent cycles
- individual local verdict
- family-level multiple-testing verdict where available
- PIT/lookahead qualification
- implementation bug status
- economic-materiality qualification
- whether the result is informative or merely technically passes a threshold
- exact alias relationship to current Research OS / Legacy IDs

## 6. Migration safety rules

1. Never collapse `PASS`, `FAIL`, `INVALID`, `UNTESTED`, and `NON_INFORMATIVE_PASS` into a binary result field.
2. Never treat two differently named gates on the same underlying exposure as independent economic evidence without an explicit structural-identity review.
3. Never count a child combination as independent confirmation of its successful parent components.
4. Never mark #111 or #112 as tested.
5. Never import the invalid same-day DAX→NDX result from #110; use only the corrected lagged version.
6. Never import the pre-fix FracDiff/H12 metrics as valid evidence.
7. Preserve the 13-member SPA/DSR negative family result alongside all individual member results.
8. Preserve that ~110 adaptive cycles were run on overlapping historical data; this is part of trial accounting even when each cycle internally claimed `n_trials=1`.
9. Do not mutate the operational Legacy ledger until the remaining PR #1 artifact/commit provenance is fully enumerated and reviewed.

## 7. Current forensic verdict

- `PR1_COMPLETED_NONML_CYCLES = 111`  
  Explanation: cycle numbers 0 through 110 inclusive.
- `PR1_UNTESTED_NONML_CYCLES = [111, 112]`
- `PR1_SEMANTIC_IDENTITY_MAP_STARTED = TRUE`
- `PR1_SEMANTIC_IDENTITY_MAP_COMPLETE = FALSE`
- `LEGACY_EXACT_COVERAGE_OF_PR1 = FALSE`
- `INDIVIDUAL_PASS_EQUALS_ESTABLISHED_EDGE = FALSE`
- `HIERARCHICAL_VOL_TARGET_FAMILY_EDGE_ESTABLISHED = FALSE`
- `PR1_OPERATIONAL_LEDGER_MIGRATION_AUTHORIZED = FALSE`

## 8. Next audit steps

1. Attach exact prereg/result/audit filenames and commit-order evidence to the highest-value families, especially momentum, trend, ToM and hierarchical vol-targeting.
2. Build a machine-readable alias/crosswalk file suitable for later Legacy import review without modifying the current operational ledger.
3. Trace PR #1 commit chronology around cycles with known corrections (#41, #77, #89, #106, #110) to preserve only the final valid interpretation.
4. Search current Research OS hypothesis IDs for structural overlap with these PR #1 families.
5. Keep Oracle activation blocked until scientific memory and authority precedence are reconciled.
