# AGENT 5 — STRUCTURAL / FRAGMENTATION RECEIPTS

Date: 2026-09-29. External research and forensic analysis only. No strategy code, no orders.
REAL_CAPITAL_AUTHORIZED = FALSE.
Branch: `claude/hopeful-hamilton-81rab1` (the branch the harness assigned to this session).
State file: `agent5_structural_etat.md`.

Evidence labels used below:
- **(P)**: read in the primary document by this agent (paper text or PDF).
- **(V)**: recomputed by this agent on 2026-09-29 from public APIs (Polymarket `data-api`,
  `user-pnl-api`, Hyperliquid `info`). Scripts were temporary and are not committed.
- **(S)**: secondary source, not verified.

---

## PART A — Forensic reconciliation: 39.59 M$ vs 291 k$

### A.1 Short answer

The two figures do not measure the same thing. Nothing needs to be averaged.

- **39.59 M$ (Saguillo et al., 2025)** sums, over each address and each window of about one hour
  (950 blocks), the favorable gap between $1 and the prices the address paid for complementary legs.
  Legs can come from different moments in that hour. For multi-outcome markets, legs the address
  never bought are filled in with estimated prices. Windows where the gap was unfavorable are not
  subtracted. The profit is the value "locked in if held to resolution". It is not cash the account
  actually made.
- **291,424 $ (Gebele et al., 2026, same resolution window)** counts only profit tied to a
  mechanism that actually realizes the payoff identity:
  - a NegRisk Adapter conversion whose inputs were bought no more than 5 blocks earlier;
  - or a complete basket over all active outcomes, built by one actor within 10 minutes.

  It drops the same-condition YES/NO channel entirely. Its authors show that channel is one unified
  order book, not two.

The ~136× gap therefore comes from different definitions, not different markets. The breakdown by
channel (§A.3) accounts for about 27% of the gap exactly. The rest sits inside the NegRisk channel
and has known causes, but it cannot be split among them without the authors' code.

### A.2 Methodological reconciliation table

