# AGENT 6 — SMALL PLAYER RENTS — deliverable

Date: 2026-09-29 (UTC). Empirical public-data research only.
No orders, no accounts, no capital, no strategy code.
**REAL_CAPITAL_AUTHORIZED = FALSE.**
Branch: `claude/epic-cannon-1sy39m` (the branch assigned to this session).
State file: `agent6_small_player_rents_etat.md`. Data and scripts are in `agent6_data/` and `agent6_scripts/`.

## TERMINAL STATUS

**SMALL_PLAYER_RENTS = VERIFIED_NET_CANDIDATES_FOUND**

This status is narrow.

- **Polymarket liquidity rewards.** Net profit after trading P&L is verified only for the top reward tier: wallets earning at least $100/day of rewards on the frame day, about 5% of all recipients. Their median cash balance is about $12–14k, which is only a lower bound on capital. That is "small" next to an institution, but it is not a €100–€5,000 player.
  - For the small reward tiers the answer is **no**. Median net over 90 days is about $0 or negative, and rewards do not offset trading losses.
  - Across all reward recipients (weighted back to the full frame), only **44–49%** were net positive over 90 days.
- **Numerai Classic.** Staked models are net positive **in NMR** in every stake tier, including small stakes. The absolute amounts are tiny, and the result in USD is dominated by the NMR price.
- **No candidate is verified reachable by a new €100–€1,000 entrant.**

Nothing here authorizes deployment.

---

## 1. What was measured (methods, receipts)

| Program | Measurement | Sample / frame | Result type |
|---|---|---|---|
| Polymarket liquidity rewards and maker rebates | Frame: on-chain reward transfers. Outcome per wallet: net = Δ`user-pnl` + REWARD + MAKER_REBATE over 90 days | 320 wallets: 2 cohorts × 4 pre-declared tiers × 40. Seed 20260929 | **VERIFIED** (on-chain + public API) |
| Polymarket reward and rebate pools | Daily payout totals from Polygon logs of the known payers | 04-01 → 09-29 (some dates UNKNOWN, see §4) | VERIFIED |
| Numerai Classic and Signals | Census of every model staked at least once in 129 resolved rounds (public GraphQL `roundDetails`) | Classic 5,981 models; Signals 912 models | VERIFIED. Tiers recomputed by the lead from the worker's CSV |
| Metaculus AI Benchmark | Published winners tables and results posts; prize code in the Metaculus repository | Q4 2024 → Summer 2026 | Prizes paid: VERIFIED to Q2 2025. Net for an entrant: UNVERIFIED |
| Kalshi Liquidity Incentive Program | Public incentives endpoint and docs | 5,562 active programs | Budget VERIFIED. Participant net: not measurable |
| Hyperliquid small maker | Reused agent 1's verified result | — | Negative (agent 1, V) |

### Polymarket receipts (on-chain, Polygon)

**Liquidity-reward payers:**
- `0xc288480574783bd7615170660d71753378159c47` (USDC.e, April);
- `0x2c2795ea295d5eb51f9121b728ed2ea4e936a709` (pUSD, July–September), paid through multisend `0xd152f549…2150` at 00:00–00:05 UTC;
- secondary small payers `0xf7cd89be…9f64` and `0xdd8db71c…9e8b` (00:15 UTC).

**Maker-rebate payers:**
- `0x3a9418b2…e0f7` (USDC.e);
- `0xfdb1b8dc…5507` (pUSD), at 00:45–01:00 UTC.

pUSD is `0xc011a7e12a19f7b1f670d46f03b03f3342e82dfb` ("Polymarket USD", 6 decimals). Every payment is an ERC-20 transfer that anyone can re-read with `eth_getLogs`, so **rewards are proven distributed, not merely advertised.**

### Method validation

- **The P&L series excludes rewards and rebates.** `user-pnl-api` barely moves on days with rewards but no trades:
  - `0x4ddc9fa3055fc42411d95f4fb03267102c64c06f`: $28.37 and $34.96 of rewards, Δ −0.0004 and −0.0007;
  - `0xa0a6ca2c507761d3f5df9f6137113ed584370bb7`: $42.51 of rewards, Δ −2.28.
- **It matches independent accounting.** It agrees with the published result of b00k13 (`0x1c5575dc…84ce`): $4,961 against $4,973 claimed.
- **Rejected alternatives.** Rebuilding P&L from the activity feed misses some redemptions and merges (−$8.8k against a true value of about +$5k). Summing closed-positions realized P&L overcounts ($23.2k against $5.9k).

### Pre-declared cohort design

These rules were committed in checkpoint `cf9db0b` before any outcome was analysed, and have not changed since.

- **Frame:** every wallet paid a REWARD on day D0, selected on receipt only, never on profit.
- **Cohort A:** D0 = 2026-04-15, window to 2026-07-14.
- **Cohort B:** D0 = 2026-07-01, window to 2026-09-29.
- **Tiers:** by D0 reward.

