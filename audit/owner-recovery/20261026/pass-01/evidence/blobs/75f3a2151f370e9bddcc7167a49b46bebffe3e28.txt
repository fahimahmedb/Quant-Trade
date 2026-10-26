# WEATHER V3 — BLUE ORCHESTRATION & SESSION DISPATCH — 2026-10-02

Status: ACTIVE PLANNING / RESEARCH ORCHESTRATION ONLY.

Branch:
`blue/weather-v3-orchestration-2026-10-02`

Base planning authority:
`astra/weather-forward-v2-independent-reaudit-2026-09-29@b7522b84cfda115a1147b3152e7d3b64300ead24`

Current V2 candidate remains separate:
`claude/charming-allen-948kd8@0cfdd4d25ef74e8158403ed6037fccc341fb7639`

Nothing in this V3 branch modifies or supersedes the running V2 audit loop.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED
BUILDER_AUTHORIZED = FALSE

---

## 1. BLUE objective

Weather V3 should maximize **usable economic information per calendar day and per unit of risk/capital**, not raw trade count.

The current bottleneck is not primarily compute. It is:
- too few independent time units;
- high variance, especially from low-price / TAIL geometry;
- dependence induced by the rolling bias method;
- incomplete point-in-time historical market data;
- calibrated inference losing power after honest dependence correction.

Therefore V3 research must answer, in this order:

1. Can we obtain materially more valid point-in-time information?
2. Can we reduce variance without fabricating edge or silently changing the estimand?
3. Can we remove avoidable dependence from the signal construction?
4. Can we broaden the cohort without destroying settlement / transportability coherence?
5. Only then: what experiment horizon and GO rule are scientifically feasible?

No session is asked to “make Weather pass”.

---

## 2. Bounded autonomy

Every Claude session has discretion to improve implementation and scientific method inside its work package.

### MAY do autonomously
- vectorize / refactor code;
- add diagnostics, stress cases, plots or summaries;
- propose a superior outcome-blind variant;
- stop a dominated candidate early after a documented falsification;
- split a computational plan into smaller deterministic slices;
- tighten a claim when evidence does not support the stronger one;
- add a new synthetic adversarial case when it exposes the same scientific question;
- change internal implementation if equivalence / regression evidence is committed.

### MUST checkpoint before any material deviation
Record:
`DEVIATION`
`WHY`
`SCIENTIFIC_EFFECT`
`FROZEN_SURFACE_TOUCHED`
`NEW_REAUDIT_SURFACE`

### MAY NOT autonomously
- inspect forward holdout outcomes;
- lower a statistical standard after seeing results;
- tune a threshold to make Weather pass;
- authorize Builder / t0 / live capital;
- alter the running V2 candidate or Astra evidence;
- redefine the North Star economic objective;
- silently change the estimand;
- convert an assumption into an empirical claim;
- select a strategy because it had the best realised P&L.

If a work package discovers that a better answer requires touching one of those surfaces, it must propose the change and stop at `OWNER_OR_BLUE_DECISION_REQUIRED`.

---

## 3. Compute standard — NUMPY FIRST

All heavy Monte Carlo work from V3 must use one common compute contract.

### Required architecture
- Python loops over **cells / plans only**.
- No Python loop over replications.
- Replications represented by NumPy arrays.
- Use vectorized reductions / broadcasting / `np.bincount` / `np.add.at` / indexed reductions where appropriate.
- Chunk only for RAM control.
- Preallocate reusable arrays when material.
- Avoid pandas in inner simulation loops.

### Deterministic RNG
Every independent cell/stream uses:

`SeedSequence([BASE_SEED, PLAN_ID, CELL_ID, STREAM_ID])`

The generated result for a cell MUST NOT depend on:
- slice number;
- number of sessions;
- completion order;
- CPU count.

### Three run levels
- `SMOKE = 1,000` reps: code failure detection only.
- `RESEARCH = 20,000` reps/cell: declared design search/calibration.
- `CONFIRM = 100,000+` reps: boundary/worst cells.

SMOKE results may never justify PASS or candidate selection.

### Equivalence gate
Before replacing an existing engine:
1. select a fixed declared comparison set;
2. run old and new engines;
3. show record-for-record equality where feasible, otherwise declared numeric tolerance + identical state decisions;
4. commit comparison evidence;
5. only then launch large jobs.

### Slice protocol
Every heavy plan supports:
`--slice i/n`

