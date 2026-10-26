# AGENT 6 — SMALL PLAYER RENTS — state / checkpoint

Checkpoint date: 2026-09-29 (UTC). Public-data research only.
REAL_CAPITAL_AUTHORIZED = FALSE. No orders, no accounts, no production strategy code touched.

**Branch:** `claude/epic-cannon-1sy39m`, the mission branch assigned to this session. The prompt's default branch `research/agent6-small-player-rents-2026-09-29` applies only when no other branch has been assigned, so it is not used.

**STATUS: DONE.** Deliverable: `agent6_small_player_rents.md`.
**SMALL_PLAYER_RENTS = VERIFIED_NET_CANDIDATES_FOUND** (narrow).
- Polymarket liquidity rewards are net positive only for the top reward tier (≥ $100/day at D0): 78% (cohort A) and 90% (cohort B) of wallets.
- The small tiers are about $0 or negative.
- Frame-weighted, 44–49% of all reward recipients are net positive.
- Numerai Classic is net positive in NMR in every stake tier; USD results are dominated by the NMR price.
- REAL_CAPITAL_AUTHORIZED = FALSE.

## 1. Inputs read
- `QUANT_NORTH_STAR.md`.
- Agent 1 `agent1_registres.md` (branch `origin/claude/dazzling-dirac-foklrv`).
- Agent 2 `agent2_profits_mesures.md` (`origin/claude/gallant-cerf-e0rpao`).
- Agent 3 `agent3_recette_recu.md` (`origin/claude/exciting-edison-w68tos`).

Prior agents verified that the Polymarket reward and rebate pools exist. They did not measure net profit for small makers. That is the open question this mission answers.

## 2. Polymarket on-chain payment receipts (VERIFIED, Polygon logs via public RPC)

| Flow | Payer (from) | Token | Period seen | Daily time (UTC) |
|---|---|---|---|---|
| Liquidity rewards (main) | `0xc288480574783bd7615170660d71753378159c47` | USDC.e `0x2791bca1…4174` | Apr 2026 | ~00:00 |
| Liquidity rewards (main) | `0x2c2795ea295d5eb51f9121b728ed2ea4e936a709` (via multisend `0xd152f549545093347a162dce210e7293f1452150`) | pUSD `0xc011a7e12a19f7b1f670d46f03b03f3342e82dfb` ("Polymarket USD", 6 dp) | Jul–Sep 2026 | ~00:00–00:05 |
| Secondary small rewards | `0xf7cd89be08af4d4d6b1522852ced49fc10169f64` (USDC.e); `0xdd8db71ce3be8d71ff148b2163d64da181a29e8b` (pUSD contract) | — | Apr / Jul–Sep 2026 | ~00:15 |
| Maker rebates | `0x3a9418b2651c8164db5ebc56f12008137865e0f7` (USDC.e); `0xfdb1b8dc7f5789a0c9a398026585b8b10fba5507` (pUSD) | — | Apr / Jul–Sep 2026 | ~00:45–01:00 |

Example transactions:
- Reward: `0xdb19c23347597c7adc01102b728da089bf72c7d4c46c553f8d82b293d1f867f4`.
- Rebate: `0x37c5c6beb1f2799e754f1363da4ded3bbd067568b284e2fbb4ec7b050a2a1ba1`.

The data-api labels these flows `REWARD` and `MAKER_REBATE`, and the amounts match the on-chain transfers. Example: RN1 `0x2005d16a…75ea` on 2026-09-29 received a rebate of 4,657.77 on-chain and 4,657.8 in the API.

### Daily recipient counts and pool size (VERIFIED on-chain, full payout window)
| Day | Reward recipients | Reward total | Median | Top-10 share | Rebate recipients | Rebate total | Top-10 share |
|---|---|---|---|---|---|---|---|
| 2026-03-02 | 3,884 | $43,215 | $1.82 | 23.4% | 874 | $77,764 | 85.5% |
| 2026-04-01 | ≥2,694 (secondary payer only; main payer not scanned) | ≥$8,335 | — | — | 5,203 | $915,293 | — |
| 2026-04-15 (**cohort A frame**) | 4,180 | $126,155 | $3.28 | 26.3% | 7,125 | $1,035,744 | 82.5% |
| 2026-07-01 (**cohort B frame**) | 3,259 | $136,887 | $4.25 | 28.2% | 7,522 | $1,643,540 | 81.2% |
| 2026-09-29 | 2,161 main + 266 secondary | $105,338 + $400 | $4.86 | 22.8% | 4,396 | $123,954 | 20.5% |