| Tier | D0 reward | Frame size A | Frame size B |
|---|---|---|---|
| T1 | < $1 | 552 | 66 |
| T2 | $1–10 | 2,496 | 2,181 |
| T3 | $10–100 | 938 | 820 |
| T4 | ≥ $100 | 194 | 192 |

- **Sample:** 40 wallets per tier per cohort, drawn with `random.Random(20260929)`.
- **Unusable:** one wallet in A-T2 (`0xd059c842…42c6`) has no P&L series. It is not replaced.

**Caveat.** The D0 reward is a proxy for activity, not for capital. For example, the A-T1 wallet `0xe9076a87…cff6` had $228k in cash and a −$4.73M trading result while earning less than $1/day in rewards. **Medians, not means, carry the answer.**

---

## 2. SPECIAL TASK 17 — Do small Polymarket liquidity providers make NET money?

**Answer: no for the small reward tiers. Yes for the largest recipients, where the reward itself is the profit.**

### 2.1 Tier results (90 days; USD)

Top-k is the share of all positive net captured by the k best wallets.

| Cohort · tier | N | net>0 | trading>0 | median net | mean net | p25 / p75 net | median trading | mean trading | median reward | median rebate | top-1/5/10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A·T1 (<$1/d) | 40 | 57% | 55% | **+1** | −112,744 | −133 / +71 | 0 | −113,720 | 0.8 | 0.0 | 68/93/100% |
| A·T2 ($1–10) | 39 | **36%** | 26% | **−106** | +1,428 | −2,521 / +119 | −199 | +597 | 51.7 | 22.5 | 44/99/100% |
| A·T3 ($10–100) | 40 | 52% | 48% | **+62** | −23,643 | −3,077 / +10,436 | −149 | −27,927 | 414.8 | 82.2 | 37/79/97% |
| A·T4 (≥$100) | 40 | **78%** | 50% | **+9,051** | +218,068 | +740 / +106,145 | −32 | +185,309 | 4,531.7 | 964.5 | 28/75/95% |
| B·T1 | 40 | 57% | 50% | **+6** | +12,133 | −106 / +5,216 | 0 | +9,095 | 24.7 | 29.7 | 46/84/98% |
| B·T2 | 40 | **42%** | 30% | **−3** | −8,718 | −669 / +287 | −74 | −9,425 | 68.0 | 20.1 | 26/85/100% |
| B·T3 | 40 | 55% | 40% | **+172** | +58,565 | −701 / +6,678 | −164 | +56,237 | 296.9 | 80.1 | 89/97/99% |
| B·T4 | 40 | **90%** | 48% | **+23,468** | +156,353 | +2,307 / +83,186 | −133 | +114,078 | 14,201.5 | 1,678.3 | 43/81/91% |

**Weighted back to the full frame**, the share of all reward recipients net positive was **44% (A) and 49% (B)**. The share with positive trading P&L was 36% and 34%.

Means are driven by a few large directional wallets with ±$1–4.7M trading P&L. They are reported but not used.

### 2.2 Decomposition: TRADING + REWARDS + REBATES = NET

**Sums** (show the split, not the typical result):

| Cohort · tier | Trading | Rewards | Rebates | Net |
|---|---|---|---|---|
| A·T4 | +7.41M | +0.84M | +0.47M | +8.72M |
| B·T4 | +4.56M | +1.20M | +0.49M | +6.25M |
| A·T2 | +23k | +11k | +22k | +56k |
| B·T2 | −377k | +10k | +18k | −349k |

**Share of wallets positive under each definition** (trading only / + rewards / + rebates / full net):

| Tier | A | B |
|---|---|---|
| T1 | 55 / 55 / 55 / 57% | 50 / 55 / 52 / 57% |
| T2 | 26 / 36 / 28 / 36% | 30 / 42 / 35 / 42% |
| T3 | 48 / 52 / 48 / 52% | 40 / 55 / 40 / 55% |
| T4 | 50 / **75** / 55 / 78% | 48 / **88** / 48 / 90% |

**How often the subsidy turns a trading loss into a net gain:**

| Tier | A | B |
|---|---|---|
| T1 | 1 of 18 losers | 3 of 20 |
| T2 | 4 of 29 | 5 of 27 |
| T3 | 2 of 21 | 6 of 24 |
| T4 | 11 of 20 | 17 of 21 |

**How much subsidy the losers received against their trading loss:**

| Tier | A | B |
|---|---|---|
| T2 | $15.4k against −$234k | $21.9k against −$531k |
| T4 | $616k against −$641k | $805k against −$951k |

**Net per dollar of volume** (median, wallets with uncapped volume ≥ $1k):

| Tier | Trading A / B | Subsidy A / B | Net A / B |
|---|---|---|---|
| T2 | −168 / −215 bp | +21 / +32 bp | −96 / −93 bp |
| T4 | −24 / −189 bp | +81 / +291 bp | +28 / +158 bp |

**Answers to the five required questions:**