| Field | Saguillo, Ghafouri, Kiffer, Suarez-Tangil | Gebele, Mutzel, Matthes |
|---|---|---|
| TITLE | *Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets* (P) | *Executable Arbitrage and Market Efficiency in Prediction Markets* (P) |
| AUTHORS | IMDEA Networks (3) + Oxford Internet Institute (1). Funded by Flashbots FRP-51 (P) | TU Munich (3) (P) |
| DATE | arXiv 2508.03474 v1, 5 Aug 2025. Peer-reviewed: AFT 2025, LIPIcs vol. 354, 27:1–27:24, published 6 Oct 2025. Key numbers are the same in both versions (P) | arXiv 2608.00666 v1, 1 Aug 2026. Preprint only. The authors' source leaves `%` unescaped, so text after each "%" is lost in both the HTML and the PDF (P) |
| SOURCE | https://arxiv.org/abs/2508.03474 · https://doi.org/10.4230/LIPIcs.AFT.2025.27 | https://arxiv.org/abs/2608.00666 |
| DATASET | Polygon events `OrderFilled`, `PositionSplit`, `PositionsMerge`, read via the Conditional Tokens contract `0x4D97…6045` (Alchemy public node). Blocks from 1 Jan 2024 to 1 Apr 2025. 86,620,143 bids. Metadata from the Polymarket API: 8,659 single-condition markets and 1,578 NegRisk markets (8,559 conditions), 17,218 conditions in total. **NegRisk Adapter `PositionsConverted` events are not among the parsed events** (P) | Three panels that do not overlap: (1) FPMM, 51 outcome sets, 235 markets, about 53k trades; (2) CLOB transactions, 32,702 events and 259 M trades for events listed through 31 Dec 2025, with fills from the Hugging Face dataset SII-WANGZJ/Polymarket_data, plus Adapter conversions and CTF split/merge from Goldsky and parsed logs, cross-checked on PolygonScan; (3) level-2 book archive (pmxt), 14 Apr–19 May 2026, used for market states only. Plus a 7-day WebSocket replay (8–15 May 2026, 308 M messages) (P) |
| BLOCK / TRADE PERIOD | Markets **resolved** between 1 Apr 2024 and 1 Apr 2025 (P) | Transactions from Jan 2024 to early 2026. The figure comparable to Saguillo is restricted to "the same 1 April 2024–1 April 2025 resolution window" (P) |
| MARKETS INCLUDED | All markets resolved in the window. For combinatorial arbitrage: only **13 manually validated pairs**, all US-election, ending 5 Nov 2024 (P) | Only mutually exclusive, exhaustive outcome sets: NegRisk events in CLOB, manually validated sets in FPMM (P) |
| MARKETS EXCLUDED | Bids below $2.00. Other pair dependencies ("weak dependencies" set aside). The LLM work cuts markets to their top 4 conditions plus "other", but only to detect dependencies (P) | **Same-condition YES/NO channel** (unified book, see WebSocket appendix). Non-NegRisk logical links. Partial baskets. One anomalous cluster on 12 Dec 2025 (outside the Saguillo window) (P) |
| TYPE OF ARBITRAGE | (a) Same-condition rebalancing: buy YES+NO below 1, or sell above 1. (b) NegRisk multi-condition rebalancing: buy/sell YES, buy/sell NO. (c) Combinatorial across 2 markets (P) | (a) Converter-enabled: NO→collateral+YES through the NegRisk Adapter before settlement. (b) Settlement-based: complete YES or NO basket held to resolution (P) |
| UNIT OF ANALYSIS | (address, condition or market, 950-block window). Profit = minimum quantity across legs × gap to $1 (or n−1) (P) | Conversion "bundle" (actor, event, NO input set, quantity), or complete basket (actor, event, quantity matched by FIFO) (P) |
| WALLET ATTRIBUTION METHOD | "For each user (single Polygon address)". No clustering (P) | "Address or Polymarket proxy wallet to which fills and token positions are attributed". No clustering, apart from the ad hoc exclusion of 3 addresses (P) |
| WHAT COUNTS AS AN ARBITRAGE | Any window where the address's legs imply a favorable sum. For NegRisk, missing low-probability legs are **estimated**: "we use the approach from Section 6 to estimate the price of the missing positions" (P) | An observed Adapter call whose full input coverage was bought ≤5 blocks (~10 s) earlier, or a complete basket over **all** active outcomes formed within ≤10 min (P) |
| WHAT COUNTS AS REALIZED | Executed fills, with profit "locked in" at resolution for the matched quantity. What happens to the positions afterwards is not tracked (P) | Converter: collateral released + actual sale proceeds of the returned YES over 150 blocks (~5 min) + **estimated** value of merged or residual positions, valued "at the estimated ask". Settlement: terminal profit, provided the basket is held to resolution (P) |
| EXECUTIONS OBSERVED? | Yes (on-chain fills) | Yes (fills + conversion calls) |
| COUNTERFACTUAL OPPORTUNITIES INCLUDED? | Not in the 39.59 M$ itself, but the missing NegRisk legs are **priced counterfactually** from VWAPs carried forward up to 5,000 blocks, or set to 0 when a token stops trading (P) | No in the 1.12 M$. The market-state analysis is kept separate: episodes (CLOB) plus a 5,185 $ benchmark (FPMM, maximum executable gap per event) (P) |
| CAPITAL ASSUMPTION | None. No return on capital (P) | None. Return on capital is used only as an anomaly diagnostic (P) |
| FEES | None: "Polymarket currently does not charge per trade executed" (P) | Market-state analysis: taker fees on every leg. Actor analysis: fees are not stated explicitly (period largely fee-free). The Adapter has a `feeBips` parameter (P) |
| GAS / CHAIN COSTS | Not counted | Not counted: "routed through Polymarket's relayer" (P) |
| INVENTORY | Surplus on any leg beyond the minimum quantity is **ignored**, so its losses are not counted (P) | Surplus excluded. Residual YES valued at the estimated ask (P) |
| UNWINDING | Not tracked | Returned YES tracked for 150 blocks |
| OPEN POSITIONS | Implicitly treated as held to resolution | Settlement baskets: conditional on being held. Converter residuals: marked-to-model |
| SETTLEMENT | Not checked per basket | Not checked per basket (conditional profit) |
| MULTI-OUTCOME NETTING | Partial basket + imputation: a basket missing legs can count | Requires all active outcomes (or complete conversion inputs) |
| CROSS-MARKET NETTING | 13 election pairs only | None |
| WALLET CLUSTERING | None | None |
| BOT / ROUTER CONTRACT HANDLING | Not described. The exchange contract is the counterparty in split- and merge-assisted matches (P) | Fills interpreted together with CTF operations in the same transaction (split- and merge-assisted matching) (P) |
| DOUBLE-COUNTING RISKS | (1) The paper never says whether a fill can enter both a same-condition basket and a multi-condition basket. (2) Overlap handling in the "rolling window" is not specified. (3) Naive aggregation of `OrderFilled` inflates turnover: Tsang & Yang (2026) find $958 M "naive" vs $391 M real for the Trump market in Oct 2024 (P, abstract). (4) The components add to **39,692,372.19 $**, but the stated total is **39,587,585.02 $**, a gap of 104,787 $ (V, arithmetic) | Quantities already attributed to conversions are excluded from settlement baskets (P) |
| TOTAL REPORTED PROFIT | **39,587,585.02 $** ("assuming an ε = $1 profit per trade"). Of which: same-condition 5,899,287 (buy) + 4,682,075 (sell) = 10.58 M$; NegRisk 11,092,286 (buy YES) + 612,189 (sell YES) + 4,264 (sell NO) + 17,307,114 (buy NO) = 29.02 M$; combinatorial 95,157 $ (P) | **1.118 M$** over the whole period: converter 1.086 M$, settlement 32,283 $ (FPMM 3,639 + CLOB 28,644). **291,424 $** on the Saguillo window. Excluding the 12 Dec 2025 cluster (381,748 $ in 7 min). "Full-set" NO→collateral conversions: **205,531 $** (18.9%) over the whole period; the rest comes from partial conversions and valuation of the returned YES (P) |
| CONCENTRATION | Top 10 = 8.18 M$ (20.7% of the total, V arithmetic). No. 1 = 2.01 M$ over 4,049 transactions (P) | Top 10 addresses = "75" (% lost in the source) of converter profit. FPMM: one actor = "76" (% lost) (P) |
| NUMBER OF ACTORS | Not reported | FPMM: 35 actors. CLOB: not reported |
| TOP ACTORS SHARE | 20.7% (top 10) | ~75% (top 10) |
| WHAT THE NUMBER ACTUALLY MEANS | **Gross profit from favorable complementary baskets**, one-sided (no netting), locked in at resolution, partly counterfactual (imputed legs). It covers market making (both sides filled across the spread), directional round-trips within the hour, partial directional bets, and a real NegRisk arbitrage share that cannot be isolated. **It is neither net cash nor arbitrage alone.** | **Mechanism-linked profit**, a lower bound on NegRisk arbitrage. Partly mark-to-model: about 81% of converter profit comes from partial conversions and the management of the returned YES (sales within 5 min, otherwise imputed value "at the estimated ask"). The **hard core, cash realized immediately, is 205.5 k$ over about 2 years for the whole platform** |

### A.3 Bridge from 39.59 M$ to 0.29 M$ (Saguillo window)

| Step | Amount | Explained by | Status |
|---|---:|---|---|
| Saguillo total (reported) | 39,587,585 $ | — | (P) |
| Gap: component sum − reported total | +104,787 $ | Probably the "ε = $1 per trade" filter; not documented | internal inconsistency, 0.26% |
| − same-condition channel (YES+NO of one condition) | −10,581,362 $ | Gebele excludes it: YES and NO are **two views of one order book**. Their WebSocket replay (8–15 May 2026, 308 M messages) finds the two books to be exact mirrors, apart from 20 isolated API inconsistencies. Cheng et al. (2026, 173 NBA games, 75 M snapshots) find only **7** executable same-market episodes, median 3.6 s | **explained** (definition) |
| − combinatorial (13 election pairs) | −95,157 $ | Outside Gebele's scope (NegRisk structure only) | **explained** (scope) |
| = NegRisk channel, Saguillo | 29,015,853 $ | — | — |
| vs NegRisk channel, Gebele (same window) | 291,424 $ | — | — |
| Remaining factor inside NegRisk | **≈100×** | Known causes, each documented in the text: (1) missing legs **imputed**, so partial baskets count; (2) 950-block window vs 5 blocks / 10 min, so accumulated positions and round-trips count; (3) **no netting** of unfavorable windows; (4) "buy NO" = 17.3 M$, which the paper links to accounts "making a lot of profit just by buying NO" (the systematic-NO strategy, which is directional); (5) Gebele also misses slow arbitrage (inputs accumulated > 5 blocks before, see §B S2) | **qualitatively explained, not split by cause** |