Each cell writes one self-contained JSONL record.
Rerun skips completed cell IDs.
Merge verifies:
- expected cell count;
- no duplicate cell ID;
- exact deterministic seed identity;
- schema version;
- plan hash.

No scientific result depends on wall-clock ordering.

---

## 4. Parallel execution graph

Start immediately in parallel:

`S0 COMPUTE INFRA`
`S1 DATA ARCHAEOLOGY`
`S2 CAPTURE ARCHITECTURE`

Then:

`S0 -> S3 TAIL / PRICE GEOMETRY`
`S1 -> S4 FORECAST / HINDCAST`
`S1 -> S6 COHORT / VENUE EXPANSION`

Then:

`S3 + S4 -> S5 VARIANCE REDUCTION / POOLING`

Then:

`S3 + S4 + S5 + S6 -> S7 BLUE V3 SYNTHESIS`

Only after S7 freezes one candidate:

`S8 FRESH ASTRA V3 AUDIT`

No Builder before S8 PASS.

---

## 5. SESSION S0 — COMPUTE INFRASTRUCTURE

Role: Builder / quantitative infrastructure engineer.
Model: Sonnet-class is sufficient.
CPU: medium/heavy.

### Goal
Make V3 simulation throughput high enough that scientific search is constrained by experimental validity, not Python overhead.

### Inputs
- existing Weather V2 simulation scripts;
- `WEATHER_V3_BLUE_WORK_BREAKDOWN_2026-10-02.md`;
- this orchestration file.

### Tasks
1. Profile representative V2 heavy cells.
2. Build a NumPy-first simulation kernel preserving exact mathematical semantics.
3. Implement deterministic cell slicing and merge/validation.
4. Implement resume-safe JSONL output.
5. Benchmark old vs new.
6. Prove equivalence on declared cells.
7. Provide a tiny public API usable by later sessions.

### Output
`research/weather_forward/v3/compute/`

Required:
- engine;
- slice driver;
- merge verifier;
- equivalence report;
- benchmark report;
- README.

### Acceptance
- deterministic across 1 slice vs N slices;
- no scientific-decision mismatch on equivalence suite;
- clean resume after interruption;
- speed and RAM reported honestly;
- no minimum speedup is required: correctness dominates speed.

---

## 6. SESSION S1 — DATA ARCHAEOLOGY

Role: independent data/research engineer.
CPU: light.
May use public web research.

### Goal
Determine what historical point-in-time information genuinely exists before redesigning the signal.

### Search separately for
A. Polymarket / prediction-market:
- historical trades;
- best bid/ask;
- order-book snapshots;
- tick/min-order changes;
- fees;
- market metadata;
- resolution timelines.

B. Meteorology:
- ECMWF historical forecasts / hindcasts;
- GFS;
- ICON;
- Open-Meteo archived forecast runs;
- station observations;
- exact forecast issuance timestamps;
- model-version breaks.

### For every source record
- exact coverage start/end;
- resolution;
- timestamp semantics;
- point-in-time validity;
- revisions;
- API/download limits;
- cost/access;
- missingness;
- whether it can be joined to the target without leakage.

### Critical distinction
`historical observation != historical forecast available at the time`.

Never substitute ERA5 / final observations for a forecast information set.

### Output
`research/weather_forward/v3/data/V3_DATA_ARCHAEOLOGY_2026-10-02.md`

and a machine-readable inventory.

### Acceptance
End with:
- `AVAILABLE_NOW`;
- `ACCESSIBLE_WITH_WORK`;
- `NOT_FOUND`;
- `NOT_POINT_IN_TIME_VALID`.

Do not invent missing history.

---

## 7. SESSION S2 — CAPTURE-ALL ARCHITECTURE

Role: data systems architect.
CPU: light.

### Goal
Design a zero-order, zero-capital collection path so future research stops losing irreplaceable point-in-time data.

### Important
This session designs only.
It does NOT declare t0 and does NOT deploy collectors unless separately authorized.

### Design
- market metadata snapshots;
- best bid/ask;
- desired order-book depth;
- timestamp semantics;
- forecast issue/run metadata;
- station/model identifiers;
- checksums;
- replayable raw immutable format;
- deduplication;
- clock synchronization;
- provenance;
- outage/gap flags.

Separate:
`DATA_T0`
`EXPERIMENT_T0`
`CAPITAL_T0`

They are different governance events.