1. **Do rewards merely offset negative trading?**
   - **Small tiers (T1–T3):** rewards do not even offset it. Across tiers and cohorts, the losers' subsidy was 0.4–37% of their trading loss (T2: 4–7%), and it flipped the sign for only 5–25% of losers.
   - **T4:** median trading is about 0 (−$32 and −$133), and **the reward is the profit**. Rewards cover the loss for 55–81% of T4 losers.
2. **Do rebates create genuine net?** **No.** Adding rebates to trading barely changes the share positive (T4: 50→55% and 48→48%; all tiers: 45→47% and 42→44%). Rebates are a secondary transfer to the same wallets that trade the most.
3. **Is there profitability in the small tiers?** **No.** T1 median net is +$1 and +$6 over 90 days. T2 median is −$106 and −$3, with only 36–42% positive. T3 median is +$62 and +$172, with 52–55% positive and top-5 concentration of 79–97%. None of these is a rent.
4. **Does it persist across both cohorts?** Yes, and it points the same way in both. T4 is positive in both (78% and 90%). T2 is negative in both. T1 and T3 hover around zero in both.
5. **Did it survive the rebate-pool decay?** Partly tested. The rebate pool collapsed between 09-01 and 09-15 (§4). Cohort B's month 3 (08-30 → 09-28) includes only about 2 weeks of the new regime.
   - In month 3, B·T4 was still 75% net positive, with a median of +$4,601.
   - T4 profit is carried by rewards, not rebates. The collapse mainly removed the very largest rebate earners, not the sampled wallets: B·T4 rebates were $102k in month 2 and $105k in month 3.
   - The reward pool itself is down 23% since July.

### 2.3 Month-by-month persistence (30-day blocks)

Each cell is the share of wallets net positive in that month, then the median net.

| Cohort · tier | Month 1 | Month 2 | Month 3 | Positive in all 3 months | No subsidy in month 3 (exit) |
|---|---|---|---|---|---|
| A·T1 | 65%, +1 | 48%, 0 | 55%, 0 | 25% | 28/40 |
| A·T2 | 44%, −4 | 36%, −6 | 23%, −2 | **10%** | 18/39 |
| A·T3 | 60%, +165 | 50%, 0 | 38%, −2 | 15% | 14/40 |
| A·T4 | 78%, +8,412 | 62%, +872 | 50%, 0 | 22% | 14/40 |
| B·T1 | 57%, +3 | 50%, 0 | 42%, 0 | 28% | 20/40 |
| B·T2 | 42%, −3 | 45%, 0 | 38%, 0 | **8%** | 21/40 |
| B·T3 | 48%, −43 | 65%, +42 | 45%, 0 | 15% | 17/40 |
| B·T4 | 88%, +5,420 | 80%, +7,178 | **75%, +4,601** | **55%** | **4/40** |

**Small recipients mostly leave.** Between 45% and 70% of T1 and T2 wallets receive no subsidy at all by month 3.

**Only B·T4 is persistently profitable** (55% positive in every month). Cohort A's T4 decays: 14/40 had left by month 3.

**Subsidy to the sampled B·T4 wallets by month:**

| | Month 1 | Month 2 | Month 3 |
|---|---|---|---|
| Rewards | $504k | $400k | $293k |
| Rebates | $287k | $102k | $105k |

### 2.4 Capital ratios and flags

**Net / cash at D0** (median over 90 days; cash ≥ $100 only; cash excludes positions, so it is a lower bound on capital and the ratio is overstated):

| Tier | A | B |
|---|---|---|
| T1 | +2.5% | +21.0% |
| T2 | −40.4% | −1.8% |
| T3 | +4.4% | +10.5% |
| T4 | +89% | +192% |

**Flags** (descriptive only; no wallet was dropped because of a flag):

| Flag | A | B |
|---|---|---|
| Missing start P&L | 0 | 0 |
| Volume capped at 5,000 records (a lower bound) | 50 | 57 |
| Cash < $10 (capital proxy about zero) | 16 | 11 |
| Leaderboard ALL P&L vs user-pnl differ > max($1k, 20%) | 23 | 37 |

**Robustness check without the leaderboard-flagged rows.** Conclusions are unchanged:

| Tier | A | B |
|---|---|---|
| T1 | 59%, +1 | 53%, 0 |
| T2 | 34%, −69 | 38%, −4 |
| T3 | 50%, +14 | 56%, +172 |
| T4 | 82%, +13,788 | 86%, +10,622 |

### 2.5 Secondary view by cash at D0

This is descriptive only. It is not a redefinition of the pre-declared tiers and was not used to select a candidate. It uses the mission's example capital bands, and cash is a lower bound on capital.