Reading: the same-condition and combinatorial channels account for about **27%** of the gap
exactly. The other ~73% is the definition gap inside NegRisk. Only rerunning Saguillo's code
could split that 73% between imputation, window length and missing netting, and the code is
not public.

### A.4 Account-level test on Saguillo's top 10 (V)

The trimmed prefixes in Table 1 of the paper were matched uniquely to full addresses in the public
leaderboard (`data-api.polymarket.com/v1/leaderboard`, ALL window, sorted by PNL then VOL):

| # | Address | Pseudonym | "Arbitrage" profit per Saguillo (Apr 2024–Apr 2025) | Cumulative lifetime P&L at 2025-04-01 (`user-pnl-api`) | Lifetime P&L at 2026-09-29 (leaderboard ALL) |
|---|---|---|---:|---:|---:|
| 1 | `0xd218e474776403a330142299f7796e8ba32eb5c9` | cigarettes | 2,009,632 | 304,926 | **−31,586** |
| 2 | `0x63d43bbb87f85af03b8f2f9e2fad7b54334fa2f1` | wokerjoesleeper | 1,273,059 | 154,844 | 593,406 |
| 3 | `0x9d84ce0306f8551e02efef1680475fc0f1dc1344` | ImJustKen | 1,092,616 | 2,141,677 | 2,264,692 |
| 4 | `0x44c1dfe43260c94ed4f1d00de2e1f80fb113ebc1` | aenews2 | 768,566 | 894,191 | 2,210,196 |
| 5 | `0x59ee6c6a56d7b00223f0c30f8002c4df762b684d` | undertaker | 749,796 | 286,483 | 116,997 |
| 6 | `0xd42f6a1634a3707e27cbae14ca966068e5d1047d` | Apsalar | 537,960 | 1,005,690 | 936,083 |
| 7 | `0x4a64afa45a44a01890c2161be88d2b44751d4430` | (address as pseudonym) | 476,767 | 238,796 | 239,951 |
| 8 | `0xb7d54bf1d0a362beb916d9cb58a04c41d67e0789` | marksman | 468,392 | 10,786 | 15,561 |
| 9 | `0x53d2d3c78597a78402d4db455a680da7ef560c3f` | abeautifulmind | 424,505 | 981,724 | 974,552 |
| 10 | `0x3cf3e8d5427aed066a7a5926980600f6c3cf87b3` | 50Whence | 383,570 | 1,137,517 | 317,102 |

Findings:

1. **For 5 of the 10 accounts (#1, #2, #5, #7, #8), one year of "arbitrage profit" is larger than
   the account's entire lifetime P&L, on both of Polymarket's P&L measures.** These 5 accounts
   total 4.98 M$ of "arbitrage profit", against 0.996 M$ of cumulative lifetime P&L at 2025-04-01
   (user-pnl) and 0.934 M$ lifetime at 2026-09-29 (leaderboard). Either these accounts lost
   4 M$ elsewhere, in which case the "arbitrage" was not a separable profit, or the figure is not
   net. **In both cases 39.59 M$ is not net cash earned by arbitrageurs.**
2. **Polymarket's own P&L measures disagree for these accounts.** #1: leaderboard −31.6 k$ vs
   user-pnl +806 k$ today. Neither is used as a reference. Both are shown only to bound the
   picture.
   **Independent cash-flow reconstruction (V), which does not use Polymarket's P&L engine**
   (raw `data-api/activity`, every action; cash = sells − buys + conversions + merges − splits +
   redemptions + rewards):

   | Account | Actions reconstructed | Composition | Net cash | Open positions | Saguillo "arbitrage" | Ratio |
   |---|---:|---|---:|---:|---:|---:|
   | **#5 undertaker**: **complete lifetime** (2024-02-17 → 2024-12-01; no action afterwards, checked) | 314,848 | splits 25.36 M$, conversions 21.70 M$ of collateral, buys 25.76 M$, sells 29.27 M$ | **+122,362 $** lifetime (in-window: +140,316 $) | 0 $ | **749,796 $** | **5.3–6.1×** |
   | **#8 marksman**: inception → 2024-12-27 (the first 400,662 actions; **the account is still active**, see note) | 400,662 | 231,342 NO buys, **0 YES buys**, 32,788 conversions over 414 long-dated events, 134,257 sales of the returned YES | **+15,223 $** on this sub-period | n/a for this sub-period | **468,392 $** | ≥ 30× on the sub-period |

   Notes:
   - #5: the reconstruction (+122.4 k$) agrees with the Polymarket leaderboard (+117.0 k$). The
     `user-pnl` series (+286.5 k$) overstates it.
   - #8: Polymarket's mark-to-market series gives **+10.8 k$ cumulative at 2025-04-01** (the end of
     the window, account created 2024-10-20), with a peak of +11.8 k$ in Jan 2025.

   Both accounts are **real** NegRisk arbitrageurs / converters with tens of millions of dollars of
   turnover. Their actual economic result is **~0.2–0.5% of turnover**, and **5 to 30 times smaller**
   than the "realized profit" Saguillo attributes to them.

3. **These are not specialised arbitrage bots.** #9 has 80,512 on-chain actions in the window
   (76,797 trades, 1,096 merges, 378 conversions, 115 liquidity-reward payments), versus the 200
   "transactions" Saguillo counts. #4 (aenews2) has 31,391 actions, including 289 conversions,
   and is a well-known weather/geopolitics trader today (agents 1 and 3). Both are market makers or directional traders who
   also use merge and conversion.
