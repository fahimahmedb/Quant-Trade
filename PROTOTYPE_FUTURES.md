# Futures trend/carry prototype: a second Quant market instance

- **Branch:** `claude/prototype-futures-trend-carry-6vr22g`. This is a lab branch; no project or Blue branch is modified.
- **Authority:** paper/shadow only. `REAL_CAPITAL_AUTHORIZED` is still FALSE. The branch is a proposal for a Builder mission. It does not change current governance, which keeps product integration paused.
- **Origin:** the lab study `research/deep_research_2026-09-24/` on branch `claude/deep-research-project-6vr22g`, which recommended R2, R3, R6 and R7.

## 1. What the prototype adds

The same planes and the same chain run on a second market: `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK -> LEARNING`. The futures instance has its own persistent Book, journal and queue. It can never touch the ETF instance.

| Plane | Change | File |
|---|---|---|
| Data | A fully collateralised excess-return index per contract, derived from a pinned pysystemtrade snapshot. The Book's `quantity x price` is therefore a real notional. Roll costs (2 half-spreads + 2 commissions) are charged. `carry_ann` is recorded point-in-time. Stale bars are forward-filled for at most 5 sessions and flagged. There is a mechanical scale-glitch exclusion rule, and the git fetch is pinned (network workaround). | `dataplane/futures.py`, `dataplane/ingest.py` |
| Data | The panel accepts point-in-time feature columns and a deterministic `.csv.gz` format (stable fingerprint). A signal cache is attached to each immutable panel. | `dataplane/panel.py` |
| Research Factory | New `ts_trend_carry` family: EWMAC 16/32/64 + smoothed carry. The scalars come from the literature (Carver), not from a fit. Sizing uses volatility targeting and a fixed IDM. Everything is causal, and the research and the Desk use the same code (`weights_for`). The `ts_long_risk_parity` baseline is added. | `factory/signals.py` |
| Research Factory | Pre-registered lanes with 3 expressions each, without a grid. The prior lab trials are charged to the multiple-testing budget. | `factory/lanes.py`, `factory/workers.py` |
| Research Factory | Falsification is family-specific. For time-series families, the test "beta < 0.15" is replaced by two tests: beat long-only risk parity, and keep equity beta below 0.5. The other tests are unchanged: 2x costs, both subperiods, t-stat corrected for the number of trials, concentration. | `factory/evaluate.py` |
| Desk | A per-market profile. Futures use directional limits (gross 4x, net 2x, single line 0.6x) and cost 0.5 + 1.5 bp. The drawdown throttle, drawdown halt and NAV floor are unchanged. | `desk/profiles.py` |
| Control | `--market futures` and `--market futures-broad` select an instance with its own state (`var/futures*`). A session calendar can be driven by a reference contract, which allows staggered entry. The cohort audit is memoised by fingerprint (60x faster on large panels). | `clock.py`, `paths.py`, `scripts/quant.py` |
| Book | Every mark records the cumulative P&L of each sleeve. `sleeve_returns()` rebuilds the daily P&L of each strategy. | `book/ledger.py` |
| Learning | A t-SPRT with plug-in sigma. It tests each sleeve's own shadow P&L every month and **drives the lifecycle**: promotion, DECAYING, or RETIRED. Before this change, the `shadow` field of strategies was never populated. | `learning/sequential.py`, `clock._review_live_evidence` |

## 2. How to run it

```bash
# narrow instance: 31 contracts aligned on a shared calendar since 2002
PYTHONPATH=src python3 scripts/quant.py run --market futures
# broad instance: 144 contracts, staggered entry since 1990
PYTHONPATH=src python3 scripts/quant.py run --market futures-broad
PYTHONPATH=src python3 scripts/quant.py brief --market futures-broad   # writes CHIEF_BRIEF_FUTURES_BROAD.md
```