| Cash band at D0 | A: n, net>0, median net, median trading, median subsidy | B: n, net>0, median net, median trading, median subsidy |
|---|---|---|
| < $500 | 50, 44%, **−4**, −23, 5 | 43, 56%, **0**, −14, 30 |
| $500–2k | 27, 56%, +44, −176, 278 | 27, 56%, +125, −781, 406 |
| $2k–10k | 30, 43%, **−93**, −1,678, 810 | 36, 61%, +2,471, −729, 826 |
| > $10k | 52, 75%, +18,945, **+18,420**, 5,019 | 54, 69%, +12,953, **+4,942**, 6,487 |

- **Small-cash participants do not earn a rent.**
- **The > $10k band is profitable mainly from trading**, which is directional skill or beta, not subsidy.

**Exploratory subgroup (not pre-declared):** T4 wallets with cash < $5k are net positive 9 of 15 (A) and 13 of 14 (B). Median trading was −$5.3k and −$8.4k, and median rewards $1.5k and $10.8k. **Their real capital must exceed their cash**, so this is not proof of small-capital viability.

---

## 3. SPECIAL TASK 18 — Numerai payout dispersion

**Classic tournament:**
- Rounds 1213–1341, opened 2026-02-27 → 08-26 and resolved by 09-28. The payout factor was 0.087–0.132 (legacy staking, where the stake is the capital).
- There is no structural break in total stake, which stayed at about 670–820k NMR per round.
- Across the platform, payouts were 76,149 NMR on a mean stake of 745,590 NMR: **+10.2% in NMR over about 6 months.**

**Census:** 5,981 models were staked at least once, and 2,851 for the whole window. Frame = all staked models; burns are included as negative payouts.

| Mean stake (USD at mean price $8.65) | N | Net NMR > 0 | Median return | p25 / p75 | Median payout (USD) |
|---|---|---|---|---|---|
| < $500 (of which < $50 "dust" = 4,488) | 5,321 | 70.5% | +4.9% | −0.9 / +14.1% | $0.04 |
| of which $50–500 | 833 | 74.5% | +6.6% | −0.0 / +14.9% | $7.53 |
| $500–2k | 305 | **78.0%** | **+6.7%** | +0.9 / +16.0% | **$61.66** |
| $2k–10k | 227 | 70.9% | +5.0% | −0.7 / +15.6% | $220 |
| > $10k | 128 | 79.7% | +9.0% | +1.7 / +21.1% | $2,419 |

- **Concentration:** the top 1/5/10/100 models take 8.5/22.4/33.4/83.6% of positive payouts. Stakes under $500 receive **2.2%** of positive payouts.
- **Burns are frequent:** the median model had about 42 negative rounds out of 107–124 staked.
- **Persistence is driven by a shared factor, not individual skill.** In the first half of the window only **46%** of models were positive (median −0.7%); in the second half 83% (median +10.1%). The correlation between the two halves is negative (−0.11 to −0.29). Returns ride the meta-model's regime.
- **Price risk:** NMR moved $16.90 → $12.40 over 12 months (**−27%**), with a **−63%** maximum drawdown (low $6.30 on 2026-03-30). Over the window itself NMR went $7.93 → $10.33 → $12.40 today. **USD results in the window are mostly NMR price appreciation, not rent.** Over 12 months, a USD holder earning about 10–20% in NMR would still have lost money.
- **The regime has changed.** v3 "atomic" staking applies from round ~1363 (opened 2026-09-25): payout factor 1.0, stake threshold 72,000 NMR, per-round stake = total locked / R ("1/64th" in the docs). No v3 round has resolved yet, so the **current regime is UNKNOWN**.

**Signals tournament:**
- Rounds 1173–1301, 912 models. Across the platform payouts were +38.5% in NMR.
- Stakes under $500 (764 models): **46% positive, median −0.9%**.
- Top-5 models take 73.5% of positive payouts. **Signals is not a small-player rent.**

Receipts: `agent6_data/numerai/` (census metadata, analysis output, per-model CSV) and `agent6_scripts/numerai/` (`roundDetails` GraphQL fetch plus analysis).

---

## 4. Program decay: daily pools (on-chain)

`agent6_data/decay_series.json` sums one daily payout window per date. Dates whose block window could not be validated to cover the payout hour are UNKNOWN.

| Day (2026) | Reward recipients | Reward total | Reward median | Reward top-10 | Rebate recipients | Rebate total | Rebate top-10 |
|---|---|---|---|---|---|---|---|
| 04-01 | 3,298 | $30,002 | $1.5 | 21.8% | 5,203 | $915,293 | 87.1% |
| 04-15 | 4,180 | $128,087 | $3.28 | 27.0% | 7,125 | $1,035,744 | 82.5% |
| 05-01 | 3,077 | $114,879 | $5.04 | 28.3% | 7,470 | $1,686,916 | 89.4% |
| 05-15 | 2,896 | $69,959 | $4.05 | 24.1% | 7,642 | $841,924 | 80.5% |
| 06-01 | 3,182 | $77,495 | $3.16 | 30.7% | 6,708 | $854,223 | 80.5% |
| 06-15 | 3,995 | $138,931 | $4.8 | 24.2% | 7,794 | $1,678,066 | 81.1% |
| 07-01 | 3,266 | $136,946 | $4.23 | 28.1% | 7,522 | $1,643,540 | 81.2% |
| 07-15 ⚠ | 5,352 | $265,933 | $5.57 | 22.7% | 7,522 | $2,299,043 | 87.1% |
| 08-01 | 2,948 | $126,991 | $4.85 | 25.6% | 5,697 | $1,054,074 | 86.8% |
| 08-15 | 2,390 | $100,810 | $4.17 | 31.5% | 5,482 | $1,168,086 | 86.4% |
| 09-01 | 2,463 | $105,528 | $4.61 | 24.3% | 4,632 | $1,014,299 | 86.3% |
| 09-15 | 2,562 | $112,229 | $4.28 | 25.3% | 4,727 | $161,994 | 21.6% |
| 09-29 | 2,224 | $105,738 | $4.68 | 22.7% | 4,396 | $123,954 | 20.5% |