4. **Replicating the same-condition rule** (bids ≥ $2, 1-hour window, min quantity × (1 − sum of
   average prices)) on #9 and #4:

   | | #9 abeautifulmind | #4 aenews2 |
   |---|---:|---:|
   | Favorable "buy below $1" windows (what Saguillo counts) | 55 windows, **+7,639 $** | 52 windows, **+21,984 $** |
   | Unfavorable windows (sum > 1, not subtracted by Saguillo) | 35 windows, −26,241 $ | 19 windows, −4,510 $ |
   | Net | **−18,601 $** | +17,474 $ |
   | Median gap between YES and NO legs in favorable windows | **394 s** | **1,014 s** |
   | Share of favorable windows with both legs ≤ 10 s apart | 3.6% | 0.0% |

   Same-condition "arbitrages" are **round-trips across price moves**: the legs are bought minutes
   apart. Example: #4 on "Will Donald Trump win the 2024 US Presidential Election?" has legs
   2,071 s apart, sum 0.959. For #9, netting flips the sign.
5. **Anomaly noted in the paper:** @Tutaaa91 "purchased both YES/NO tokens for less than
   $0.02 each" for 58,983 $ in one trade. On a unified book, that is either a parsing artifact or
   two dislocated moments. It is not a simultaneous arbitrage.

### A.5 What the numbers actually mean

- **39.59 M$** = gross gain from favorable complementary trading. It is **an upper bound on
  "gains from complementary-leg trading", not an arbitrage profit and not net cash.** It should
  never again be cited as "realized arbitrage profit".
- **291 k$ (window) / 1.118 M$ (Jan 2024 → early 2026)** = profit tied to an identifiable
  realization path. This is **a lower bound** for NegRisk arbitrage: it misses slow arbitrage
  (inventory accumulated more than 5 blocks before conversion; see §B, active 2026 converters
  whose conversions all fall outside that rule), and it is partly marked-to-model.
  **The part cashed immediately with no residual risk (full-set NO→collateral) is 205,531 $ over
  ~2 years for the whole platform.**
- True net arbitrage profit is **not known exactly**. It lies between ~0.3 M$/year (mechanism-linked
  lower bound) and an unknown value well below 29 M$ (NegRisk, gross). It cannot be taken from either
  paper as is.

### A.6 Economic question after reconciliation

**Did real arbitrageurs receive economically meaningful profit?**
Yes, but it is small and concentrated. At platform scale, the mechanism-linked arbitrage is about
0.3 M$ per year in 2024–25, with ~75% going to 10 addresses. By comparison, the platform's
**liquidity subsidy** in 2026 is **~3.9 M$ every 30 days** (agent 1, R2), i.e. ~47 M$/year.
Different periods, but the order of magnitude is clear: structural arbitrage is **about two
orders of magnitude** smaller than what the platform pays to buy liquidity.

| Question | Answer |
|---|---|
| Exact mechanism | (1) **NegRisk NO→collateral + YES conversion** through the Adapter: 97% of the mechanism-linked profit, mostly partial conversions and recycling of the returned YES. (2) Complete-basket settlement: 3%. Same-condition: not an executable channel. Combinatorial: 95 k$ gross, 13 election pairs, one-off. No market-creation bug is established. The 12 Dec 2025 cluster (381,748 $ in 7 min, 3 addresses) looks like a transfer between related wallets, not arbitrage |
| Does it require speed? | **Converter side (NO): yes.** In 2026 only 36 positive NO-side episodes appear in 5 weeks of sampling, with a median duration of **7.99 s** (n=5). **Settlement side (YES): no.** 2,098 positive YES-side episodes, 58.7% of observed episodes last longer than 50 min, but the realized amount is tiny (see §B S1) |
| Does it require large capital? | No per opportunity. Depth is shallow (Cheng et al.: 76.9% of combinatorial opportunities are capped at ~14.8 shares). Capital stays locked until resolution on the settlement side |
| Does it require special infrastructure? | Converter side: a multi-book WebSocket, near-atomic multi-leg execution, and conversion calls. In practice the 2026 converters are **market makers** (e.g. AJSV: 412 conversions and 6,138 merges in 3 days, V) that use conversion to recycle inventory |
| Observably alive in 2025–2026? | **Conversions yes (V):** 45 of the 525 top monthly accounts converted in the last 30 days, including Saguillo's n°1 ("cigarettes": 163 conversions, 596 k$ of collateral released in 30 days). **Standalone conversion arbitrage profit in 2026: not established.** The median profit per conversion fell from ~1 $ (to Jul 2024) to ~0.20 $ (late 2024–2025) to **~0.08 $ (early 2026)** (Gebele Fig. 6). Taker fees since 2026 (rate × p(1−p) per leg, 0 for geopolitics) squeeze taker arbitrage further |
| Do small actors participate profitably? | Not demonstrated. Top 10 = ~75% of converter profit. Small actors appear in the long tail of 0.08 $ conversions, with no measured net P&L |

**POLYMARKET_ARBITRAGE_RECONCILIATION = RESOLVED** (the gap comes from definitions, not market data;
each cause is documented in the primary texts and confirmed on account-level samples). Limitation
stated: the ~100× factor left inside NegRisk is explained qualitatively but not split by cause.

---

## PART B — Structural white-space search

### B.1 Funnel (10 preliminary → 5 deep → 3 cards)

| # | Preliminary candidate | Receipt gate | Outcome |
|---|---|---|---|
| P1 | NegRisk YES basket < 1 held to resolution (the direction with no converter) | Realized: Gebele 2026, 4,014 YES baskets, Feb 2024–Oct 2025 | **Deep → card S1** |
| P2 | NegRisk NO→collateral conversion (arbitrage via the Adapter) | Realized: Gebele through early 2026; conversions still active Sep 2026 (V) | Deep → **rejected for small player** (speed race / market-making tool) → negative N2 |
| P3 | Post-event settlement liquidity (bid at 0.999 on already-decided claims) | Realized: Gebele & Matthes 2026, Table 6, actor-level through Dec 2025 + fills visible Sep 2026 (V) | **Deep → card S2** |
| P4 | Hyperliquid HLP (liquidation absorption + protocol market making) | Realized: vault P&L on-chain through 29 Sep 2026 (V) | **Deep → card S3** |
| P5 | Polymarket holding rewards on a complete YES+NO set | Payments are on-chain (`YIELD` type) | Deep → **rejected** (subsidy carry ≈ cash rate) → negative N5 |
| P6 | Monotonicity of date or strike ladders ("by March" ≤ "by June") | No realized reconstruction found | Rejected (no receipt). White space to measure |
| P7 | Cross-venue Polymarket ↔ Kalshi / other on-chain venues | Price gaps only (Gebele & Matthes 2601.01706) | Rejected (no realized profit; double access impossible) → N6 |
| P8 | Combinatorial NBA (moneyline/spread/total) | Opportunities only (Cheng et al. 2605.00864) | Rejected → N4 |
| P9 | Stake discount / redemption queue (stETH etc.) | No actor-level receipt found | Rejected (no receipt) |
| P10 | Kalshi "Collateral Return" on exclusive portfolios | Mechanism documented (May 2026), no receipt | Out of scope (US only) |

