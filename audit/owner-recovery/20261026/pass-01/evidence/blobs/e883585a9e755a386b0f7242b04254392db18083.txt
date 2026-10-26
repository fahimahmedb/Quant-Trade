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
| `ts_trend_carry_futures`: 31 aligned contracts | trend 0.5 + carry 0.5 | 0.82 (2002-2014) | 2014-03 → 2020-09 | **0.07 / 0.18** | 2.84 (11) | 0.11 | **REJECT** |
| `ts_trend_carry_futures_broad`: 144 contracts, staggered | trend only | 0.58 (1990-2008) | 2008-11 → 2019-02 | **-0.52 / -1.69** (costs 128% > gross 108%) | 3.10 (26) | -1.66 | **REJECT** |
| `..._broad_speed_limited`: cost ≤ 0.13 SR | trend 0.5 + carry 0.5 | 1.16 | 2008-11 → 2019-02 | **0.47 / 1.52** | 3.13 (29) | 1.45 | **REJECT** |

How to read these results:

- **The system works as its North Star demands.** It rejects, costs are counted, the trial budget is honest, and the reasons are traced in the ticket.
- **The lab was optimistic.** The lab (Sharpe ~1.06 on 190 instruments) divided pysystemtrade's `SpreadCost` by 2, when it is already a half-spread (per the pysystemtrade docs, *"Slippage … Half the bid-ask spread"*). It also underestimated rolls on illiquid contracts. Breadth only pays when it is affordable: the vol targeting puts large notionals on low-volatility, expensive contracts, whose rolls then consume the edge.
- **The most promising candidate is the speed-limited broad lane** (Sharpe 0.47 in validation, baseline 0.43, alpha t 1.45). It cannot be accepted on this history because the validation window is exhausted and contaminated. Only forward data (> 2024-03-28) can decide.
- The rejected strategies still run in shadow on the **evaluation ledger** (zero authority). The Learning plane measures whether each rejection was wrong ("false reject").

### Shadow Desk results

The rejected strategies run on the evaluation ledger, which has zero capital authority. The windows were seen by the lab, so these results are **not evidence**.

| Instance | Sessions | Simulated fills | Ledger NAV (1 M) | Shadow SR | Costs (incl. rolls) | SPRT (monitoring) |
|---|---|---|---|---|---|---|
| narrow (1 strategy) | 837 (2020-09 → 2024-03) | 3,903 | +2.9 % | 0.65 | 2.2 k$ (rolls 1.3 k$) | CONTINUE, ~24 years to reach a decision |
| broad (2 strategies) | 1,304 (2019-02 → 2024-03) | 23,764 | +2.8 % | 0.24 | 49.5 k$ | CONTINUE |

In the broad instance, the unlimited sleeve paid **40.8 k$ of costs, 39.0 k$ of them rolls**, against 8.8 k$ for the speed-limited sleeve. This confirms the research diagnosis: breadth only pays when the contracts are affordable to hold.

Learning counts 1 "false reject" and 1 "undetermined". These are indicative only, because they are scored on a window the lab had already seen.

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
| E7 | LOW | The flat 4 bp cost undercharged expensive commodities. | A per-contract `cost_bps` feature is added. Research charges max(4 bp, contract cost); a Desk fill charges max(model cost of 2 bp, contract cost). Research is therefore the more conservative of the two. |
| E8 | LOW | Gross notional is not a risk measure for a vol-targeted book. | Declared as a limit (§5). No ex-ante volatility limit yet. |

Verified clean by the red team:
- The first REJECT was computed correctly.
- Desk and research correlate at 0.999 on the shadow window.
- `sleeve_pnl` adds back to NAV within 7e-9.
- The index math and the carry sign are correct.
- No leakage through `panel.derived`.

### 4.1b Runtime red team (restart, isolation): findings and actions

What held up:

- **75 `kill -9`** at random points (boot, research, mid-session, monthly review). The final economic state matches the uninterrupted run: identical `book.json`, NAV, cash and attribution within 2e-10, no duplicate tickets, identical `applied_operations`.
- A crash injected right after a review-driven RETIRED transition still gives exactly one transition.
- The dataset rebuilds byte-identically from the pinned commit.
- The ETF and futures instances are isolated from each other.
- The memo cannot return a stale result.