⚠ 07-15: the main payer made 6,563 transfers to 5,352 recipients (about 2 per wallet), against about 1 per wallet on other dates. This probably includes a catch-up batch, so it is not used as a trend point. Every window was checked on-chain to cover midnight −3h to +4h.

- **Rewards.** The program ramped up in early April ($30k on 04-01). Since then it has paid **$70–139k/day**, and since August **$101–112k/day**.
  - Recipients fell from 2.9–4.2k (April–July) to **2.2–2.6k (August–September)**.
  - The median payout stayed at $4–5.
  - Change from 07-01 to 09-29: −23% in pool, −32% in recipients.
- **Rebates.**
  - April → 09-01: **$0.84–2.30M/day**, with the top-10 taking 80–89%.
  - Then, **between 09-01 and 09-15**, the pool collapsed to **$162k and $124k/day**, and the top-10 share fell to 21–22%. The very large rebate earners disappeared. Their cause (for example a fee change in high-fee markets) is **not verified**.
  - Recipients fell from 7.1–7.8k (April–July) to 4.4–4.7k (September).
- **Effect on the cohorts.** The collapse hit mainly wallets outside the reward sample. The sampled B·T4 wallets received rebates of $287k, $102k and $105k in months 1, 2 and 3. Cohort B's month 3 (08-30 → 09-28) contains only about 2 weeks after the collapse. **Survival past the collapse is therefore only weakly tested.**

---

## 5. CANDIDATE CARDS

### C1 — PM-LR-T4 · Polymarket liquidity rewards, top reward tier