### B.2 Candidate cards

#### S1 — NegRisk complete YES basket below $1, held to resolution

| Field | Content |
|---|---|
| ID | A5-S1 |
| TITLE | Polymarket NegRisk: buy one YES of every active outcome when the sum of asks, after fees, is below $1, and redeem at resolution (the direction with **no converter**) |
| TYPE | intra-market / settlement (multi-outcome, same event) |
| MECHANISM | In a NegRisk event, exactly one YES pays $1. If Σ best YES asks + taker fees < 1, the complete basket locks in 1 − Σ. The Adapter converts only NO→YES, so this direction **can only be closed at settlement**. Capital is locked, so the fast arbitrageurs, who recycle capital, avoid it. That is why the gap persists (P, Gebele §3.3, I1–I3) |
| WHO PAYS | YES sellers on individual outcomes (exits from a candidate, market makers too wide on long shots) who do not reprice the rest of the event |
| WHY IT PERSISTS | No pre-settlement path (capital locked for days to months); shallow depth; all active outcomes must be held, placeholders included; tiny absolute gain → not worth it at scale |
| RECEIPT | Gebele, Mutzel, Matthes 2026 (arXiv 2608.00666), §5.3 and App. 0.G: **4,014 complete YES baskets** formed ≤10 min by one actor, **14,199 $**; plus 1,909 NO baskets, 14,445 $ (CLOB). Market states, 14 Apr–19 May 2026: **2,098 positive YES-side episodes after taker fees** vs 36 on the NO side (P) |
| PERIOD | Realized: Feb 2024 → Oct 2025. Opportunities: Apr–May 2026 |
| LAST PROFITABLE DATE | Oct 2025 (last month in Fig. 7). **Realized profit in 2026: not measured** |
| REALIZED PROFIT | 14,199 $ over ~20 months **for the whole platform** (≈3.5 $ per basket, ≈700 $/month all actors combined) |
| GROSS / NET | Locked in when the basket completes, conditional on resolution. Incomplete baskets (legging) are **excluded** from the measure → survivorship |
| FEES INCLUDED? | Realized: no (period largely fee-free). 2026 opportunities: yes (taker fees) |
| NUMBER OF ACTORS | Not reported for CLOB. FPMM: 35 actors |
| PROFIT CONCENTRATION | FPMM: one actor ≈ "76" (% lost in the source). CLOB: not reported |
| LOSER POPULATION | Unknown: failed attempts and incomplete baskets are not counted |
| SPEED REQUIREMENT | **SECONDS/MINUTES SUFFICIENT.** 58.7% of the 624 episodes in the 2026 persistence sample last longer than 50 min (that sample is smaller than the 2,134 positive episodes of Fig. 2; the source does not explain the gap). But episodes that close within the window have a median of **16 s** (n=253), so the long ones are probably the shallowest |
| CAPITAL REQUIREMENT | A few tens of $ per basket |
| CAPITAL LOCK | Until resolution (days to months) |
| INFRASTRUCTURE | Collector for all books of NegRisk events + `feeSchedule` per market; multi-leg taker execution. No colocation |
| PUBLIC DATA REQUIRED | CLOB books (REST/WebSocket), list of active outcomes (augmented NegRisk), Gamma metadata, fees |
| CAPACITY | Very low: the whole platform realized ~700 $/month in 2024–25 |
| ESTIMATED SMALL-SIZE €/MONTH | UNKNOWN for 2026. Upper bound from 2024–25: €500 ≈ 0–5 €, €1,000 ≈ 0–10 €, €5,000 ≈ 0–30 € (capped by total platform flow and capital lock-up) |
| TAIL RISK | **Augmented NegRisk**: outcomes added later or "Other" redefined → basket no longer complete. UMA mis-resolution. Ambiguous resolution (FIDE Blitz 2024 case, two "winners", Saguillo fn. 5). Capital blocked for months |
| VENUE ACCESS | Polymarket international. Owner declares access, to confirm with `GET polymarket.com/api/geoblock` (agent 1). France is on the official "close-only" list (agent 1) |
| ONE-DAY PUBLIC VERIFICATION POSSIBLE? | Yes for opportunities (24 h of books). No for realized 2026 (needs complete-basket reconstruction, a few days) |
| CHEAPEST FALSIFICATION TEST | 24 h of 1-minute snapshots of all active NegRisk events: count (event, minute) with Σ YES asks + fees < 1 − 0.5 ¢ and depth ≥ 20 baskets. If Σ(executable gap × depth) < 5 $/day → **reject** |
| CONFIDENCE | **PROBABLE** (mechanism and 2024–25 receipts verified in the text; realized 2026 not verified; economically negligible) |

#### S2 — Settlement liquidity: buying already-decided claims at 0.998–0.999

