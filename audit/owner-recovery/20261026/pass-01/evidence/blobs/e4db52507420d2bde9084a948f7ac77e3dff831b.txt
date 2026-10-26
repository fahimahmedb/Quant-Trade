# QUANT — ECONOMIC REORIENTATION / STRATEGY DISCOVERY CHECKPOINT — 2026-09-29

Status: DURABLE PROJECT CHECKPOINT  
Purpose: explain why Quant moved from “a robot with no proven strategy” toward receipt-first strategy discovery, record the strongest measured evidence found so far, and preserve how validated strategies are intended to reconnect to the existing Quant chassis.

```text
PROJECT_OBJECTIVE                    = UNCHANGED
TERMINAL_OBJECTIVE                   = NET ECONOMIC GAIN / LONG-RUN REAL WEALTH GROWTH AFTER REAL FRICTIONS
ROBOT_CHASSIS                        = SUBSTANTIAL / REUSABLE
REAL_DATA_POSITIVE_PATH              = NOT YET PROVEN
RESEARCH_MODE                        = RECEIPT_FIRST + FALSIFICATION_FIRST
VALIDATED_DEPLOYABLE_STRATEGY        = NONE YET
REAL_CAPITAL_AUTHORIZED              = FALSE
WEATHER_t0                           = NOT_DECLARED
CURRENT_DIRECTION                    = FIND -> FALSIFY -> VALIDATE -> INTEGRATE INTO QUANT
```

---

## 1. Why this checkpoint exists

Quant did not change its terminal objective.

The North Star remains:

> increase real capital through repeatable discovery, selection, sizing, execution and replacement of genuine market edge.

The architecture already defines Quant as a persistent system, not a single strategy:

```text
DATA
  -> RESEARCH FACTORY
  -> OPPORTUNITIES
  -> SCAN
  -> VET
  -> SIZE
  -> RISK
  -> FILLS
  -> BOOK
  -> LEARNING
  -> SEARCH / REPLACEMENT
```

The important project change is therefore not:

> “we abandoned the robot and started trading weather.”

It is:

> “we stopped treating infrastructure progress as evidence of economic progress.”

The first engineering phase increasingly proved that Quant could preserve state, route evidence, size, risk, simulate fills, book outcomes and learn.

It did **not** prove that Quant already possessed a real market edge worth sending through that machinery.

That distinction is now the central project discipline.

---

## 2. What the robot already proved

Reference:

- North Star: `QUANT_NORTH_STAR.md`
- First vertical shadow-loop handoff:
  `builder/post-p0-first-vertical-shadow-loop-2026-09-21@5c8b5b71ef627ac0ec0faa509edc40b7d9d0c4df`

The first vertical Builder completed a substantial reusable path.

Recorded proof includes:

- scientific/economic boundary wiring;
- SIZE / RISK / FILLS / BOOK;
- persistent Ledger authority;
- durable Learning;
- replay / restart idempotence;
- one synthetic positive path through the real downstream stack;
- one common bankroll / Book concept rather than “fresh capital per experiment”;
- 478/478 tests green in the final handoff;
- no live capital authorization.

The important line in that handoff is:

```text
REAL_DATA_POSITIVE_PATH_AVAILABLE = FALSE
```

The synthetic positive fixture proved **plumbing**, not **market edge**.

That is the point at which more generic execution engineering became lower economic priority than answering:

> what real, current, accessible economic object should Quant actually trade?

Two integration limitations were also left explicitly deferred:

1. the Control Plane does not yet automatically invoke the economic-admission bridge before a Desk session;
2. the legacy inline Desk entry path is not fully spliced through the newer economic-size / durable-Learning path.

Therefore the chassis is substantial but not yet a zero-effort strategy plug-in platform.

---

## 3. Why the project pivoted toward strategies

The risk became obvious:

```text
excellent infrastructure
+ no demonstrated edge
= technically sophisticated zero-value activity
```

The North Star says wealth growth is terminal; code elegance, number of agents, number of trades and architecture depth are not.