**Rebate-decay observation (to verify, not yet a conclusion):**
- The daily rebate pool fell about 13×, from $1.64M on 07-01 to $124k on 09-29.
- The top-10 share fell from 81% to 20%. This suggests the very large rebate recipients (probably high-fee markets) disappeared, or are now paid by a payer not yet identified.
- The 09-29 frame is complete for at least RN1.

Reward recipient counts also fell: 4,180 → 3,259 → ~2,427. Meanwhile the median reward per recipient rose: $3.28 → $4.25 → $4.86.

The decay series script (1st and 15th of each month, Mar–Sep) stopped on an RPC timeout after its first date. Only the 03-02 row came from it; the other rows come from the frame scans.

## 3. Method validation (VERIFIED)
- **`user-pnl-api` excludes rewards and rebates.** On days with rewards but no trade, redeem, merge or split, Δuser-pnl ≈ 0:
  - `0x4ddc9fa3055fc42411d95f4fb03267102c64c06f`: 09-26 reward+rebate $28.37, Δ −0.0004; 09-27 $34.96, Δ −0.0007.
  - `0xa0a6ca2c507761d3f5df9f6137113ed584370bb7`: 09-19 $42.51, Δ −2.28.
  - So: **net = Δuser-pnl + REWARD + MAKER_REBATE**.
- **`user-pnl` matches independent accounting.** For b00k13 `0x1c5575dc20e4ea54d1bb09ccda72ccf8a3b684ce` (polymm author), user-pnl at end of April 2026 is +$4,961. The author's blog reports +$4,973 for Jan–Apr.
- **Rejected alternatives:**
  - Activity-feed cash-flow reconstruction misses some redemption or merge inflows. Example: condition `0x32b43c11…` shows a buy of $212, no REDEEM, and a closed-position realized P&L of −$12. The reconstruction gives −$8.8k against a true value of about +$5k.
  - Σ `closed-positions.realizedPnl` overcounts: $23.2k against user-pnl's $5.9k.
- **API limits.** The activity API caps `offset` at 5,000; `pmapi.activity_all` pages backwards with `end=`. Public RPC `getLogs` is limited to 10k blocks. drpc.org serves archive `eth_call` (historical balances); publicnode does not.

## 4. Pre-declared cohort design (fixed before any outcome was looked at)
- **Frame:** every wallet that received a REWARD transfer from the main or secondary reward payers during the D0 payout window. Rows with `reward_usd_d0 > 0` in `agent6_data/frame_*.csv`. Selection is on reward receipt only, never on P&L.
- **Cohort A:** D0 = 2026-04-15, window [D0, D0+90d). Payout blocks 85,544,678–85,550,978. Payers `0xc288…9c47` and `0xf7cd…9f64`.
- **Cohort B:** D0 = 2026-07-01, window [D0, D0+90d), ending 2026-09-29. Blocks 89,438,137–89,446,537. Payers `0x2c27…a709` and `0xdd8d…9e8b`.
- **Tiers** (D0 reward, as an activity/size proxy):

  | Tier | D0 reward | Frame size A | Frame size B |
  |---|---|---|---|
  | T1 | < $1 | 552 | 66 |
  | T2 | $1–10 | 2,496 | 2,181 |
  | T3 | $10–100 | 938 | 820 |
  | T4 | ≥ $100 | 194 | 192 |

- **Sample:** 40 per tier per cohort, 320 wallets in total, drawn with `random.Random(20260929).sample(sorted(tier_members), 40)`. **SEED = 20260929.** The draw is deterministic, so re-running reproduces the same wallets.
- **Metrics per wallet:**
  - trading = user-pnl(D0+90d) − user-pnl(D0), which excludes rewards;
  - rewards and rebates paid in (D0+6h, D0+90d+6h], split into three 30-day months;
  - net = trading + rewards + rebates;
  - cash at D0 = USDC.e + pUSD `balanceOf` at the D0 block, a lower bound on capital;
  - window TRADE volume, capped at 5,000 records, so a lower bound when capped;
  - leaderboard ALL pnl/vol, as a consistency check.