| Field | Value |
|---|---|
| ID | C1 PM-LR-T4 |
| PROGRAM / VENUE | Polymarket (international CLOB) liquidity rewards, plus maker rebates |
| TYPE | reward (liquidity subsidy), with rebate |
| PAYER | Polymarket treasury (rewards). Takers' fees (rebates). |
| WHY PAYER CONTINUES | The venue buys two-sided depth to attract takers. Fees now fund the rebates. This is a business reason, but a discretionary one. |
| PAYMENT MECHANISM | Daily pUSD (earlier USDC.e) ERC-20 transfers from the payer wallets at about 00:00 UTC, pro rata to scored resting liquidity |
| RECEIPT | On-chain payer logs (§1), data-api `activity?type=REWARD\|MAKER_REBATE`, `user-pnl-api`. Frames and results are in `agent6_data/`. |
| PERIOD | Cohorts A (04-15 → 07-14) and B (07-01 → 09-29), 2026 |
| STILL ACTIVE IN 2026? | Yes. Paid on 2026-09-29: $105k to 2,161 wallets (plus $0.4k secondary). |
| TOTAL PAYMENTS | About $126–137k/day on the frame days; $105k/day on 09-29 (§4) |
| NUMBER OF PARTICIPANTS | 4,180 (04-15), 3,259 (07-01), 2,224 unique (09-29) reward recipients a day. T4 is 194 and 192. |
| SMALL-PARTICIPANT COHORT DEFINITION | Pre-declared D0-reward tiers. T4 is ≥ $100/day (not small). The small tiers are T1 and T2 (< $10/day). |
| FRACTION NET PROFITABLE | T4: 78% (A), 90% (B). T1/T2: 36–57%. All recipients (frame-weighted): 44–49%. |
| MEDIAN NET P&L | T4: +$9,051 (A), +$23,468 (B) per 90 days. T1/T2: −$106 to +$6. |
| REWARD / SUBSIDY | T4 median rewards $4.5k and $14.2k per 90 days; rebates $1.0k and $1.7k |
| TRADING P&L EXCLUDING REWARD | T4 median −$32 and −$133 (p25 −$6.9k and −$13.8k) |
| NET P&L INCLUDING REWARD | T4 p25 +$740 and +$2,307; p75 +$106k and +$83k |
| FEES | Makers pay 0 in 2026. Taker fees on hedges are already inside the P&L. |
| CAPITAL REQUIRED | T4 cash at D0 median $14.1k and $11.7k (p25 $2.5k and $2.1k). This is a lower bound; positions are excluded. |
| CAPITAL LOCK | Orders are not locked, but inventory is held until resolution; binary loss at resolution |
| SPEED | MODERATE AUTOMATION at least. Adverse selection (negative median trading in every tier) suggests quote-pull speed matters. LOW-LATENCY is not ruled out. |
| INFRASTRUCTURE | 24/7 post-only quoting bot across many markets, cancel on news, inventory control |
| PROFIT CONCENTRATION | T4 positive net: top-1/5/10 = 28/75/95% (A), 43/81/91% (B) |
| PROGRAM DECAY | Reward pool −23% and recipients −32% from 07-01 to 09-29. Rebate pool collapsed about 85% between 09-01 and 09-15 (§4). Cohort A T4 lost 14/40 wallets by month 3. |
| TEMPORARY OR STRUCTURAL? | A structural need for liquidity, but a discretionary budget. The platform has changed the payer, token and rates within 2026. |
| €100 ECONOMICS | Not reachable at T4 scale. Evidence for cash < $500: median net about $0 per 90 days → **≈ €0/month** |
| €500 ECONOMICS | Same band → **≈ €0/month** (44–56% positive) |
| €1,000 ECONOMICS | $500–2k cash band: median +$44 / +$125 per 90 days → **≈ €15–40/month median, 56% positive**. Trading is negative and offset by rewards. Weak. |
| €5,000 ECONOMICS | $2k–10k band: median −$93 (A) vs +$2,471 (B) per 90 days → **UNKNOWN** (inconsistent across cohorts) |
| CAPACITY CEILING | Reward pool about $105k/day for all makers. The T4 median of $3–8k/month per wallet is incumbent scale. A new entrant's ceiling is UNKNOWN. |
| TAIL RISK | Being picked off before news or resolution. UMA disputes. Budget cut. Access: geoblock (owner-declared access, unverified). |
| ACCESS | Polymarket international. Close-only in the US, France and others. Must be checked with `/api/geoblock` from the owner's location. |
| CAN VERIFY IN 1 DAY? | Yes. Scripts and frames are committed; re-run takes about 1 hour. |
| CHEAPEST FALSIFICATION TEST | Pre-registered: cohort C = the 2026-09-29 frame (committed), tiers unchanged. On 2026-10-29 measure 30-day net. C1 is falsified if T4 net>0 < 60% or median ≤ 0. |
| CONFIDENCE | **VERIFIED** (net-positive distribution for T4 incumbents, 2 cohorts). **UNVERIFIED** as reachable for a new small entrant. |

### C2 — NMR-CLASSIC · Numerai Classic staking payouts

| Field | Value |
|---|---|
| ID | C2 NMR-CLASSIC |
| PROGRAM / VENUE | Numerai Classic tournament (staked predictions) |
| TYPE | prize / service payment (paid in NMR) |
| PAYER | Numerai (hedge fund) treasury in NMR; NMR buybacks |
| WHY PAYER CONTINUES | The stake-weighted meta-model feeds the fund's trading. This is a durable research-value reason. |
| PAYMENT MECHANISM | Per-round payout = stake × payout factor × score; negative scores burn stake |
| RECEIPT | Public GraphQL `roundDetails` (per model, per round: stake, payoutSettled). Census in `agent6_data/numerai/`. |
| PERIOD | Rounds opened 2026-02-27 → 08-26 (129 rounds), resolved by 2026-09-28 |
| STILL ACTIVE IN 2026? | Yes. The rules changed to v3 on 2026-09-25. |
| TOTAL PAYMENTS | 76,149 NMR net over the window (about $660k at the mean price) |
| NUMBER OF PARTICIPANTS | 5,981 staked models (about 3,900–4,340 per round) |
| SMALL-PARTICIPANT COHORT DEFINITION | Mean stake < $500 and $500–2k (USD at the mean window price) |
| FRACTION NET PROFITABLE | 70.5% (< $500), 78.0% ($500–2k), in NMR |
| MEDIAN NET P&L | < $500: $0.04 (dust-dominated), of which $50–500: $7.53. $500–2k: **$61.66 per 6 months** (+6.7%). |
| REWARD / SUBSIDY | The payout is the whole revenue |
| TRADING OR SERVICE P&L EXCLUDING REWARD | Not applicable (burns are netted into the payout) |
| NET P&L INCLUDING REWARD | As above, in NMR. **USD net over 12 months is negative** for a holder (NMR −27%). |
| FEES | None to the platform. Gas or wallet costs under v3 are UNKNOWN. |
| CAPITAL REQUIRED | Any NMR stake. Meaningful at ≥ $500. |
| CAPITAL LOCK | Stake locked through each round's scoring (about 1 month). v3 splits it across R concurrent rounds. |
| SPEED | LOW SPEED REQUIREMENT (daily or weekly submissions) |
| INFRASTRUCTURE | A model at least as good as the median staked model; a daily submission pipeline |
| PROFIT CONCENTRATION | Top-10 = 33.4% of positive payouts; < $500 stakes get 2.2% |
| PROGRAM DECAY | Payout factor 0.107 → 0.087 (dilution). New v3 regime and scoring formula from round ~1363 are unmeasured. |
| TEMPORARY OR STRUCTURAL? | Structural payer. The rules and token price are highly unstable. |
| €100 ECONOMICS | ≈ +5–7% NMR per 6 months → **≈ €1/month**, before NMR price moves |
| €500 ECONOMICS | ≈ **€5–6/month** in NMR |
| €1,000 ECONOMICS | ≈ **€11/month** in NMR |
| €5,000 ECONOMICS | ≈ **€40–55/month** in NMR. NMR volatility (±50%/yr) dominates. |
| CAPACITY CEILING | Not binding for small stakes (payout-factor dilution is platform-wide) |
| TAIL RISK | NMR crash (−63% drawdown observed). Burn streaks (first half 2026: only 46% positive). Unilateral rule changes. |
| ACCESS | Worldwide. Needs an NMR wallet. Crypto tax applies. |
| CAN VERIFY IN 1 DAY? | Yes (census reproduced by the lead from the committed CSV) |
| CHEAPEST FALSIFICATION TEST | When the first 20 v3 rounds (≥ 1363) resolve (about late October 2026), recompute stake-tier returns. Falsified if < $2k stakes have median NMR return ≤ 0 or < 55% positive. |
| CONFIDENCE | **VERIFIED** (NMR net, legacy window). **UNVERIFIED** in USD and under v3. |