So the research question was widened from:

> “can we finish the original Form-4 vertical?”

to:

> “where is there recent, verifiable, public evidence that an economically accessible mechanism actually transfers money to participants like the ones Quant could become?”

The resulting search policy became:

```text
RECEIPT
-> MECHANISM
-> ACCOUNTING CHECK
-> SURVIVORSHIP CHECK
-> SPEED / CAPITAL / ACCESS CHECK
-> REPRODUCIBLE RULE
-> PROSPECTIVE FALSIFICATION
-> SHADOW INTEGRATION
-> ONLY LATER: REAL CAPITAL QUESTION
```

This is not abandoning the robot.

It is filling the Research Factory with candidates worthy of the downstream robot.

---

## 4. What “receipt-first” means

A candidate is no longer interesting merely because:

- a backtest looks attractive;
- a chart looks clean;
- one public trader claims a profit;
- an aggregate reward pool is large;
- a strategy is theoretically arbitrage.

The new evidence hierarchy prefers:

1. realized public receipts;
2. a known economic payer / mechanism;
3. recent evidence;
4. losing participants visible, not only winners;
5. accounting semantics checked;
6. speed compatible with ordinary automation;
7. capital compatible with small size;
8. public reproducible inputs;
9. an experiment that can be frozen before outcomes.

This discipline has already killed or downgraded several attractive-looking ideas.

That is a feature.

---

## 5. Research wave — what we actually found

### 5.1 Weather: strong receipt evidence, reproducibility still unproven

Source:

- Agent 1 branch: `claude/dazzling-dirac-foklrv@4682fbbf335257f931209b433e0f10ea7b4f3b14`

Three weather-associated public wallets had 12-month whole-wallet `user-pnl` of approximately:

- +$87k
- +$96k
- +$93k

For the period after the 2026 weather-fee rollout, the same three were approximately:

- +$38k
- +$41k
- +$93k

The realized weather-attributed closed-position evidence was approximately:

- +$56k
- +$49k
- +$16k

with truncation caveats on two wallets.

This was not treated as “proof of our weather strategy.”

The same Agent 1 search found:

- 380 losers among the top 1,050 weather wallets by volume = **36% losers**;
- in a systematic 20-wallet sample, 17 were active and 4 lost money;
- median sampled weather P&L ≈ **+$264**;
- upper quartile roughly **$4k–$12k**.

The search also found decay risk:

- previously public weather stars such as gopfan2 / aenews2 / ColdMath showed very little recent profit compared with their historic totals.

### Why this was encouraging

Not because “weather is proven.”

It was encouraging because all of the following existed at once:

- recent post-fee receipts;
- repeated daily markets;
- public forecast inputs;
- low nominal capital requirement;
- a mechanism that does not obviously require sub-millisecond latency;
- enough events to support a prospective test.

That combination was stronger than most other candidates.

---

### 5.2 Weather feasibility: the market looks testable operationally

Source:

- frozen Weather V1:
  `claude/intelligent-gates-msidml@726070a199957a6fc05515ebb3027e945028fddc`
- Astra independent feasibility review:
  `claude/dreamy-franklin-1vki4t@e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250`

Astra deliberately used pre-outcome information only.

Measured cross-section:

- 80 temperature events examined;
- 60 °C events eligible under the frozen E4 geometry;
- 38/60 = **63%** triggered the frozen `h = 0.10` rule at b=0;
- **38/38** triggers had at least a realistic 5-share fill;
- **26/38 = 68%** filled the full $50 reference stake;
- **29/38 = 76%** had at least $25 depth inside the execution cap.

Astra estimated outcome-blind throughput scenarios around:

- pessimistic: **13 fills/day**
- conservative: **27 fills/day**
- central: **42 fills/day**

Implied time to 1,000 fills:

- ~77 days pessimistic
- ~37 days conservative
- ~24 days central

This produced an important result:

```text
HURDLE_SAMPLE_INCOMPATIBILITY = FALSE
```