### Output
`research/weather_forward/v3/data/V3_CAPTURE_ALL_ARCHITECTURE_2026-10-02.md`

### Acceptance
A future Builder can implement mechanically without deciding scientific thresholds.

---

## 8. SESSION S3 — TAIL / PRICE GEOMETRY

Role: quantitative design researcher.
Depends on S0.
CPU: heavy / sliceable.

### Goal
Test whether the dominant variance can be removed without silently changing the economic question.

Compare outcome-blind candidate families declared BEFORE simulation:

A. V2 geometry baseline.
B. No-TAIL entry universe.
C. Constant-payout / risk-normalized sizing.
D. Other mathematically equivalent variance controls if discovered.

The session has discretion to add a candidate only before examining that candidate's simulation outcomes; document the declaration timestamp/commit.

### Measure
- variance of theta / kappa objects;
- MDE80;
- T2/T1/NEG power;
- expected usable opportunity count;
- cost-mass concentration;
- maximum-date concentration;
- sensitivity to favourite-heavy prices;
- effect on the estimand;
- effect on economic capacity.

### Non-negotiable
A lower variance is NOT automatically better if it selects a different economic population.

### Output
`research/weather_forward/v3/design/V3_TAIL_PRICE_GEOMETRY_2026-10-02.md`

### Terminal labels
`DOMINATED`
`SCIENTIFICALLY_DISTINCT_ESTIMAND`
`CANDIDATE_FOR_V3`

No “winner” by realised P&L.

---

## 9. SESSION S4 — FORECAST / HINDCAST & BIAS REDESIGN

Role: forecast-method architect.
Depends on S1.
CPU: medium/heavy.

### Goal
Attack two sources of weakness:
1. forecast-information quality;
2. cross-block dependence from rolling 30-date bias correction.

### Candidate families
- current ECMWF/Open-Meteo rule as baseline;
- fixed historical/hindcast bias correction;
- pre-frozen multi-model ensemble ECMWF + GFS + ICON where PIT data support it;
- simple model-combination rules before complex learned weighting.

### Firewall
Historical observations may be used to estimate a correction ONLY on a declared development period.

A separate held-out forward period remains untouched.

No threshold in R* is tuned using future resolved outcomes.

### Key questions
- Does fixed bias materially reduce serial dependence?
- Does multi-model information improve forecast calibration before market comparison?
- Are improvements robust to model-version changes?
- Is the archive actually point-in-time valid?
- How much extra calendar coverage is obtained?

### Output
`research/weather_forward/v3/design/V3_FORECAST_HINDCAST_DESIGN_2026-10-02.md`

If historical forecast coverage is insufficient, say so and downgrade the candidate rather than synthesizing data.

---

## 10. SESSION S5 — COVARIATE ADJUSTMENT / HIERARCHICAL POOLING

Role: statistical-method researcher.
Depends on S3 + S4.
CPU: heavy / sliceable.

### Goal
Reduce variance without introducing post-treatment or post-outcome information.

Evaluate:
- ANCOVA;
- CUPED-type adjustment;
- fixed external coefficients;
- hierarchical station pooling;
- partial pooling only where exchangeability assumptions are explicit.

### Every covariate must be classified
`KNOWN_PRE_TRADE`
`KNOWN_ONLY_AFTER_TRADE`
`LEAKAGE_RISK`

Only KNOWN_PRE_TRADE enters a candidate estimator.

### Required comparison
For each estimator report:
- bias;
- size / coverage;
- power;
- variance;
- robustness to station heterogeneity;
- robustness to price skew;
- dependence sensitivity;
- estimand changed? yes/no.

### Output
`research/weather_forward/v3/design/V3_VARRED_POOLING_2026-10-02.md`

Complexity loses to the simpler estimator unless it produces a meaningful, calibrated gain.

---

## 11. SESSION S6 — COHORT / VENUE EXPANSION

Role: market-universe researcher.
Depends on S1.
CPU: light/medium.

### Goal
Increase genuinely informative independent opportunity flow.

Investigate:
- additional weather stations;
- additional weather contract types;
- compatible markets/venues;
- other horizons if settlement semantics remain comparable.

### Reject naive N expansion
More contracts on the same weather event are NOT independent dates.

For every expansion estimate:
- new independent date units;
- station/event dependence;
- overlap with existing risk;
- settlement-rule compatibility;
- market liquidity;
- price availability;
- ability to construct PIT data;
- transportability implications.