| # | Severity | Finding | Fix |
|---|---|---|---|
| R1 | HIGH | A **RETIRED** sleeve kept its positions in the CAPITAL Book, and nothing managed them any more. | `CapitalDesk.liquidating()` / `ledger_for()`: a strategy with no entitlement that still holds a capital sleeve is flattened through the normal chain. There is a `SCAN LIQUIDATE` trace, a RISK throttle cannot trap the exit, closes are exact, and no minimum size blocks them. Tested with a restart after the exit, and (after the final audit) with a crash after the fills but before the commit. |
| R2 | MED | At boot, a committed snapshot was registered without checking the fingerprint in its sidecar. | A mismatch makes the dataset INVALID and emits a `snapshot_fingerprint_mismatch` FAULT, and the check still holds through `refresh_availability`. Tested with one tampered bar. |
| R3 | MED perf | Whole files were rewritten on every session (`opportunities.jsonl` re-read, journal, ledger). | The opportunity-id set is now cached in memory. The journal and ledger rewrites are documented (A5), not fixed. |
| R4 | LOW | SIGKILL left orphaned staging files behind (24 MB vs 11.5 MB). | Swept at boot, but only files older than 10 min, so a concurrent writer such as the SEC service is never hit. |
| R5 | LOW | Position-level fields (`opened_at`, position `realized_pnl`) depend on crash history. | Existing ledger behaviour. Sleeve attribution and `sleeve_pnl` are unaffected. Documented. |
| R6 | LOW | After a resume, the ticket's `book_effect` only counts the operations that were not replayed. | Existing behaviour. Documented; nothing reads it for decisions. |
| R7 | LOW | The `shadow` stats were sampled monthly and some fields stayed at zero. | The stats are now derived from the full per-mark `sleeve_pnl` path (costs, gross, wins/losses, peak, max drawdown). |
| R8 | LOW | SEC: the futures instance opened a second SEC lifecycle, and `sec-*` commands ignored `--market`. | The SEC lifecycle is skipped outside the ETF instance, and `sec-*` refuses `--market` other than `etf`. |
| R9 | LOW | Test gaps. | Added: end-to-end review (pristine data), liquidation + restart, tampered snapshot, orphan sweep, full-instance replay. |

### 4.1c Final audit on head `e2d8ea1`

The independent audit agent was **interrupted by the API session limit** before it could report, so the final audit was done by the lead:

- Full suite: **402 tests OK**. `status_artifacts --check` is fresh (the canonical ETF replay is unchanged apart from the dataset and test counts) and `generate_schemas --check` is OK. V1 end-to-end demo: **35/35 checks passed**.
- Rolls: charged idempotently (op-id `ROLL-<strategy>-<symbol>-<date>`) on the decision snapshot, so a replay sees the same positions. The research charge (|w| x `roll_cost` at the exit bar) and the Desk charge (|qty| x price(t) x `roll_cost(t+1)`) describe the same economic event.
- Liquidation: any strategy with **no** capital entitlement (including one re-registered on the evaluation track) that still holds a **capital** sleeve is flattened before doing anything else. The RISK override only applies to it, and it leaves `actionable()` once it is flat.
- Committed ETF snapshots: their sidecars carry the right fingerprints (status check fresh), so the new check does not invalidate them.
- `pristine_after`: every lifecycle transition uses the filtered series, never the full one (tested). The full series is only reported as monitoring.
- Speed limit: it reads `cost_bps` and the volatility **for that date**, so it is causal. Without a cost, the contract is excluded (conservative).

### 4.1d Final independent audit (on `40e73ea`, after the quota reset)

The audit passed every item **except R2**, and it confirmed the figures in §3 for the narrow lane. Its summary: 402 tests OK, statuses fresh, and E1-E8, R3-R9 and A1-A4 PASS.

It found 4 new defects, all fixed in the next commit with a test for each (`FinalAuditTests`):

| # | Severity | Defect | Fix |
|---|---|---|---|
| F1 | MED | A strategy re-registered on the evaluation track kept trading on the **capital** ledger with no entitlement. | `liquidating()` now covers every strategy with no entitlement that holds a capital sleeve. It flattens first, then moves to the evaluation ledger. |
| F2 | MED (R2 FAIL) | A snapshot legitimately re-committed stayed INVALID forever, because the check compared against the fingerprint cached in `var/`. | `_revalidate` now re-reads the committed sidecar on disk. |
| F3 | LOW | A crash after the last liquidation fill but before the commit lost the ticket, because the plan never resumed once the sleeve was flat. | Every pending plan of the session is resumed, even for a strategy that is no longer actionable. `_apply` uses the **ledger recorded in the ticket**: a fresh lookup would have sent the replay to the evaluation ledger. |
| F4 | LOW-MED | In a staggered universe the survivors were levered up (N = the contracts that passed the filter). | N now counts the contracts listed and past warmup, **before** the speed limit, and the IDM is capped at √N. The broad lanes were re-evaluated and **6 extra trials charged**. The verdicts are unchanged (REJECT). |

Still open (documented): the Learning plane's FALSE/TRUE_REJECT verdict does not take `pristine_after` into account.

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