The frozen `h = 0.10` rule did **not** fail because it produced too few opportunities.

### What blocked Weather V1

Astra instead found:

```text
EXPERIMENT_FEASIBILITY = BLOCKED_POWER_BELOW_DECLARED_MEUE
```

The protocol declared an economically meaningful effect of 0.02 per dollar committed, but the experiment could not reliably detect such a small effect inside its horizon.

Astra estimated realistic minimum detectable effects around:

- **0.06–0.10** per dollar under the lower-variance executable mix;
- **~0.15–0.25** if very-low-price high-variance legs remain material.

Other defects were procedural/statistical:

- incomplete terminal-state partition;
- incorrect use of order-book “last change” timestamp as observation timestamp;
- burn-in too short to possess 30 prior resolved dates;
- US 2°F buckets accidentally excluded by single-degree geometry;
- insufficient date × station dependence treatment.

### Why this is still encouraging

The independent reviewer did **not** conclude:

> “there is no weather opportunity.”

It concluded:

> “the experiment, as written, cannot answer the economic question it claims to answer.”

That is a much better failure to discover **before t0** than after months of forward data.

Operationally:

- events exist;
- triggers exist;
- books are fillable;
- the sample can accumulate.

The immediate problem is experimental architecture.

That is repairable outcome-blind.

No strategy claim is upgraded by this fact, but it means the candidate has not died for lack of opportunity flow.

---

## 6. Slow public information outside Weather

Source:

- Agent 4:
  `claude/magical-ramanujan-wsktyr@501093d1f6760201a5d81e638e74aa16ff75c3a8`

Agent 4 examined 12 preliminary mechanisms and kept 5 cards.

The most interesting current non-weather candidate is **box office**.

### Box-office receipts

Three currently relevant wallets showed:

- The-Joker: whole-wallet 12m `user-pnl` **+$158,771**; box-office closed-realized attribution **+$60,790**
- fanat12: `user-pnl` **+$36,042**; box-office attribution **+$30,492**
- denzeldumfries: `user-pnl` **+$42,264**; box-office attribution **+$28,019** since June 2026

A fourth historical wallet:

- Big.Chungus: `user-pnl` **+$269,106**; box-office attribution **+$96,774**, but box activity faded after March 2026.

Approximate family realized / family bought ratios measured for the four were:

- 5.3%
- 3.7%
- 12.4%
- 5.3%

Recent monthly box-office P&L for the active wallets was roughly **+$0.5k to +$13k/month**, depending on wallet/month.

### Activity-selected survivorship sample

Agent 4 did not stop at leaderboard winners.

For three September 2026 box-office events:

- 509 participants existed;
- the 70 most active were sampled by activity, not profit;
- **24/70 = 34%** had negative whole-wallet 12-month `user-pnl`;
- median whole-wallet 12-month P&L ≈ **+$11.5k**;
- family-corrected box-office median ≈ **+$1.4k**.

This still does not prove a reproducible rule, but it materially weakens the “only cherry-picked winner screenshots” interpretation.

### Why box office is interesting

The public information arrives slowly:

- Thursday previews;
- Friday actuals;
- Saturday / Sunday estimates;
- final reported grosses.

The Agent 4 evidence found winning brackets trading around **0.15–0.39** across Saturday/Sunday and converging later.

That suggests — but does not prove — that some public information may remain monetizable for hours rather than milliseconds.

The capacity is also naturally small:

- winning-bracket volume roughly **$25k–$30k per film-week** in the examples;
- likely only a few thousand dollars per event for a newcomer.

That is exactly the type of capacity that can be economically relevant to Quant while remaining irrelevant to large funds.

Current status:

```text
SPI-1 BOX-OFFICE = PROBABLE RECEIPT CANDIDATE
REPRODUCIBILITY = NOT PROVEN
```

Cheapest falsification remains a timestamped replay across ~26 weeks, followed by prospective testing if it survives.

---

## 7. Post-determination / resolution-lag economics

