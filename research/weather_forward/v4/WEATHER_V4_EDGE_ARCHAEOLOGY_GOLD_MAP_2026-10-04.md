# WEATHER V4 — EDGE ARCHAEOLOGY / GOLD MAP — 2026-10-04

Status: **RESEARCH MAP — DO NOT IMPLEMENT BLINDLY**

Purpose: preserve the strongest ideas and external clues found after V3 ended `V3_NOT_JUSTIFIED`, before Blue compresses them into a smaller V4 research program.

This document intentionally keeps more hypotheses than a normal mission brief. It is a **working evidence map**, not a strategy specification. The owner and Blue should review it together before pruning.

Authority remains unchanged:

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED
BUILDER_AUTHORIZED = FALSE
```

No forward holdout, market outcome, P&L, deployment or capital authorization is created by this document.

---

## 0. Why this exists

V3 improved scientific hygiene but did not materially improve economic proximity:

- no freezeable candidate;
- no validated increase in independent dates;
- no credible increase in trade frequency;
- no validated variance reduction;
- no demonstrated prospective edge.

The research question therefore changes from:

> “How do we make the existing Weather design pass?”

to:

> **“Which Weather mechanism has the highest probability of becoming economically positive, and what technique are successful traders using that Quant does not yet possess?”**

The key shift is from generic forecast superiority toward **contract mechanics, information timing, resolution-source behavior, intraday lock states, execution and microstructure**.

---

# 1. Evidence discipline

Every claim below should be interpreted with one of four evidence grades:

- **A — DIRECT/OFFICIAL:** official Polymarket/NOAA/FAA/API/docs or directly inspectable protocol behavior.
- **B — REPRODUCIBLE PUBLIC ARTIFACT:** open-source code/data/backtest that Quant can independently rerun.
- **C — THIRD-PARTY OBSERVATION:** wallet analytics, dashboards, secondary reporting.
- **D — COMMUNITY/LEAD:** Reddit/forum/anecdote. Useful for hypothesis generation only.

A strong V4 candidate must not rely on a C/D claim without independent reproduction.

---

# 2. Core external findings that change the direction

## 2.1 Simple “forecast probability minus market price” is not enough

A public forward experiment (Pondletter) reportedly tested multi-model weather probabilities against Kalshi/Polymarket and found that naive ensemble-vs-price divergence was not profitable across the tested configurations.

**Interpretation:** this is highly consistent with V3’s disappointing path. It suggests that “better q” alone is unlikely to be the easiest path to positive economics.

**Consequence:** generic ECMWF/GFS probability forecasting is demoted from primary edge to **supporting signal**.

Source:
- https://pondletter.com/kalshi-weather-markets-efficient/

Evidence grade: **C/B depending on reproducibility of their published artifacts.**

---

## 2.2 Publicly visible Weather winners appear to use different archetypes

Public wallet analytics suggest at least two distinct successful behavior families:

### Archetype A — high-probability / active repricing
Examples reported publicly: HighTempTation, Weatherstappen.

Observed traits reported by third-party analytics include:
- high share of high-price entries;
- many fills per market;
- frequent selling/partial exits;
- short sessions;
- very high event win rates.

This pattern is more compatible with:

```text
fresh information
→ enter before repricing completes
→ reduce/sell
```

than with:

```text
forecast once
→ buy
→ hold to settlement
```

### Archetype B — low-price / tail accumulation
Example reported publicly: ColdMath.

Observed traits suggest:
- many cheap entries;
- much lower win rate;
- limited selling;
- large payoff asymmetry.

This can be economically positive but is a poor fit for the owner’s current objective of maximizing the probability that the system becomes net-positive.

Sources:
- https://polydata.pro/traders/hightemptation
- https://polydata.pro/traders/Weatherstappen
- https://polydata.pro/traders/ColdMath

Evidence grade: **C**.

**V4 implication:** prioritize the high-probability / information-timing archetype first.

---

# 3. The 12 high-value edge families / clues

## 3.1 Resolution-source / oracle edge

The contract is paid according to a **specific contractual resolution source and procedure**, not “true physical temperature” in the abstract.

Potential chain:

```text
physical atmosphere
!= raw station observations
!= public METAR representation
!= NOAA/WRH rendered table
!= WU fallback
!= contractual settlement value
```

If these surfaces diverge, a trader who knows the contractual surface first can have an edge even without superior forecasting.

Research object:
- exact source per market;
- exact station;
- exact unit/rounding;
- observation inclusion rules;
- cutoff behavior;
- fallback hierarchy;
- revision behavior;
- first moment the contractual result becomes inferable.

Evidence:
- current Polymarket market rules should be treated as A evidence;
- reported divergence incidents are only D/C until reconstructed.

Example rule page:
- https://polymarket.com/

Evidence grade: **A for rules; D/C for anecdotal exploitation claims.**

---

## 3.2 Faster station-observation access than ordinary METAR polling

Potential latency hierarchy for US stations:

```text
ASOS sensor
→ high-frequency ASOS / one-minute products
→ local/public ASOS voice/broadcast
→ METAR/SPECI
→ generic weather API
→ market repricing
```

The hypothesis is not “secret data”; it is that some public/official dissemination paths may update earlier than the feed most bots watch.

Possible sources to verify:
- NOAA/FAA ASOS documentation;
- Synoptic High-Frequency ASOS;
- AviationWeather METAR/SPECI;
- airport ASOS public phone lines where applicable.

Sources:
- https://docs.synopticdata.com/services/high-frequency-asos
- https://aviationweather.gov/data/api/
- https://www.faa.gov/air_traffic/publications/ATpubs/AIM/aim0403.html

Evidence grade: **A for dissemination mechanisms; economic edge unproven.**

---

## 3.3 Distinct winner archetypes imply distinct objective functions

The ecosystem appears to contain at least:

```text
A. information/repricing traders
B. tail/convexity traders
C. possible maker/microstructure traders
D. possible structural-arbitrage traders
```

Quant should **not average these into one Weather strategy**.

Each candidate family should have its own:
- estimand;
- P&L distribution;
- holding time;
- execution requirements;
- risk budget;
- evidence standard.

Evidence grade: **C + inference.**

---

## 3.4 Active exit may be part of the edge, not an implementation detail

V3 was mostly:

```text
signal → enter → hold to settlement
```

A more realistic successful mechanism may be:

```text
information shock
→ enter
→ market reprices
→ sell/reduce
→ possibly re-enter on next shock
```

This changes what must be modeled:

- markout after 1s / 5s / 30s / 1m / 5m;
- fill probability;
- spread capture/loss;
- adverse selection;
- exit depth;
- inventory duration.

**Critical implication:** a forecast can be economically useful even if it is not accurate enough to beat settlement directly, provided it predicts **the next repricing**.

Evidence grade: **C + strong inference from wallet behavior.**

---

## 3.5 Historical L2 / market microstructure data may now exist via third parties

A third-party provider, Marketlens, claims historical Polymarket Weather trades/order books/candles/resolutions.

If accurate and sufficiently timestamped, this could convert a multi-month prospective latency study into an immediate retrospective event study.

Use only after validating:
- exact timestamp semantics;
- full depth vs reconstructed snapshots;
- missing intervals;
- universe completeness;
- license/cost;
- whether data are point-in-time and unmodified.

Source:
- https://marketlens.trade/polymarket-weather-data

Evidence grade: **C until audited.**

**Potential value:** extremely high because it can answer:

```text
new observation/model run at t0
→ executable book at t0
→ +1s
→ +5s
→ +30s
→ +1m
→ +5m
```

---

## 3.6 Daily-high “lock” / fade edge

Once the day is advanced, the question changes from:

> “What will the daily maximum be?”

to:

> “Will the already-observed running high be exceeded again?”

That second problem can be far easier.

A public open-source Weather Command Center ships two-year ASOS artifacts and reports very high late-day “running high survives to close” rates for many cities.

Potential strategy state:

```text
running high H
current temperature << H
declining trend
late local time
remaining model envelope below H
→ probability(new high) small
→ some higher buckets become economically fadeable
```

Source/artifacts:
- https://github.com/testedmedia/polymarket-weather-command-center
- `data/backtest/asos_hourly_hold_rates_v1.json`
- `data/backtest/asos_fade_lock_v1.json`

Evidence grade: **B for the shipped statistics; economic execution edge not yet validated.**

---

## 3.7 Daily-low “lock” may be the mirror image and potentially more attractive

If the daily minimum is often established around the overnight/early-morning low, then after sunrise the question can become:

> “Will today make a new low later?”

Potential advantage:
- low may be known relatively early;
- many hours remain for market repricing;
- could create a longer economic window than late-day high lock.

This was not seriously explored in V3.

Required study:
- per city: time-of-final-low distribution;
- conditional probability the running low survives;
- current temperature/trend;
- cloud/wind/front regime;
- settlement-source reliability;
- market response speed.

Evidence grade: **inference; must be built from A/B data.**

---

## 3.8 Source-migration edge

The Weather product’s settlement infrastructure may have changed over time (for many markets, current rules may reference NOAA/Weather.gov surfaces where older tooling assumed WU).

Any migration can create temporary edge if legacy bots still price using:
- old source;
- wrong station;
- wrong rounding;
- wrong daily summary;
- outdated fallback logic.

Research target:

```text
legacy-implied settlement
vs
current-contractual settlement
```

Trade only when the two materially diverge and the current rule is unambiguous.

Possible source for mapping current exchange rules:
- https://www.wethr.net/exchanges/polymarket-com
- official Polymarket market-resolution pages must supersede all secondary mappings.

Evidence grade: **C for aggregate mapping; A per individual market rule.**

---

## 3.9 Data-outage / fallback-rule edge

Rare but potentially high-value states:

```text
primary source incomplete/unavailable
→ contractual fallback becomes increasingly likely
→ market continues to price physical weather / normal source
→ fallback-implied outcome differs
```

Possible mechanisms:
- missing observations;
- delayed ingest;
- viewer outage;
- source cutoff reached;
- documented fallback to secondary source;
- documented default bracket behavior.

This is not a daily scalable strategy, but it may be a high-EV exception handler.

Evidence grade: **A if rule explicitly states fallback; economic occurrence frequency unknown.**

---

## 3.10 City/model specificity may dominate a global weather model

The open-source Weather Command Center ships two-year backtest artifacts across many models/cities and reports that only a small number of city/model combinations survive stronger verification gates.

Examples claimed in its README include:
- London / UKMO;
- London / UKMO 2km;
- London / ICON;
- NYC / GFS-HRRR.

The same project’s bias-adjustment validation is heterogeneous:
- aggregate modest lift;
- stronger in some °F-city subsets;
- negative in some °C-city subsets.

This strongly argues against one global R*.

Possible correct granularity:

```text
station × model family × season × lead horizon
```

rather than:

```text
one global ensemble rule
```

Source:
- https://github.com/testedmedia/polymarket-weather-command-center
- `data/backtest/polymarket_asos_ground_truth_v1.json`
- `data/backtest/bias_adjusted_polymarket_v5_validate.json`

Evidence grade: **B for artifacts; selection/overfit risk remains and must be independently audited.**

---

## 3.11 Multi-bucket / distribution trading instead of single argmax

V3’s single argmax discards information.

Candidate alternatives:

### Cluster pricing
For adjacent set S:

```text
model probability mass(S)
vs
sum executable asks(S)
```

This reduces sensitivity to a one-bucket miss.

### Complement / NO-side logic
Trade NO when the model/observation state makes a bucket implausible rather than always picking the most likely YES.

### Full mutually-exclusive basket
Use the full outcome simplex and NegRisk relationships.

This should be viewed as **distribution pricing**, not “more trades from the same signal”.

Evidence grade: **mechanically valid concept; economic edge unproven.**

---

## 3.12 Maker rebate / spread overlay

Polymarket Weather fees/rebates can make execution itself part of economics.

A small directional edge may become viable as:

```text
weak positive information edge
+ spread capture
+ maker rebate
- adverse selection
```

But maker economics are not free alpha. Public forward experiments suggest adverse selection can overwhelm naive market making.

Therefore:
- maker/rebate is an **overlay**;
- never count rebate before modeling actual fills and markout;
- do not promote it to primary edge without evidence.

Official source:
- https://help.polymarket.com/

Evidence grade: **A for fee/rebate rules; edge unproven.**

---

# 4. Additional edge families identified before the 12-point pass

These should not be lost.

## 4.1 NegRisk / structural arbitrage

Weather bucket markets are mutually exclusive.

Scan protocol-equivalent portfolios for:

```text
guaranteed payout - executable acquisition cost - fees - execution risk > 0
```

Examples:
- sum of executable YES asks below guaranteed payout;
- equivalent NO/YES portfolios enabled by NegRisk conversions;
- split/merge/conversion inconsistencies.

This requires no weather forecast.

Official protocol reference:
- https://github.com/Polymarket/neg-risk-ctf-adapter

Research reference:
- public studies of Polymarket arbitrage should be independently reproduced before relying on reported aggregate profits.

Evidence grade: **A mechanism; profitability/frequency empirical.**

---

## 4.2 Model-release latency

Different question from forecast superiority.

```text
old market price
→ new ECMWF/GFS/HRRR/UKMO/etc run arrives
→ q moves materially
→ market reprices with delay
```

Key object:

**price-response half-life after a forecast release**

Measure:
- q shock magnitude;
- pre-release spread/depth;
- first market move;
- 50%/90% repricing time;
- executable edge at each delay;
- capacity;
- false-shock rate.

This can work even if the long-run market is efficient.

Evidence grade: **strong hypothesis; requires L2/event study.**

---

## 4.3 Observation latency

Same architecture, but observation shock instead of forecast run:

```text
new authoritative observation
→ bucket feasibility changes
→ market reprices
```

This is especially compelling near:
- bucket boundaries;
- daily high/low lock transitions;
- end-of-day;
- contractual fallback states.

Evidence grade: **strong hypothesis; requires synchronized observation + L2 timestamps.**

---

## 4.4 Exact-station discipline

The market resolves on a specific station/source. A fast reading from the wrong station is worse than a slower correct reading.

Every candidate must bind:
- market ID;
- exact station;
- exact source;
- exact timezone/local-day;
- exact unit;
- exact rounding/bucket conversion.

The open-source command-center artifacts explicitly highlight station mismatch as a major failure mode.

Evidence grade: **A/B.**

---

## 4.5 Cross-venue arbitrage is dangerous unless settlement is identical

Kalshi and Polymarket may appear to ask the same weather question while using different:
- stations;
- resolution sources;
- bracket semantics;
- timing/cutoffs.

Therefore a price gap is not necessarily an arbitrage.

Only permit a cross-venue candidate if settlement equivalence is proved mechanically.

Evidence grade: **A/C depending on contract pair.**

---

# 5. Reverse-engineering winners before designing V4

Before selecting a strategy family, build an **EDGE ARCHAEOLOGY** dataset from successful and unsuccessful Weather wallets.

For each market/fill, attempt to reconstruct:

- exact city/station/source;
- side (YES/NO);
- bucket;
- entry price;
- exit price if any;
- maker/taker if reconstructible;
- size;
- number of adds;
- holding time;
- time-to-settlement;
- local clock time;
- proximity to daily high/low;
- proximity to known model release;
- proximity to METAR/SPECI/ASOS observation;
- simultaneous positions in adjacent buckets;
- simultaneous complement/NegRisk patterns;
- selling before settlement;
- event P&L distribution;
- repeated cadence / automation signature.

Use winners **and controls**. Do not infer strategy from winners alone.

Possible public starting points:
- official Weather leaderboard;
- wallet analytics sites;
- on-chain/public CLOB data;
- historical L2 provider if validated.

Terminal purpose:

```text
CLASSIFY_WALLET_ARCHETYPE
not
COPY_WALLET_BLINDLY
```

---

# 6. V4 objective should change

The owner explicitly prefers maximizing the probability that Quant obtains a positive economic result rather than maximizing jackpot EV.

Therefore the Weather-lane objective should include:

```text
P(NetPnL_7d > 0)
P(NetPnL_30d > 0)
P(NetPnL_90d > 0)
median NetPnL
5th percentile NetPnL
max drawdown
opportunities/day
median edge after all costs
capacity
edge half-life
```

This naturally favors:
- repeatable small edges;
- high-probability information shocks;
- short markout cycles;
- low tail exposure;
- low estimator variance.

It disfavors:
- rare longshots;
- huge positive skew with frequent losses;
- rules requiring very long paper windows before any inference.

---

# 7. Revised priority ranking

Current research priority, **not a claim of proven profitability**:

1. **Observation / settlement latency**
2. **High-lock + low-lock intraday states**
3. **Resolution-source migration / source divergence / outage**
4. **Model-release latency**
5. **City-specific forecast quality + distribution/multi-bucket pricing**
6. **Maker/rebate overlay**
7. **NegRisk structural arb scanner**
8. **Generic ECMWF single-argmax**
9. **Tail/longshot strategy** for this owner objective

The first three are attractive because they potentially transform a hard forecast problem into a much easier **state recognition + repricing problem**.

---

# 8. The most important conceptual change

V3 asked:

> “Can we estimate final weather outcome probability accurately enough?”

V4 should first ask:

> **“Can we know earlier than the market what the contractual resolution state or next repricing state will be?”**

That creates four different informational targets:

```text
A. FINAL WEATHER OUTCOME
B. CONTRACTUAL RESOLUTION VALUE
C. NEXT MARKET REPRICE
D. STRUCTURAL PAYOUT IDENTITY
```

V3 mostly targeted A.

The strongest new ideas target B, C and D.

These may be substantially easier to monetize.

---

# 9. Proposed V4-P0 — Edge Archaeology before strategy construction

Do **not** launch a full V4 strategy yet.

Run five bounded falsification studies:

## E1 — OBS_LATENCY
Synchronize exact-source observations with historical/existing L2.

Output:
- opportunities/day;
- markout curves;
- median executable edge;
- edge half-life;
- fillable depth.

## E2 — HIGH_LOW_LOCK
Build empirical conditional survival probabilities for running daily high and running daily low.

Output:
- lock probability by city/time/state;
- potential bucket eliminations;
- market pricing gap at lock states.

## E3 — SOURCE_DIVERGENCE
Track current contractual source vs alternative data surfaces.

Output:
- divergence frequency;
- duration;
- rule-dependent tradeability;
- fallback/outage cases.

## E4 — MODEL_RELEASE
Timestamp model releases and market response.

Output:
- repricing lag distribution;
- q-shock threshold needed;
- executable edge decay.

## E5 — STRUCTURAL / NEGRISK
Continuously scan mutually exclusive baskets.

Output:
- pure arb count;
- executable depth;
- net edge after fees;
- half-life;
- capital requirements.

---

# 10. Promotion gate

No family becomes a V4 candidate merely because a backtest P&L is positive.

Promote only if it demonstrates:

1. **mechanism identified;**
2. **PIT-valid data;**
3. **executable price, not theoretical midpoint;**
4. **non-trivial opportunities/day;**
5. **positive post-cost markout or guaranteed payout relation;**
6. **capacity > trivial dust;**
7. **no hidden settlement mismatch;**
8. **no dependence on future outcomes for signal construction;**
9. **forward falsification path available.**

If none of E1–E5 clears this gate, stop Weather rather than restart another broad forecasting project.

---

# 11. What NOT to lose from the open-source command-center artifacts

Repository:
- https://github.com/testedmedia/polymarket-weather-command-center

Potentially valuable artifacts to independently audit:

- `polymarket_asos_ground_truth_v1.json`
- `asos_hourly_hold_rates_v1.json`
- `asos_fade_lock_v1.json`
- `buynosafe_audit_17cities_v1.json`
- `asos_wu_all_cities_verify.json`
- `bias_adjusted_polymarket_v5_train.json`
- `bias_adjusted_polymarket_v5_validate.json`
- model/city combo artifacts.

Important warnings:
- headline claims are author-generated, not independent validation;
- some proxy statistics are ASOS, not Polymarket settlement truth;
- some city/model selection may be exposed to multiplicity/overfit;
- current market resolution rules may have changed after the artifact period.

Still, these artifacts are unusually valuable because they give Quant something reproducible to attack rather than anecdotes.

---

# 12. Immediate research questions for owner + Blue

Before any V4 implementation, resolve together:

1. Do we agree that **P(NetPnL_H > 0)** is the primary Weather objective?
2. Do we prioritize **high-probability active repricing** over tail/convexity?
3. Are we willing to acquire/validate third-party historical L2 if cost is reasonable?
4. Should exact source/oracle tracking become a first-class Quant primitive?
5. Should daily-low markets be treated as a separate lane from daily-high?
6. Should wallet reverse-engineering be used only for mechanism discovery, never imitation?
7. Which of E1–E5 deserves the first bounded experiment?
8. What economic minimum kills a lane early (e.g. opportunities/day, median net edge, capacity)?

---

# 13. Current thesis, deliberately not frozen

The strongest working thesis after the two research passes is:

> **Weather may be more monetizable as an information-timing / contract-state / repricing problem than as a generic meteorological forecasting problem.**

Potential dominant chain:

```text
exact contractual source
        +