### Output
`research/weather_forward/v3/design/V3_COHORT_EXPANSION_2026-10-02.md`

---

## 12. SESSION S7 — BLUE V3 SYNTHESIS

Role: BLUE scientific/economic architect.
Model: strongest reasoning model.
CPU: light; consume summaries, not raw simulations.

### Inputs
S1, S3, S4, S5, S6 outputs plus S0 technical verification and S2 capture design.

### Mission
Choose the smallest coherent V3 experiment that maximizes information gained per calendar day while keeping claims valid.

Do NOT mechanically combine every promising idea.

Prefer a simpler design if the marginal improvement of an added component is small.

### Must freeze
- exact estimand(s);
- signal;
- bias method;
- price/tail universe;
- sizing semantics;
- cohort;
- inference engine;
- declared stochastic class;
- GO / NO_GO meaning;
- horizon / sequential rule;
- forward holdout;
- state machine;
- falsification criteria.

### Required economic summary
For the frozen V3 candidate estimate:
- expected usable signals/day;
- expected trades/day;
- expected independent dates/month;
- MDE80;
- time to useful answer;
- capital utilization in shadow;
- edge-replacement / learning value.

### Terminal states
`V3_CANDIDATE_READY_FOR_ASTRA`
or
`V3_NOT_JUSTIFIED`

No Builder authorization.

---

## 13. SESSION S8 — FRESH ASTRA V3 AUDIT

Role: independent adversarial reviewer.
Must be a fresh context that did not design S3-S7.

Audit exact frozen SHA only.

### First attacks
1. point-in-time leakage;
2. hidden selection from multiple V3 candidates;
3. size / coverage over the actually declared class;
4. dependence and price concentration;
5. estimator drift / changed estimand;
6. transportability;
7. opportunity-count inflation from correlated markets;
8. historical archive/version bias;
9. forward-holdout contamination;
10. state-machine aliases that imply prospective edge.

### Terminal
`ASTRA_V3 = PASS_SCIENTIFIC_CONTRACT_ONLY`
or
`BLOCKED_<REASON>`

A PASS does not prove economic edge and does not authorize capital.

---

## 14. Scheduling / concurrency

At most three CPU-heavy simulation sessions should run simultaneously unless account/compute limits are explicitly raised.

Recommended launch order:

Wave A now:
- S0 Compute Infrastructure
- S1 Data Archaeology
- S2 Capture Architecture

Wave B as soon as dependencies resolve:
- S3 Tail / Price Geometry
- S4 Forecast / Hindcast
- S6 Cohort Expansion

Wave C:
- S5 Variance Reduction / Pooling

Wave D:
- S7 Blue Synthesis

Wave E:
- S8 fresh Astra

Other Quant lanes continue independently; Weather must not monopolize the system.

---

## 15. Session checkpoint contract

Every session must commit and push after each durable phase.

Each work package maintains:
`CURRENT_PHASE`
`CURRENT_HEAD`
`INPUT_SHA_SET`
`OPEN_QUESTIONS`
`FAILED_CANDIDATES`
`SURVIVING_CANDIDATES`
`DEVIATIONS`
`NEXT_EXACT_ACTION`

On interruption, resume from Git only.

No important result may exist only in chat or scratch storage.

---

## 16. Hand-back protocol

Final chat hand-back from each session: maximum 12 lines.

It must include:
1. branch;
2. exact SHA;
3. mission status;
4. main quantitative result;
5. failed candidates;
6. surviving candidate(s);
7. scientific limitation;
8. deviation, if any;
9. files committed;
10. next dependency;
11. owner decision required, if any;
12. authority flags.

All details live in committed files.

---

## 17. Immediate decisions deliberately deferred

The orchestration does NOT yet choose:
- V3's final tail policy;
- final forecast ensemble;
- final estimator;
- final cohort;
- W / sequential horizon;
- GO thresholds;
- any capital sizing;
- DATA_T0 activation.

Those decisions are made only after the relevant work packages provide evidence.

This is intentional: Blue is organizing the search without pre-selecting the answer.

---

## 18. Current V2 separation

The ongoing V2 cycle-3 recheck remains authoritative for V2.

V3 sessions may read V2 scientific findings as design evidence, but may not:
- commit to the V2 candidate branch;
- modify Astra audit evidence;
- reinterpret a V2 BLOCK as a V3 PASS;
- use any future Weather outcome to tune V3.

The two lanes converge only if Blue later explicitly freezes V3.
