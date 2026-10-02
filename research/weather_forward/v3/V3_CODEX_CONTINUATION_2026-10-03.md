# WEATHER V3 — CODEX CONTINUATION DISPATCH — 2026-10-03

Authority:
- Blue orchestration branch: blue/weather-v3-orchestration-2026-10-02
- Blue orchestration head before this dispatch: 44d9ce2009ef5400132f84d5002ea0c52f66ed9f
- S0 Claude WIP: claude/weather-v3-s0-compute-2026-10-02@1fa81100d3d4f32cd8f8842356c043c3d502910d
- S1 Claude DONE: claude/weather-v3-s1-data-archaeology-2026-10-02@697865d4f8ba5ecfcb23025272b50b5eee2b2f30
- S2 Claude DONE: claude/weather-v3-s2-capture-architecture-2026-10-02@9751368c90150a71eb88147ff69446f0711c81f2

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED
BUILDER_AUTHORIZED = FALSE

Codex may continue implementation/research from committed Git state. It must not infer missing state from chat.

---

## C0 — finish S0 compute infrastructure

Branch:
codex/weather-v3-s0-finish-2026-10-03

Base:
1fa81100d3d4f32cd8f8842356c043c3d502910d

Read first:
- QUANT_NORTH_STAR.md
- research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md
- research/weather_forward/v3/coordination/S0_PROGRESS.md
- research/weather_forward/v3/compute/ACCEPTANCE_REPORT.json
- research/weather_forward/v3/compute/EQUIVALENCE_LAYER_A_REPORT.json
- research/weather_forward/v3/compute/COMPARISON_SET.json

Continue exactly from S0_PROGRESS.NEXT_EXACT_ACTION.

Required:
1. run layer-B generator/statistical equivalence against old V2 engine;
2. commit EQUIVALENCE_LAYER_B_REPORT.json;
3. run honest speed + memory benchmark old vs new;
4. write README + benchmark report;
5. mark S0.DONE only if:
   - layer A PASS,
   - layer B within predeclared tolerance,
   - identical scientific decisions,
   - 1/n-slice determinism PASS,
   - resume PASS,
   - merge negative tests PASS.
6. Do not tune tolerances after seeing results.
7. If layer B fails materially, diagnose and repair the engine; rerun both A and B before DONE.

Bounded autonomy:
Codex may refactor NumPy layout, chunking and test harnesses, but cannot change scientific definitions, thresholds, RNG contract or V2 semantics.

Final handback <=12 lines and push exact SHA.

---

## C4 — S4 forecast/hindcast design

Branch:
codex/weather-v3-s4-forecast-hindcast-2026-10-03

Base:
697865d4f8ba5ecfcb23025272b50b5eee2b2f30

Read:
- QUANT_NORTH_STAR.md
- research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md
- research/weather_forward/v3/data/V3_DATA_ARCHAEOLOGY_2026-10-02.md
- machine-readable S1 inventory
- only the V2 signal/bias sections needed to reconstruct the current rule

Mission:
Execute S4 from the Blue orchestration.

Priority:
1. determine which as-issued forecast sources can actually support a historical redesign;
2. design fixed hindcast/history-based bias correction that does not create the 30-day rolling dependence;
3. evaluate simple multi-model ensemble candidates only where PIT data supports them;
4. preserve a clean development/holdout firewall;
5. quantify expected effect on serial dependence and information availability before proposing complexity.

Do not download/open quarantined market outcomes or P&L.
Do not tune R* thresholds on resolved market outcomes.

Codex may add public-source verification, small validation scripts, and alternative outcome-blind correction families if they answer the same question.

Output:
research/weather_forward/v3/design/V3_FORECAST_HINDCAST_DESIGN_2026-10-03.md
plus any small reproducible support scripts/data inventory deltas.

Terminal:
CANDIDATE_FOR_V3
or
INSUFFICIENT_PIT_HISTORY
or
DESIGN_REQUIRES_OWNER_ACCESS

Push exact SHA.

---

## C6 — S6 cohort / venue expansion

Branch:
codex/weather-v3-s6-cohort-expansion-2026-10-03

Base:
697865d4f8ba5ecfcb23025272b50b5eee2b2f30

Read:
- QUANT_NORTH_STAR.md
- research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md
- research/weather_forward/v3/data/V3_DATA_ARCHAEOLOGY_2026-10-02.md
- machine-readable S1 inventory

Mission:
Execute S6 from Blue orchestration.

Goal:
increase genuinely independent information flow, not nominal contract count.

For each possible expansion:
- extra independent date/event units per month;
- shared-weather dependence;
- station overlap;
- settlement semantic compatibility;
- liquidity / price observability;
- PIT data availability;
- transportability implications;
- whether it changes the estimand.

Explicitly reject counting correlated contracts on the same weather realization as independent dates.

Codex may discover additional stations, contract families or compatible venues, but must keep them in separate candidate families if settlement semantics differ.

Output:
research/weather_forward/v3/design/V3_COHORT_EXPANSION_2026-10-03.md
plus machine-readable candidate table.

Terminal per candidate:
CANDIDATE_FOR_V3
DOMINATED_CORRELATED_COUNT
INCOMPATIBLE_SETTLEMENT
INSUFFICIENT_PIT_DATA
OWNER_ACCESS_REQUIRED

Push exact SHA.

---

## Convergence rule

C4 and C6 may run immediately because S1 is DONE.

C3 (tail/price geometry) must NOT start until C0 marks S0.DONE.

After C0 PASS:
Blue should create a fresh C3 branch from the finished S0 SHA and execute S3 using the NumPy engine.

S5 waits for C3 + C4.
S7 waits for C3 + C4 + S5 + C6.
S8 remains fresh Astra only after S7 freezes one candidate.

Nothing here authorizes deployment or capital.