## 5. Sampling script and status
- Scripts are in `agent6_scripts/` (`sample_cohorts.py`, `pmapi.py`, `rpc.py`). The runner reads the frame JSONs in the session scratchpad; the committed `agent6_data/frame_*.csv` files hold the same data.
- **Cohort A: COMPLETE**, 160/160 → `agent6_data/results_A.jsonl`, analysed (`agent6_data/analysis_summary.txt`). 1 wallet has no user-pnl series (`err`), so 159 are usable.
- **Cohort B: COMPLETE**, 160/160 → `agent6_data/results_B.jsonl`, analysed. No errors.
- The background shell exited with code 1. That came only from a trailing `tail -3` syntax error after both runs had finished; the sampler logged `done A` and `done B`.
- To reproduce: `python3 sample_cohorts.py A|B` (about 15–25 min per cohort, 4 threads, public endpoints only).

## 6. Other workstreams
- **Numerai payout dispersion: DONE.**
  - A census via GraphQL `roundDetails` covered 129 resolved rounds for Classic and for Signals.
  - The worker never sent its hand-back message, but its output files were complete. The lead recomputed the Classic tiers from the CSV and they match.
  - The window is entirely the legacy regime: no break in total stake, payout factor 0.087–0.132. v3 (round ~1363 onward) is UNKNOWN.
  - Receipts: `agent6_data/numerai/`.
- **Metaculus AIB (worker result; V = verified, S = secondary):**
  - The API and tournament pages return 403. Notebooks are readable.
  - **Q1 2025:** 45 entrants, 10 paid, pool $30k, top-1 25.6%, top-3 57.5%.
  - **Q2 2025:** 96 entrants, 19 paid, pool $30k, top-3 51.3%.
  - **Spring 2026:** 173 bots; 37 of 133 owners paid (28%). **The median prize across all entrants is $0.**
  - **Prize formula** (Metaculus source, `scoring/utils.py`): each entrant's share ∝ max(Σ peer score, 0)². This concentrates prizes at the top.
  - **Template frontier-model bots** ranked 10th–18th in Fall 2025 and Spring 2026.
  - **Cost:** about $0.5–1.4 per question, or roughly $0.5–1.3k per season. Donated credits are available.
  - **Pool per external entrant** fell from about $882 in Q1 2025 to about $450 in Spring 2026.
  - **Payment** is by bank transfer through Ramp, only to countries Ramp supports.
- **Kalshi:**
  - The Liquidity Incentive Program is live until 2027-01-01 and can be ended at any time. It is US-only.
  - `GET /trade-api/v2/incentive_programs?status=active` (no auth) listed 5,562 active programs worth $711,975 in total period rewards.
  - **There is no per-account data.** Public trades carry no account or maker ID, so net maker P&L after rewards cannot be measured.

## 7. Decay series (DONE)
- Script: `agent6_scripts/decay_series.py`. Output: `agent6_data/decay_series.json`; logs `decay_series.log` and `decay_series_run2.log`.
- Method: block numbers interpolated between on-chain anchors, corrected with real block timestamps. Every window was validated to cover midnight −3h to +4h.
- Attempt 1 used a binary search whose bracket failed before April. It produced a wrong 03-01 row, which was discarded (`decay_series_attempt1_INVALID.log`).
- **Rebate pool:** $0.84–2.30M/day from April to 09-01. It collapsed to $162k (09-15) and $124k (09-29) as the top-10 share fell from 86% to 22%.
- **Reward pool:** $101–112k/day since August, with 2.2–2.6k recipients. Change from 07-01 to 09-29: pool −23%, recipients −32%.

## 8. NEXT_ACTION
- **Mission complete.** Pre-registered follow-up (not authorized to run live; public data only):
  - On 2026-10-29, measure 30-day net for the committed 2026-09-29 frame (cohort C), with the same tiers.
  - C1 is falsified if T4 net>0 < 60% or median ≤ 0.
  - Recompute Numerai on the first 20 resolved v3 rounds.