faster / cleaner observation
        +
high/low lock state
        +
market repricing delay
        +
active execution
        +
optional maker/rebate overlay
        ↓
higher P(positive economics)
```

Forecast models remain useful, especially city-specific/local models, but mainly as:
- residual uncertainty estimators;
- lock-state confirmation;
- release-shock detectors;
- probability mass over adjacent buckets.

They are no longer assumed to be the edge by themselves.

---

# 14. Sources / leads preserved for follow-up

Official / direct:
- https://polymarket.com/
- https://help.polymarket.com/
- https://github.com/Polymarket/neg-risk-ctf-adapter
- https://aviationweather.gov/data/api/
- https://www.faa.gov/air_traffic/publications/ATpubs/AIM/aim0403.html
- https://docs.synopticdata.com/services/high-frequency-asos

Reproducible/open-source:
- https://github.com/testedmedia/polymarket-weather-command-center

Third-party / leads requiring audit:
- https://marketlens.trade/polymarket-weather-data
- https://polydata.pro/
- https://www.wethr.net/exchanges/polymarket-com
- https://pondletter.com/kalshi-weather-markets-efficient/

Community leads:
- Reddit / Polymarket weather discussions on resolution-source divergence, settlement incidents and observation latency.

---

# 15. Governance note

This file intentionally preserves hypotheses that will later be cut.

Do not turn it directly into a Builder mission.

Next step is **owner + Blue pruning**:

```text
GOLD MAP
→ challenge each mechanism
→ rank by P(success) × evidence × speed × capacity
→ retain 2–3 bounded experiments
→ kill the rest
```

That pruning step should happen before V4 is pre-registered.