To re-derive the datasets without network access to the vendor APIs, run `quant.dataplane.ingest.ingest_futures_panel(..., broad=True|False)`. The pinned commit is fetched through git.

## 3. Results (paper/shadow, simulated; the protocol after all fixes)

Every expression was pre-registered, with costs by contract and rolls charged on |w|. Validation Sharpe (SR) values are annualised on daily returns.

| Lane (dataset) | Discovery winner | Discovery SR | Validation | Validation SR / t | Required t (trials) | Alpha t vs baseline | Verdict |
|---|---|---|---|---|---|---|---|
| `ts_trend_carry_futures`: 31 aligned contracts | trend 0.5 + carry 0.5 | 0.82 (2002-2014) | 2014-05 → 2020-09 | **0.07 / 0.18** | 2.84 (11) | 0.11 | **REJECT** |
| `ts_trend_carry_futures_broad`: 144 contracts, staggered | trend only | 0.58 (1990-2009) | 2009-03 → 2019-05 | **-0.52 / -1.69** (costs 128% > gross 108%) | 3.02 (20) | -1.66 | **REJECT** |
| `..._broad_speed_limited`: cost ≤ 0.13 SR | trend 0.5 + carry 0.5 | 1.15 | 2009-03 → 2019-05 | **0.49 / 1.59** | 3.07 (23) | 1.49 | **REJECT** |

How to read these results:

- **The system works as its North Star demands.** It rejects, costs are counted, the trial budget is honest, and the reasons are traced in the ticket.
- **The lab was optimistic.** The lab (Sharpe ~1.06 on 190 instruments) divided pysystemtrade's `SpreadCost` by 2, when it is already a half-spread (per the pysystemtrade docs, *"Slippage … Half the bid-ask spread"*). It also underestimated rolls on illiquid contracts. Breadth only pays when it is affordable: the vol targeting puts large notionals on low-volatility, expensive contracts, whose rolls then consume the edge.
- **The most promising candidate is the speed-limited broad lane** (Sharpe 0.49 in validation, baseline 0.42, alpha t 1.49). It cannot be accepted on this history because the validation window is exhausted and contaminated. Only forward data (> 2024-03-28) can decide.
- The rejected strategies still run in shadow on the **evaluation ledger** (zero authority). The Learning plane measures whether each rejection was wrong ("false reject").

Shadow Desk results (evaluation ledger, rejected strategies, windows seen by the lab, **not evidence**): see §6.

## 4. Red team and audit

The process ran in this order:

1. Implementation.
2. Two independent red teams in parallel, working read-only on commit `c124c3b`:
   - economic and research integrity;
   - runtime, restart and isolation.
3. My own audit.
4. The fixes.
5. A final audit on the new head.

### 4.1 Economic red team: its findings and what was done