Agent 4 also found a recurring class:

> buy a side after the public underlying fact is effectively determined but before platform resolution.

Measured selected-wallet aggregates for entries at >= 0.90 included approximately:

- tweet family: **+1.7%** on ~$9.7M bought
- box office: **+3.5%** on ~$1.14M
- music: **+4.2%** on ~$124k
- AI: **−16.5%** on ~$335k

The negative AI result matters.

It shows that “buy near-certain outcomes” is not automatically an edge.

A small cleaner wallet example had `user-pnl` around **+$8,578** since July 2026 while often buying NO at ~0.84–0.90 on already-unreachable tweet buckets.

Main hidden risk:

- public “determination” can later be revised;
- source / resolution disputes can erase many small wins at once.

So this is a mechanism family requiring resolution-tail falsification, not a free bond.

---

## 8. Structural / fragmentation research corrected an important false positive

Source:

- Agent 5:
  `claude/hopeful-hamilton-81rab1@85483fb9f85c6beea36e0af969e3f0a3e939e07f`

Earlier literature appeared to report approximately **$39.59M** of Polymarket arbitrage profit.

A stricter 2026 paper measured roughly **$291k** for mechanism-linked realization over the comparable window.

Agent 5 reconciled the contradiction instead of averaging the numbers.

The large estimate was found to count favourable gaps under a broader accounting construction, while the strict estimate required actual linked realization.

Independent account checks reinforced the issue.