### C3 — MTC-AIB · Metaculus AI Benchmark (FutureEval) prizes

| Field | Value |
|---|---|
| ID | C3 MTC-AIB |
| PROGRAM / VENUE | Metaculus AI forecasting benchmark tournaments and MiniBench |
| TYPE | prize |
| PAYER | Metaculus (grant-funded); sponsors donate LLM credits |
| WHY PAYER CONTINUES | Research value (benchmarking AI forecasting). Grant-dependent. |
| PAYMENT MECHANISM | Share ∝ max(Σ peer score, 0)², with a minimum-prize cut-off; bank transfer via Ramp |
| RECEIPT | Winners notebooks 31370, 37692 and 39140 (amounts). Metaculus repository `scoring/utils.py`. Metaculus's own bots are excluded from prizes (notebook 38928). |
| PERIOD | Q4 2024 → Summer 2026 |
| STILL ACTIVE IN 2026? | Yes: Summer 2026 pool $50k; MiniBench $1k every two weeks. **2026 payout tables not found.** |
| TOTAL PAYMENTS | $30k per quarter (2024–25); $50k per season (2025–26) |
| NUMBER OF PARTICIPANTS | 45 → 96 → 134 → 173 bots (about 277 in Summer 2026, secondary source) |
| SMALL-PARTICIPANT COHORT DEFINITION | All non-Metaculus entrants (no capital involved) |
| FRACTION NET PROFITABLE | Spring 2026: 37 of 133 owners won anything (**28%**). The median entrant wins $0. |
| MEDIAN NET P&L | **Negative** for the median entrant (prize $0, costs about $0.5–1.3k per season unless covered by credits) |
| REWARD / SUBSIDY | Ranks 4–19 averaged $914 in Q2 2025. Top-3 take 51–60%. |
| TRADING OR SERVICE P&L EXCLUDING REWARD | −LLM costs (about $0.5–1.4 per question) and development time |
| NET P&L INCLUDING REWARD | A top-15 bot: plausibly +$0.5–1.5k per season (UNVERIFIED) |
| FEES | None |
| CAPITAL REQUIRED | €0 |
| CAPITAL LOCK | None. Payout comes months after questions resolve. |
| SPEED | LOW SPEED REQUIREMENT |
| INFRASTRUCTURE | LLM forecasting bot. Template frontier-model bots ranked 10th–18th in the last two seasons. |
| PROFIT CONCENTRATION | Top-1 25–32%; top-3 51–60% |
| PROGRAM DECAY | Pool per external entrant $882 → $556 → about $450 |
| TEMPORARY OR STRUCTURAL? | Grant-funded, so temporary |
| €100 / €500 / €1,000 / €5,000 ECONOMICS | Not capital-based. About €0–400/month for a consistent top-15 bot (UNVERIFIED). The median entrant is ≤ €0. |
| CAPACITY CEILING | One prize-winning bot per person; pool about $50k per season |
| TAIL RISK | Programme ends; eligibility (the Ramp country list) |
| ACCESS | Worldwide, subject to Ramp's supported countries |
| CAN VERIFY IN 1 DAY? | Partly. Tournament pages and the API return 403; notebooks are readable. |
| CHEAPEST FALSIFICATION TEST | Obtain the Fall 2025 and Spring 2026 payout tables. Falsified if the rank ~15 prize is < $300. |
| CONFIDENCE | Prize payments **VERIFIED** (2024–25). Small-entrant net **UNVERIFIED**. |