| # | Severity | Finding | Fix |
|---|---|---|---|
| E1 | HIGH | The lab had already seen the whole futures history, including the validation and shadow windows. They are therefore not a pristine out-of-sample test. | `pristine_after = 2024-03-28` is recorded in the lane, the ticket and the strategy evidence. The lifecycle can only act on shadow returns **after** that date. The full series is still tested, but labelled `monitoring_including_seen_history`. Every earlier look is charged to the multiple-testing budget: 8 prior trials on the narrow dataset and 17 on the broad one. |
| E2 | HIGH (sign) | The roll cost was subtracted from the index, which **credited** it to short positions (a bias of 26-30 bp/yr in the strategy's favour). | The index now excludes roll costs. They are published in a `roll_cost` column and charged on **\|w\|** in research (`walk_forward`) and on \|notional\| at the Desk (`CapitalDesk._charge_rolls` → `Ledger.apply_charge`, idempotent). |
| E3 | MED | The test "beats long-only risk parity" was a point comparison against a weak baseline. | A new test requires the alpha of the strategy regressed on the baseline to have t ≥ 2. |
| E4 | MED | The SPRT is effectively inert at a Sharpe of 0.5 (decades to reach a decision). | The expected time to a decision is now published, and the SPRT is documented as **monitoring**. A decision only uses pristine data. |
| E5 | LOW-MED | Carry could go stale (DAX/FTSE observed rarely). | Carry not refreshed for 20 sessions is dropped. |
| E6 | LOW | There were 86 sessions on Sundays (Globex snapshots). | Weekends are removed from the calendar. A roll on a non-session day is charged on the next session. |
| E7 | LOW | The flat 4 bp cost undercharged expensive commodities. | A per-contract `cost_bps` feature is added. Research and the Desk both charge max(uniform cost, contract cost). |
| E8 | LOW | Gross notional is not a risk measure for a vol-targeted book. | Declared as a limit (§5). No ex-ante volatility limit yet. |

Verified clean by the red team:
- The first REJECT was computed correctly.
- Desk and research correlate at 0.999 on the shadow window.
- `sleeve_pnl` adds back to NAV within 7e-9.
- The index math and the carry sign are correct.
- No leakage through `panel.derived`.

### 4.2 My own audit (before and after the red team)

- **A1 BLOCKER**: on the broad universe, 52 of 144 contracts cost more than 4 bp (some 50-300 bp). The first "validation" (Sharpe 1.10, t 3.57) came from the cost assumption. After correction: Sharpe 0.65, t 2.11, **REJECT**. Fixed with the per-contract costs of E7.
- **A2**: a bug in `sleeve_returns` dropped a new sleeve's first day of P&L. It was caught by the multi-strategy test and fixed.
- **A3**: the prior trials were double-counted when several lanes declared them. They are now reserved once per dataset, under `<dataset_key>:prior-trials`.
- **A4 perf**: the cohort audit re-hashed 180k bars on every tick (10 s per session). It is now memoised by fingerprint (0.17 s per session).
- **A5 perf (not fixed)**: the ledger rewrites and fsyncs its whole JSON on every fill, which is quadratic at 100+ fills per session. The broad instance takes about 3-5 s per session as a result. This is a legacy ETF-scale design; fixing it (fill batching) touches persistence invariants, so it is left to a dedicated mission.

## 5. Known limits

- The data is third-party (pysystemtrade repository). It is not an exchange feed and carries mild survivorship bias (contracts still quoted in 2024). Currency effects are not modelled. Volume is missing, so **capacity is not modelled**.
- Current cost estimates are applied to the whole history, which likely understates early-2000s costs. Rolls are modelled as two outright trades, which is conservative because a calendar spread usually costs less.
- Execution is modelled at close(t+1), because the dataset has no separate open/close. There is no ex-ante portfolio volatility limit, only a notional gross limit plus drawdown limits.
- The SPRT only moves the lifecycle on data after 2024-03-28, so nothing has moved it yet. At a Sharpe of 0.5 it is monitoring (decades to reach a decision), not a fast kill switch. The `expected_sessions_to_accept_if_true` field says so.
- The ledger rewrites its whole JSON with fsync on every fill (audit finding A5). The broad instance takes 3-5 s per session as a result.
- The Learning plane's "FALSE_REJECT" rule (existing logic) scores the counterfactual on the replayed shadow window, which is also contaminated. Its verdicts on this data are indicative only.

## 6. Recommended next steps

1. **Real forward data.** Open network access to a daily futures source (for example Norgate, CSI or Databento, which need owner approval) and let the instances accumulate sessions after 2024-03-28. That is the only way to decide on the speed-limited lane.
2. Include **roll costs in the speed-limit**. This is a new hypothesis and may only be tested on forward data.
3. **Batch ledger writes** (one atomic write per session, with the same op-ids). This needs a dedicated mission with restart tests.
4. Add an **ex-ante volatility limit** to RISK for vol-targeted books.
5. Make the ETF/futures profiles a first-class configuration surface (for example in `STATE.md`/brief) rather than one hard-coded per dataset.