| Field | Content |
|---|---|
| ID | A5-S2 |
| TITLE | Post-event settlement liquidity on Polymarket: buy (resting bid) the winning claim of an already-decided event at 0.998–0.999, redeem at 1 after UMA resolution |
| TYPE | settlement |
| MECHANISM | Once the real event is decided, the claim is still not redeemable until UMA finalizes (2 h minimum if undisputed). Holders who want their cash immediately sell into bids at 0.999 because the **0.001 tick** allows no better price. The buyer earns 0.1–0.2% over a few hours (P, Gebele & Matthes, App. 9.3: "settlement-liquidity trade"). **Distinct from the rejected "favorites > 90¢"** (a bet before the event is decided): here the outcome is known, and the only risk left is settlement/resolution. The 0.995–0.998 fills taken before the final observation (weather) fall back into the rejected category and are **not** part of S2 |
| WHO PAYS | Holders of winning claims who want to recycle capital immediately (bots, active traders): they pay 0.1% to skip a few hours of settlement delay |
| WHY IT PERSISTS | Settlement latency (UMA) + **tick floor**: at the 0.999 level the discount cannot compress below 0.1%, so competition shifts to the queue, not the price. Capacity is too small for large players. The trade uses balance sheet |
| RECEIPT | (P) Gebele & Matthes 2026, arXiv 2605.31431, Table 6: top 10 identified liquidity providers, e.g. `0x751a…` **+23,616 $ over 34,994 trades** (median 0.04 $/trade, median hold 1.06 h); top-10 total ≈ **104 k$**. Median APY per trade 6.22%. Sample from inception to 31 Dec 2025, "latest 1,500 trades per market", **disputes excluded**. (V) Live slice today: 300 binary markets (volume ≥ 1 k$) closed 29/09/2026 between 15:07 and 16:39 UTC → **5,692 BUY fills at ≥ 0.995 in the 24 h before close, 1.17 M$ notional, net +1,680.51 $ (0.14%)**, **1 losing fill** (−9.99 $, CS2 match), **1,155 distinct buyers**, top buyer +143 $ on 139 k$. **Second independent slice** (300 other markets, later): ≈1.07 M$ notional, ≈+1,564 $. At ≥0.999 the return is **exactly the 0.1% tick floor** in every category. Median hold: esports 0.99 h, other 1.83 h, weather 9.3 h, **crypto "Up or Down" 0.04 h** (latency territory, excluded). At 0.995–0.998: 0.25–0.30% for holds of 8–11 h (residual risk before the final observation). 2 losing fills (esports) |
| PERIOD | Through Dec 2025 (P) + 29/09/2026 (V) |
| LAST PROFITABLE DATE | 2026-09-29 (V) |
| REALIZED PROFIT | Top 10 ≈ 104 k$ cumulative (P). 2026: two slices of 300 markets each → +1,680 $ and +1,564 $ (~0.14–0.15% of notional), all buyers combined (V) |
| GROSS / NET | Net of fees (makers pay 0; seller's taker fee ≈ rate × 0.999 × 0.001 ≈ 0.00005 $/share). **Mis-resolution losses: absent from the academic screen** (disputes excluded) → survivorship |
| FEES INCLUDED? | Yes (P&L computed from executed prices and final payout) |
| NUMBER OF ACTORS | 1,155 distinct buyers in 1.5 h of closes (V): **very fragmented** |
| PROFIT CONCENTRATION | Low in the V slice (top buyer 8.5% of profit). Top 10 academic: the n°1 ≈ 23% of the top-10 total |
| LOSER POPULATION | Sellers (by choice: they pay for liquidity). On the buyer side: rare losers when "certainty" flips (3 fills out of ~11,000 across the two slices) |
| SPEED REQUIREMENT | **SECONDS/MINUTES SUFFICIENT** for esports / other / weather (holds of 1–11 h), but with a **queue race** at 0.999 (price-time priority): being in the queue before the sellers arrive decides fills. **Crypto "Up or Down" markets excluded** (hold 2.4 min → LOW-LATENCY) |
| CAPITAL REQUIREMENT | Small (fills of a few to a few hundred shares) |
| CAPITAL LOCK | Hours: 1–2 h (Table 6; esports/other V), ~9–11 h (weather V); days if disputed |
| INFRASTRUCTURE | Watcher for event ends / resolution sources + resting bids across many markets; checks on the resolution rule. No colocation |
| PUBLIC DATA REQUIRED | Gamma (`endDate`, `closedTime`, `umaResolutionStatus`), books, `data-api/trades`, resolution sources |
| CAPACITY | Low per market; aggregate ~1.2 M$ of near-certain notional per 1.5 h of closes, shared among >1,000 buyers |
| ESTIMATED SMALL-SIZE €/MONTH | **UNKNOWN** (depends on fill share in the queue). Upper bound: capital × 0.1–0.14% × 2 cycles/day × utilization. At 10–30% utilization: €500 ≈ 3–9 €, €1,000 ≈ 6–18 €, €5,000 ≈ 30–90 €, **before** tail losses |
| TAIL RISK | A single flip or mis-resolution costs ~99.9% of the position, i.e. ~1,000 profitable trades. UMA vote against the facts or a disputed rule; revision of the resolution data (weather station, cf. agent 3 on Roissy); a "certain" state misjudged (3 losing fills across the two V slices) |
| VENUE ACCESS | Polymarket international (as S1) |
| ONE-DAY PUBLIC VERIFICATION POSSIBLE? | **Yes** (partly done: V slice) |
| CHEAPEST FALSIFICATION TEST | 30 days of closed markets: for each buyer at ≥ 0.998, net P&L **including** disputed or flipped markets; plus a shadow queue simulation (a bid posted at 0.999 at time t: what fill share given the queue ahead?). If net per buyer ≤ 0 over 30 days, or expected fill share for a new bid < 5% → **reject** |
| CONFIDENCE | **PROBABLE** (actor-level receipt through 2025 + live profitable fills in 2026; net of tail losses and fill share for a newcomer not verified) |

#### S3 — Hyperliquid HLP: liquidation absorption and protocol market making

| Field | Content |
|---|---|
| ID | A5-S3 |
| TITLE | Deposit USDC into HLP, the protocol vault that runs Hyperliquid's liquidations and market making |
| TYPE | structural (forced flow / backstop). **Delegated, not executed by Quant** |
| MECHANISM | HLP takes over liquidated positions and quotes the book with several market-making strategies. It also "supplies USDC in Earn" (lending, a cash-like return). Depositors share P&L pro rata. Leader commission 0% (V) |
| WHO PAYS | Leveraged traders who are forcibly liquidated, and takers |
| WHY IT PERSISTS | Protocol privilege (priority on liquidations); demand for leverage; liquidations are forced, not optional |
| RECEIPT | (V) `POST api.hyperliquid.xyz/info {"type":"vaultDetails","vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"}`: all-time PnL +138.4 M$. **12 months (17/09/2025 → 27/09/2026): +60.7 M$ on ~342 M$ average AV (≈17.7% simple).** **6 months (18/03 → 27/09/2026): −0.3 M$ (≈0%).** Last 30 days +0.60 M$. API APR 3.94%. TVL 403 M$ (Apr 2026) → 183 M$ (Sep 2026) |
| PERIOD | May 2023 → 29 Sep 2026 |
| LAST PROFITABLE DATE | 2026-09-29 (day +28.7 k$, V) |
| REALIZED PROFIT | +60.7 M$ over 12 months at vault level (marked-to-market, realized for depositors on withdrawal) |
| GROSS / NET | Net of trading fees; 0% commission |
| FEES INCLUDED? | Yes |
| NUMBER OF ACTORS | Pro-rata vault (many depositors) |
| PROFIT CONCENTRATION | Pro rata. **Concentrated in time**: 12-month return is ~all before March 2026 (liquidation episodes) |
| LOSER POPULATION | Liquidated traders |
| SPEED REQUIREMENT | **NO SPEED ADVANTAGE REQUIRED** (delegated) |
| CAPITAL REQUIREMENT | Small (no documented minimum) |
| CAPITAL LOCK | **4 days** after the latest deposit (official docs) |
| INFRASTRUCTURE | None (wallet + deposit) |
| PUBLIC DATA REQUIRED | `vaultDetails` (pnlHistory, accountValueHistory) |
| CAPACITY | Large (TVL 183 M$) |
| ESTIMATED SMALL-SIZE €/MONTH | Last 6 months' pace: ≈0 € at every size. 12-month pace: ≈7 € / 15 € / 74 € (for €500 / €1,000 / €5,000). Current APR (3.9%): ≈1.6 € / 3.3 € / 16 € |
| TAIL RISK | Manipulation of an illiquid asset that HLP ends up carrying (JELLY case, Mar 2025, S); liquidation cascade with losing inventory; discretionary validator intervention; bridge/smart-contract risk; unknown regulatory status in France |
| VENUE ACCESS | Hyperliquid: no KYC, US front-end blocked; France technically accessible, regulatory status unknown (agent 1) |
| ONE-DAY PUBLIC VERIFICATION POSSIBLE? | Yes (done here) |
| CHEAPEST FALSIFICATION TEST | Daily `pnlHistory` over 24 months → monthly return **in excess** of the USDC lending rate (Aave). If the median monthly excess ≤ 0 and > 70% of profit comes from ≤ 2 episodes → classify as "crash insurance", **not a repeatable edge** → reject |
| CONFIDENCE | **VERIFIED** for the receipt. For "structural excess return" at small size: **UNVERIFIED** (≈0 for 6 months; part of the return is plain lending) |

### B.3 NEGATIFS UTILES (6)

1. **Same-condition YES/NO "arbitrage" (10.58 M$ in Saguillo) — false realization accounting.**
   YES and NO are two views of one book (Gebele WebSocket appendix: exact mirrors apart from 20
   API inconsistencies in 7 days; Cheng et al.: 7 executable episodes in 173 NBA games, median
   3.6 s). The favorable "baskets" in our sample have legs **394–1,014 s apart** (median), and
   0–3.6% have legs ≤10 s apart. For #9, netting unfavorable windows turns +7.6 k$ into
   **−18.6 k$** (V). A scanner showing YES+NO < 1 is almost always a feed that is out of sync,
   not an opportunity.
2. **NegRisk NO→collateral conversion in taker mode — execution race + professional
   infrastructure.** In 2026: 36 positive NO-side episodes in 5 weeks of sampling, median duration
   **7.99 s** (n=5). Median profit per conversion ~0.08 $ in early 2026 (from ~1 $ in 2024). Top
   10 = ~75% of converter profit (P). Active converters in Sep 2026 are market makers recycling
   inventory (AJSV: 412 conversions and 6,138 merges in 3 days; none of the sampled conversions
   is a ≤60 s bundle, V). There is no room for a non-market-maker small player.
3. **"Realized profit of top arbitrageurs" — confusion between gross, one-sided "locked-in"
   profit and cash.** #5 undertaker, a converter and split/sell trader with a **complete**
   lifetime (Feb–Dec 2024), cashed **+122 k$** on ~25 M$ of buys, not the **750 k$** attributed
   to it. #8 marksman, a pure NegRisk converter, cashed **+15.2 k$** over its first 400,662 actions
   (8.75 M$ of NO bought), and Polymarket marks it at +10.8 k$ cumulative at the end of the window,
   not **468 k$**. Real margin: **~0.2–0.5% of turnover**. Across 5 of the top 10,
   4.98 M$ of "arbitrage" sits against ~1.0 M$ of lifetime P&L (V). Any 2024–25 "arbitrage bot"
   success story built on the 40 M$ figure rests on this bias.
4. **Combinatorial arbitrage (election pairs, NBA) — capacity.** 95 k$ gross over 13 pairs, all
   from the 2024 election (one-off). In the NBA, the "Middle" jackpot is **never realized** and
   76.9% of opportunities are capped at ~14.8 shares on average (Cheng et al., abstract). Real,
   but at "retail scale" in the literal sense: a few dollars.
5. **Holding rewards on a complete YES+NO set — carry disguised as structural.** Current rate
   **3.25%** (variable, at Polymarket's discretion), computed on YES and NO shares at the mid, in
   5 categories of long-dated markets (official help centre). Splitting 1 $ into YES+NO therefore
   earns ~3.25%/year of subsidy with no price risk. That is at or below the cash rate, carries
   platform risk, and the rate can be cut or capped at any time. No excess return.
6. **Cross-venue Polymarket ↔ Kalshi / other venues — false realization.** Gaps of 2–4% on
   equivalent events (Gebele & Matthes, arXiv 2601.01706, 10 venues, >100k events), but **no
   profit reconstructed**. Resolution rules are not fungible, and double access for one resident
   is impossible (Kalshi is US-only). Confirms agent 2 R6.

---

## Final self-audit

| Attack | Target | Result | Action |
|---|---|---|---|
| Gross taken for net | 39.59 M$ | Confirmed: one-sided, locked-in, imputed legs. #5 → complete lifetime cash 5.3× smaller; #8 → ≥30× on the reconstructed sub-period | Figure reclassified as "gross upper bound", never to be cited as realized profit |
| Gross taken for net | Gebele 1.118 M$ | Partly true: residual YES valued "at the estimated ask" (generous), settlement baskets conditional. Only 205.5 k$ (full set) is immediate cash | Presented as a lower bound **and** partly marked-to-model |
| Opportunity taken for execution | S1 | 2026 evidence = **market states** (fee-adjusted episodes), not realized trades. Realized stops in Oct 2025 | S1 stays **PROBABLE**, "realized 2026: not measured" stated explicitly |
| Circular wallet attribution | Top 10 Saguillo | Prefixes of 22 hex characters (88 bits) matched **one** proxy wallet each on the public leaderboard; negligible collision risk. The #5/#8 cash tests use the raw activity feed, not Saguillo's method and not Polymarket's P&L engine | No circularity. Remaining risk: one operator can run several wallets (no clustering on either side) |
| Double counting | Saguillo | Components 39,692,372 $ vs total 39,587,585 $ (gap 104,787 $); fill exclusivity across strategies not documented | Reported as an unresolved internal inconsistency (0.26%) |
| Open positions / truncation | #8, #5 | **Error found and fixed during the audit:** the #8 fetch hit a 400,000-action cap and stopped at 2024-12-27, but the account is still active (last action 29/09/2026). Its figure was first described as "lifetime" | #8 scoped back to the reconstructed sub-period. #5 checked complete (no action after 2024-12-01, 0 open positions) and used as the main example |
| Hidden speed | S1 | Episodes that close within the window: median **16 s**. The "> 50 min" episodes are probably the shallowest | Speed class kept at "SECONDS/MINUTES" with this caveat |
| Hidden speed | S2 | Price-time priority at 0.999: being **first in the queue** matters (a queue race, not a ms race) | Stated. Test: fill share for a new bid |
| Hidden capital | S1 | Capital locked until resolution (months) → negligible return on locked capital | Reflected in €/month |
| Survivorship | S2 | Gebele & Matthes' screen **excludes disputes**, so tail losses are absent from the P&L; Table 6 = top 10 only | Confidence capped at PROBABLE; falsification test includes losers |
| Survivorship | Saguillo top 10 | These are "winners" of a gross measure; their lifetime P&L is often below it | Used as proof of bias, not as edge evidence |
| 2024 assumed alive in 2026 | Arbitrage | Saguillo's 2024–25 results are **not** extrapolated. Converter 2026: activity observed, standalone profit not established | 2026 = "active as an MM tool, standalone profit unverified" |
| Misattributed secondary claims | "73% to bots < 100 ms", "2.7 s average duration" (cited by agent 3 as S and by blogs as coming from the IMDEA study) | **Absent from Saguillo's text**: no occurrence of "millisecond", "latency", "73%" or "2.7 s" in the arXiv, HTML or LIPIcs versions (V, grep) | Treated as (S) false, not reused |

---

## Synthesis

**Part A.** The "contradiction" 39.59 M$ vs 291 k$ is a definition gap. Saguillo measures gross,
one-sided, partly imputed gains from complementary trading. Gebele measures profit tied to a
realization mechanism. The raw account data (V) confirm it: #5, reconstructed over its **complete** lifetime,
**cashed 122 k$, not 750 k$**. #8, a pure converter, cashed 15 k$ over its first 400k
actions (Polymarket: +10.8 k$ at the end of the window), not 468 k$.
Structural arbitrage on Polymarket is real, but small (~0.3 M$/year at platform scale in
2024–25), concentrated (top 10 ≈ 75%), and in 2026 it has become an inventory tool for market
makers. The NO/converter side is a seconds-level race. The YES/settlement side is slow but
microscopic.

**Part B.** Three mechanisms pass the receipt, speed and capital gates. All three are
**economically marginal** at Quant's size:
- **S2 (settlement liquidity at the 0.001 tick)** is the only one that is **alive, realized and
  measurable in 2026** with small capital and no speed. It is structural, not predictive: the
  0.001 tick sets a floor on the discount. Unknowns: the fill share for a newcomer, and the net
  after disputes.
- **S1** (NegRisk YES basket) is realized but microscopic (~700 $/month for the whole platform
  in 2024–25).
- **S3** (HLP) has a verified receipt, but about 0% over 6 months. It is delegated insurance
  against liquidations, not an edge Quant runs itself.

No candidate justifies real capital. REAL_CAPITAL_AUTHORIZED stays FALSE.

**POLYMARKET_ARBITRAGE_RECONCILIATION = RESOLVED**

**STRUCTURAL_RECEIPT_SEARCH = VALID_SMALL_PLAYER_CANDIDATES_FOUND**
(qualifier: the 3 candidates pass the receipt, speed and capital gates, but the realistic value is
≤ ~90 €/month at €5,000 before tail losses. None is a large edge.)

## Final report (7 lines)

1. Branch: `claude/hopeful-hamilton-81rab1`
2. SHA: see `git log -1` on the branch (also recorded in `agent5_structural_etat.md`)
3. POLYMARKET_ARBITRAGE_RECONCILIATION = RESOLVED
4. 39.59 M$ is a gross, one-sided, partly imputed sum of favorable complementary baskets (per address, ~1 h windows, no netting); 291 k$ counts only profit tied to an observed NegRisk conversion or a complete basket formed within minutes. Different estimands: on raw on-chain cash, Saguillo's #5 made +122 k$ over its complete lifetime vs 750 k$ attributed.
5. STRUCTURAL_RECEIPT_SEARCH = VALID_SMALL_PLAYER_CANDIDATES_FOUND (marginal: ≤ ~90 €/month at €5k)
6. A5-S2 (settlement liquidity at 0.999), A5-S1 (NegRisk YES basket < 1), A5-S3 (HLP)
7. Cheapest next falsification: 30-day on-chain census of all ≥0.998 buys on closed Polymarket markets (excluding crypto "Up or Down"), net P&L per buyer **including** disputed or flipped markets, plus a shadow simulation of the fill share for a new 0.999 bid.