---

## 6. Adversarial self-audit

| Attack | C1 PM-LR-T4 | C2 NMR-CLASSIC | C3 MTC-AIB |
|---|---|---|---|
| Is the "profit" just subsidy? | **Yes.** Median trading ≈ 0 or negative; the reward is the profit, at platform discretion. | Yes, a payment for a service, but a structural one | Yes, a prize |
| Does earning it create a bigger loss? | For T1–T3, yes: trading losses far exceed subsidies. For T4, no on the median, but half of T4 have trading losses. | Burns are included; net NMR still positive for 70–78% | LLM costs exceed $0 prize for about 72% of entrants |
| Are only survivors visible? | **Partly.** The forward window keeps leavers. But **being in T4 on D0 already embeds prior survival**. Entrants who failed to reach T4 appear only in T1–T3, which are not profitable. | No: census of all staked models, leavers included | Entrant counts known; the zero-prize majority is counted |
| Does it favour large capital? | **Yes.** Profit sits in T4 and the > $10k cash band; small bands are about €0. | Same % returns; tiny absolute amounts | No capital |
| Is low latency required? | Possibly, for adverse-selection control. Not proven either way. | No | No |
| Is it already decaying? | **Yes.** Rebates collapsed in September, rewards −23% since July, recipients −32%, A-cohort T4 exits. Post-collapse evidence covers only about 2 weeks. | Dilution; regime change unmeasured | Pool per entrant falling |
| Is capital lock understated? | Cash is a lower bound; positions are excluded | v3 splits the lock across rounds | None |
| About to expire? | Can end any day | Rules changed 2026-09-25 | Grant-funded |
| Is €/month extrapolated? | Small-capital figures use the secondary cash view and are flagged. T4 figures are incumbent-only. | Linear in stake from medians, NMR-denominated | UNVERIFIED |
| **Result** | Kept as VERIFIED net for incumbents; **downgraded to UNVERIFIED as a small-player target** | Kept: VERIFIED in NMR; UNVERIFIED in USD and under v3 | Kept as prize-verified, net UNVERIFIED |

---

## 7. NEGATIFS UTILES

1. **Small Polymarket reward recipients do not earn a net rent.** Tiers < $10/day have median net of −$106 to +$6 per 90 days, and T2 is only 36–42% positive. For T2 losers, subsidies are only 4–7% of their trading losses. **Across all reward recipients, only 44–49% are net positive.**
2. **Polymarket maker rebates do not create net profit.** Adding them to trading lifts the share positive by 0–5 points. The daily rebate pool also collapsed between 09-01 and 09-15, from $1.01M/day to $162k/day (§4).
3. **Numerai Signals, small stakes:** 46% positive, median −0.9%; top-5 models take 73.5% of positive payouts.
4. **Metaculus AI benchmark:** 72% of owners won $0 in Spring 2026, and the pool per entrant is falling.
5. **Kalshi Liquidity Incentive Program:** live until 2027-01-01 and paying about $712k/day across 5,562 markets, but **US-only**, and there is **no per-account data**, so net maker P&L cannot be measured.
6. **Hyperliquid small maker:** the tier-0 maker fee (1.5 bp) is at least equal to established market makers' total net margin (0.2–1.9 bp/$), and 56.5% of maker-like accounts lost money in the month (agent 1, verified). There is no small-maker subsidy.

---

## 8. FINAL REPORT (7 lines)

1. Branch: `claude/epic-cannon-1sy39m`
2. SHA: see the commit that adds this file (`git log -1 -- research/recus_2026-09/agent6_small_player_rents.md`)
3. Status: **SMALL_PLAYER_RENTS = VERIFIED_NET_CANDIDATES_FOUND**. Net is verified only for top-tier Polymarket reward earners, and in NMR for Numerai Classic; no €100–1,000 entrant rent is verified. REAL_CAPITAL_AUTHORIZED = FALSE.
4. Deeply measured: Polymarket liquidity rewards and maker rebates (320-wallet pre-declared cohorts plus on-chain pools); Numerai Classic and Signals (full census); Metaculus AIB and Kalshi LIP (program-level).
5. Best 3: C1 PM-LR-T4, C2 NMR-CLASSIC, C3 MTC-AIB
6. Strongest verified small-player net result: **Polymarket top-tier rewards.**
   - B·T4: 90% net positive, median +$23.5k per 90 days, trading median −$133.
   - In month 3, 75% were still positive (median +$4.6k); only about 2 weeks of that month fall after the September rebate collapse.
   - But the small tiers T1/T2 are about $0 or negative.
   - **Numerai Classic, $500–2k stakes:** 78% positive, +6.7% NMR per 6 months (about $62).
7. Cheapest next falsification test: pre-registered cohort C (committed 2026-09-29 frame, same tiers). On 2026-10-29, C1 fails if T4 net>0 < 60% or median ≤ 0. In parallel, recompute Numerai on the first 20 resolved v3 rounds.
