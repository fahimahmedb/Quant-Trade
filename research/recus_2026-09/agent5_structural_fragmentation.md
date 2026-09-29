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
| COUNTERFACTUAL OPPORTUNITIES INCLUDED? | Not in the 39.59 M$ itself, but the missing NegRisk legs are **priced counterfactually** from VWAPs carried forward up to 5,000 blocks, or set to 0 when a token stops trading (P) | No in the 1.12 M$. The market-state analysis counts episodes only, with no $ figure (P) |
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
| WHAT THE NUMBER ACTUALLY MEANS | **Gross profit from favorable complementary baskets**, one-sided (no netting), locked in at resolution, partly counterfactual (imputed legs). It covers market making (both sides filled across the spread), directional round-trips within the hour, partial directional bets, and a real NegRisk arbitrage share that cannot be isolated. **It is neither net cash nor arbitrage alone.** | **Mechanism-linked profit**, a lower bound on NegRisk arbitrage. Partly mark-to-model: about 81% of converter profit comes from partial conversions whose value depends on the imputed YES. The **hard core, cash realized immediately, is 205.5 k$ over about 2 years for the whole platform** |

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
   **Independent cash-flow reconstruction (V), which does not use Polymarket's P&L engine.**
   Account #8 (marksman): the full history (`data-api/activity`, 400,662 actions, every action of
   its life) runs from **20 Oct to 27 Dec 2024**, entirely inside Saguillo's window. It is a
   **pure NegRisk converter**: 231,342 NO buys, **0 YES buys**, 32,788 Adapter conversions across
   414 long-dated events (Champions League 2025, Premier League, NFL MVP, Heisman, Super Bowl…),
   and 134,257 sales of the returned YES.
   Cash: buys −8,752,103 $; collateral released by conversion +8,475,499 $; sales +290,038 $;
   redemptions +114 $; rewards +1,675 $. **Lifetime net cash = +15,223 $.** Open positions valued
   at 46,926 $ today (`/positions`). Maximum lifetime economic result: **≤ 62.1 k$**.
   Saguillo attributes **468,392 $** of "realized profit" to it. The realized cash is **31×
   smaller**, and even the maximum is **7.5× smaller**. It is a real arbitrageur, with 0.2–0.7%
   margin on 8.75 M$ of turnover, **and it earned 15 k$, not 468 k$.** Polymarket's two measures
   (user-pnl 10.8 k$, leaderboard 15.6 k$) agree with this reconstruction for this account.
3. **These are not specialised arbitrage bots.** #9 has 80,512 on-chain actions in the window
   (76,797 trades, 1,096 merges, 378 conversions, 115 liquidity-reward payments), versus the 200
   "transactions" Saguillo counts. #4 (aenews2) has 31,391 actions, including 289 conversions,
   and is a well-known weather trader today. Both are market makers or directional traders who
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
**liquidity subsidy is paid every 30 days at ~3.9 M$** (agent 1, R2). Arbitrage is therefore an order
of magnitude smaller than the subsidy.

| Question | Answer |
|---|---|
| Exact mechanism | (1) **NegRisk NO→collateral + YES conversion** through the Adapter: 97% of the mechanism-linked profit, mostly partial conversions and recycling of the returned YES. (2) Complete-basket settlement: 3%. Same-condition: not an executable channel. Combinatorial: 95 k$ gross, 13 election pairs, one-off. No market-creation bug is established. The 12 Dec 2025 cluster (381,748 $ in 7 min, 3 addresses) looks like a transfer between related wallets, not arbitrage |
| Does it require speed? | **Converter side (NO): yes.** In 2026 only 36 positive NO-side episodes appear in 5 weeks of sampling, with a median duration of **7.99 s** (n=5). **Settlement side (YES): no.** 2,098 positive YES-side episodes, 58.7% of observed episodes last longer than 50 min, but the realized amount is tiny (see §B S1) |
| Does it require large capital? | No per opportunity. Depth is shallow (Cheng et al.: 76.9% of combinatorial opportunities are capped at ~14.8 shares). Capital stays locked until resolution on the settlement side |
| Does it require special infrastructure? | Converter side: a multi-book WebSocket, near-atomic multi-leg execution, and conversion calls. In practice the 2026 converters are **market makers** (e.g. AJSV: 412 conversions and 6,138 merges in 3 days, V) that use conversion to recycle inventory |
| Observably alive in 2025–2026? | **Conversions yes (V):** 45 of the 525 top monthly accounts converted in the last 30 days. **Standalone conversion arbitrage profit in 2026: not established.** The median profit per conversion fell from ~1 $ (to Jul 2024) to ~0.20 $ (late 2024–2025) to **~0.08 $ (early 2026)** (Gebele Fig. 6). Taker fees since 2026 (rate × p(1−p) per leg, 0 for geopolitics) squeeze taker arbitrage further |
| Do small actors participate profitably? | Not demonstrated. Top 10 = ~75% of converter profit. Small actors appear in the long tail of 0.08 $ conversions, with no measured net P&L |

**POLYMARKET_ARBITRAGE_RECONCILIATION = RESOLVED** (the gap comes from definitions, not market data;
each cause is documented in the primary texts and confirmed on account-level samples). Limitation
stated: the ~100× factor left inside NegRisk is explained qualitatively but not split by cause.