For one top account (#5):

- independent complete-lifetime cash result ≈ **+$122k**
- paper-attributed “arbitrage” ≈ **+$750k**

For another NegRisk converter (#8), the now-complete in-window reconstruction covers 2024-10-20 -> 2025-04-01 and 532,608 unique actions:

- ~$10.55M buys;
- ~$10.23M conversion collateral;
- ~$0.34M sales;
- net cash approximately **+$17,353**;
- paper-attributed "arbitrage" approximately **+$468,392**.

That is roughly a **27x gap** between independently reconstructed cash and the paper-attributed figure for this account/window.

Together with account #5 (+$122k complete-lifetime cash vs ~$750k attributed), this materially strengthens the conclusion that the large $39.59M estimate should not be treated as directly cashable realized profit.

### Why this matters

This is encouraging for the **research process**, even though it downgrades a candidate.

Quant is successfully removing fake economic signal before implementation.

That is exactly what the Research Factory must do.

---

## 9. Structural candidate: settlement liquidity near 0.999

Agent 5 found a small but currently live mechanism:

> buy an already-decided claim very near $1 before formal settlement, effectively providing impatient holders with immediate liquidity.

First recent slice:

- 300 recently closed markets;
- **5,692** near-certain BUY fills >= 0.995 in the prior 24h;
- about **$1.17M** notional;
- net ≈ **+$1,680.51**
- approximately **+0.14%** on notional;
- 1,155 distinct buyers;
- one losing fill in that first slice.

A second independent 300-market sample gave approximately:

- **+$1,564**
- on **~$1.07M**
- again around **0.14–0.15%**.

Crypto “Up or Down” markets looked latency-driven and were excluded from the slow structural interpretation.

### Why this is encouraging

The edge is tiny in percentage terms but:

- observable now;
- repeated;
- not obviously dependent on directional forecasting;
- naturally capacity-limited;
- potentially compatible with small capital.

Agent 5's own final economic assessment remains modest:

```text
VALID_SMALL_PLAYER_CANDIDATES_FOUND
economically marginal: <= ~EUR 90/month at EUR 5k
```

This is not a reason to deploy.

It is a reason to run the proposed 30-day falsification including disputed/reversed outcomes and realistic newcomer queue priority.

---

## 10. Small-player rewards: the key empirical test is now properly framed

Source:

- Agent 6:
  `claude/epic-cannon-1sy39m@cf9db0b8aeeef120155e2735b0e88b078447cea4`

The earlier maker-reward observation was large but incomplete.

Agent 1 had measured roughly:

- **$129,514/day** in Polymarket liquidity rewards;
- **16,179** rewarded markets in one snapshot.

But gross subsidy is meaningless if participants lose more through trading.

Agent 6 therefore built a pre-declared participant sample.

Two 90-day cohorts are now frozen:

- Cohort A: 2026-04-15
- Cohort B: 2026-07-01

Four reward tiers:

- T1 < $1 D0 reward
- T2 $1–10
- T3 $10–100
- T4 >= $100

Sampling:

- 40 wallets per tier;
- 4 tiers;
- 2 cohorts;
- **320 wallets total**;
- deterministic seed **20260929**;
- selection based on reward receipt, not P&L.

Completion:

- Cohort A: 160/160 collected, 159 usable due to one missing P&L history;
- Cohort B: 160/160 collected, no sampling errors.

Agent 6 verified an important accounting identity:

```text
NET = delta user-pnl + REWARDS + MAKER_REBATES
```

because the `user-pnl` series excludes those external payments.

### Reward / rebate program evolution

Measured on-chain daily snapshots:

2026-04-15:
- 4,180 reward recipients
- ~$126k rewards
- 7,125 rebate recipients
- ~$1.036M rebates

2026-07-01:
- 3,259 reward recipients
- ~$137k rewards
- 7,522 rebate recipients
- ~$1.644M rebates

2026-09-29:
- ~2,427 reward recipients across main + secondary flows
- ~$105.7k rewards
- 4,396 rebate recipients
- ~$124k rebates

The apparent rebate pool therefore fell roughly **13x** from July 1 to September 29.

That is currently an observation, not yet a causal conclusion.

### Why Agent 6 is important

This is one of the strongest methodological advances in the search.

For the first time, the question is not:

> “Does Polymarket distribute lots of money?”

It is:

> “Among participants selected independently of profit, what fraction actually ends 90 days net positive after trading P&L + rewards + rebates?”

That directly attacks adverse selection and survivorship.

At this checkpoint, the sample is complete but the final outcome analysis has **not yet been pushed**.

Therefore no small-player-rent conclusion is recorded here.

---

## 11. Other measured evidence that the economic search space is not empty

Source:

- Agent 2:
  `claude/gallant-cerf-e0rpao@94381734a22df464331c7654d70371faa48748c3`

### Kalshi maker/taker study

Across 46,282 resolved YES contracts through April 2025:

- makers: average return **−9.64%**
- takers: **−31.46%**
- makers on contracts >= 50c: about **+2.6%**
- an independent extension/reproduction reported about **+2.40% gross** in the >=50c maker subset after later maker-fee changes.

This is not directly actionable for Quant because of access constraints and incomplete account-level economics.

But it supports the broader hypothesis that some market-design rents accrue to liquidity provision rather than taking.

### Metaculus

Verified 2025 prize pools:

- Q1 2025: ~$30k
- Q2 2025: ~$30k
- later seasons announced at ~$50k

Top prizes were around ~$7.5k per quarter in Q1/Q2 2025.

Agent 6 later found that in Spring 2026:

- 173 bots;
- 37 of 133 owners paid = **28%**;
- median prize across entrants = **$0**.

This is useful because it prevents aggregate prize pools from being mistaken for typical small-player profit.

---

## 12. Strong negative evidence — equally important progress

The project has not only accumulated “promising” candidates.

It has killed or strongly downgraded many.

Examples:

### Hyperliquid user vaults / copy trading

Agent 1 measured:

- 8,029 user vaults with non-zero P&L;
- gains +$62.2M;
- losses −$123.5M;
- net **−$61.3M**;
- **73.2% losers**.

This reinforced the decision to reject copy-trading as a general path.

### Hyperliquid small market making

Agent 1 identified 198 large-volume likely maker accounts.

- aggregate all-time P&L ≈ +$295.5M;
- **47.5%** were losers all-time;
- among monthly active subset, **56.5%** lost in the month.

Established margins were roughly **0.18–1.93 bp per dollar** for the largest examples, while a small tier-0 maker pays around **1.5 bp** maker fees.

Therefore what works for giant market makers does not transfer cleanly to a small participant.

### Tweet-count accounting illusion

Agent 4 found a wallet showing about:

- +$216,687 “realized” in closed tweet positions

but after including 979 unredeemed losing buckets:

- whole-wallet 12m `user-pnl` ≈ **−$28,932**.

This is precisely why receipt semantics now require dead-position and `user-pnl` checks.

### Passive Uniswap LP

The measured literature reviewed by Agent 2 points to aggregate LP losses after adverse-selection/LVR in the 2025–2026 setting.

The profitable counterparty is the fast arbitrage side, which violates our speed constraint.

### Why the negatives are encouraging

They show the project is **not** optimistically promoting every idea.

A healthy research factory should produce many deaths.

If every research agent returned a “strategy,” the process would be suspect.

---

## 13. What is actually encouraging at the portfolio-of-hypotheses level

No individual candidate is yet authorized for real capital.

But the project-level evidence has improved in several ways.

### 13.1 We are no longer searching in a vacuum

We now have multiple independent mechanism classes with recent receipts:

- public weather information;
- box-office slow information;
- music/count-style slow information;
- post-determination / resolution lag;
- settlement-liquidity carry;
- explicit venue rewards/rebates;
- prediction/research prizes.

That reduces dependence on one original hypothesis.

### 13.2 Some opportunities are naturally small

Several candidates have capacity that is too small to matter to institutions but meaningful to Quant:

- a few thousand dollars per box-office event;
- hundreds to low thousands in niche music/count markets;
- ~0.1% settlement carry on limited flow;
- explicit small maker incentives.

This is aligned with the project's small-capital advantage hypothesis.

### 13.3 Several do not require HFT

The strongest surviving slow-public-information candidates operate on:

- hours;
- days;
- repeated public releases;

rather than milliseconds.

That matches Quant's intended automation advantage better than traditional market making or MEV.

### 13.4 We are measuring losers now

The research moved from winner anecdotes to:

- activity-selected samples;
- complete dead-loss checks;
- 320-wallet pre-declared cohorts;
- independent cash reconstructions.

This is the biggest improvement in evidence quality.

### 13.5 The Weather rail survived the operational-feasibility question

Astra found enough events and fillable books.

The failure is currently power/design coherence, not “there are no opportunities.”

That preserves Weather as a candidate while preventing premature forward testing.

### 13.6 The existing robot becomes more valuable if several candidates survive

Quant was explicitly designed for:

```text
multiple strategies
+ one persistent bankroll
+ common sizing
+ portfolio risk
+ shared execution
+ shared Book
+ learning
+ retirement / replacement
```

A portfolio of several low-capacity edges is more compatible with that architecture than one giant permanent strategy.

---

## 14. Why none of this is yet “we have a winning strategy”

The evidence ladder must remain explicit:

```text
RECEIPT EXISTS
    !=
MECHANISM IDENTIFIED
    !=
REPRODUCIBLE RULE
    !=
PROSPECTIVE EDGE
    !=
SHADOW-PROVEN ECONOMICS
    !=
REAL-CAPITAL AUTHORIZATION
```

Current strongest candidates mostly sit between the first three stages.

Weather has progressed furthest toward a prospective protocol, but Weather V1 is blocked pending experimental redesign and independent re-audit.

Agent 6 has the best current cohort design for maker rewards, but its outcome analysis is still pending.

Box office has unusually clean recent receipts and a plausible slow information path, but the exact rule has not been validated prospectively.

Settlement liquidity has direct recent transaction economics but needs dispute-tail and newcomer-fill tests.

Therefore:

```text
VALIDATED_DEPLOYABLE_STRATEGY = NONE YET
REAL_CAPITAL_AUTHORIZED = FALSE
```

---

## 15. How validated strategies reconnect to the existing robot

The correct target architecture is:

```text
WEATHER -----------\
BOX OFFICE ---------\
SETTLEMENT ----------> StrategyEvidence / Opportunity
FORM-4 -------------/             |
OTHER --------------/              v
                               COMMON QUANT CORE
                                     |
                                    VET
                                     |
                                    SIZE
                                     |
                                    RISK
                                     |
                                   FILLS
                                     |
                                    BOOK
                                     |
                                  LEARNING
```

The strategy-specific module should answer:

> what opportunity exists, based on what evidence, with what uncertainty/capacity/lifecycle?

The shared robot should answer:

> should capital be allocated, how much, with what portfolio risk, how was it executed, what happened, and what should be learned?

### Reusable components

Subject to bounded integration review, the existing robot should retain:

- Control Plane / clock;
- scheduler / routing;
- PIT/provenance discipline;
- evidence identity and persistence;
- economic-admission concepts;
- SIZE;
- RISK;
- ExecutionModel abstraction;
- Book / ledger;
- persistent bankroll;
- durable Learning;
- restart/replay safety;
- observability / governance.

### Strategy-specific adapters still required

Weather would need:

- forecast capture;
- market book capture;
- station / bucket / settlement semantics;
- Weather evidence artifact;
- Polymarket venue adapter.

Box office would need:

- public release-source timeline capture;
- bracket mapping;
- resolution semantics;
- evidence artifact.

Settlement liquidity would need:

- resolution-state detector;
- queue/fill model;
- dispute-tail accounting.

These should feed the same downstream Quant system rather than becoming separate standalone bots.

---

## 16. Current decision tree

### WEATHER rail

```text
Weather V1 Architect
    -> Astra feasibility audit
    -> BLOCKED_POWER_BELOW_DECLARED_MEUE
    -> Fable scientific design challenge
    -> Opus Architect V2 convergence
    -> Astra independent V2 re-audit
    -> if PASS: Sonnet Builder
    -> shadow forward experiment
```

No Builder before V2 passes independent re-audit.

No t0 before the revised protocol is frozen.

### SMALL-PLAYER-RENTS rail

```text
320-wallet frozen sample
    -> analyze A/B by tier
    -> trading vs rewards vs rebates decomposition
    -> persistence / concentration
    -> adversarial self-audit
    -> final status
```

This result may either promote or kill maker rewards as a candidate.

### BOX-OFFICE rail

Next cheapest falsification:

- last ~26 weeks;
- exact public-release timestamps;
- contemporaneous market prices;
- bracket implied by each public release;
- fees and revisions included;
- no tuning on eventual winners.

If historical replay survives, freeze a prospective rule before forward testing.

### SETTLEMENT-LIQUIDITY rail

Next cheapest falsification:

- 30 days of closed markets;
- all buys >= 0.998;
- include disputed/reversed outcomes;
- exclude latency-like crypto up/down family;
- reconstruct newcomer 0.999 queue/fill share;
- reject if net <= 0 or newcomer fill share < 5%.

---

## 17. What would count as genuine project progress from here

The next milestone is **not**:

- another 500 tests;
- another execution subsystem;
- another generic agent;
- another strategy brainstorm.

The next meaningful milestones are:

1. one candidate obtains a coherent frozen prospective experiment;
2. independent audit says that experiment can answer its stated question;
3. forward/shadow evidence is collected without tuning;
4. the candidate survives costs, dependence, concentration and decay;
5. it is adapted into the generic Quant chassis;
6. the shared robot measures its shadow contribution to persistent Book wealth;
7. only then is a separate real-capital gate considered.

---

## 18. Project interpretation at this checkpoint

The project is in a better position than when it had “a robot but no strategy” for three reasons.

### First

The robot was not discarded.

Its reusable downstream structure exists and has already been exercised in shadow/synthetic integration.

### Second

The economic search is now empirical.

The project has observed real money transfer in several candidate mechanisms and real losses in several rejected ones.

### Third

The research process is becoming capable of saying “no.”

Examples already killed or downgraded include:

- copy trading;
- small Hyperliquid market making;
- passive LP;
- naïve cross-venue arbitrage;
- inflated closed-position P&L;
- several high-price / late-favourite variants;
- Weather V1's underpowered experimental claim.

That is evidence that the process is filtering rather than merely storytelling.

The encouraging statement is therefore NOT:

> “Quant has found a profitable strategy.”

The defensible encouraging statement is:

> “Quant has moved from an infrastructure-heavy system with no demonstrated economic payload to a receipt-first research factory with several current, small-cap-compatible candidate mechanisms, increasingly strong anti-survivorship/accounting controls, and a reusable downstream robot ready to receive any strategy that survives prospective falsification.”

---

## 19. Source / branch inventory for this checkpoint

Architecture:

- `blue/master-v2-2026-09-20@09ba64b8bee1419076ec8a30f8d75a916932c2ba`
- `builder/post-p0-first-vertical-shadow-loop-2026-09-21@5c8b5b71ef627ac0ec0faa509edc40b7d9d0c4df`

Research:

- Agent 1 — registers / observed winners:
  `claude/dazzling-dirac-foklrv@4682fbbf335257f931209b433e0f10ea7b4f3b14`

- Agent 2 — measured realized profits:
  `claude/gallant-cerf-e0rpao@94381734a22df464331c7654d70371faa48748c3`

- Agent 3 — method + receipt practitioners:
  `claude/exciting-edison-w68tos@454d8522061c441659570dff4b3ec6b59cb526b5`

- Agent 4 — slow public information:
  `claude/magical-ramanujan-wsktyr@501093d1f6760201a5d81e638e74aa16ff75c3a8`

- Agent 5 — structural / fragmentation:
  `claude/hopeful-hamilton-81rab1@85483fb9f85c6beea36e0af969e3f0a3e939e07f`

- Agent 6 — small-player rents checkpoint:
  `claude/epic-cannon-1sy39m@cf9db0b8aeeef120155e2735b0e88b078447cea4`

Weather:

- Weather V1 frozen architect:
  `claude/intelligent-gates-msidml@726070a199957a6fc05515ebb3027e945028fddc`

- independent Astra feasibility review:
  `claude/dreamy-franklin-1vki4t@e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250`

---

## 20. Hard state at checkpoint

```text
QUANT_TERMINAL_OBJECTIVE          = NET_REAL_WEALTH_GROWTH
ROBOT_REUSABLE_CHASSIS            = TRUE_WITH_BOUNDED_INTEGRATION_GAPS

FORM4_ORIGINAL_REAL_DATA_PATH      = NOT_PROVEN

WEATHER_RECEIPT_EVIDENCE           = ENCOURAGING_BUT_SELECTION_BIASED
WEATHER_REPRODUCIBLE_EDGE          = NOT_PROVEN
WEATHER_EXPERIMENT_V1              = BLOCKED_POWER_BELOW_DECLARED_MEUE
WEATHER_t0                         = NOT_DECLARED

BOX_OFFICE_RECEIPTS                = PROBABLE_RECENT_CANDIDATE
BOX_OFFICE_REPRODUCIBLE_EDGE       = NOT_PROVEN

SETTLEMENT_LIQUIDITY               = SMALL_RECENT_STRUCTURAL_CANDIDATE
SETTLEMENT_LIQUIDITY_30D_TEST      = NOT_YET_RUN

SMALL_PLAYER_REWARD_SAMPLE         = 320_WALLETS_FROZEN_AND_COLLECTED
SMALL_PLAYER_NET_RESULT            = PENDING_ANALYSIS

VALIDATED_DEPLOYABLE_STRATEGY      = NONE
REAL_CAPITAL_AUTHORIZED            = FALSE

NEXT_ECONOMIC_GOAL =
FIRST_PROSPECTIVELY_FALSIFIED,
COST-AWARE,
SMALL-CAP-COMPATIBLE STRATEGY
THAT CAN BE ADAPTED INTO THE SHARED QUANT CORE
```