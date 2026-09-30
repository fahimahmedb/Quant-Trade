# SETTLEMENT LIQUIDITY S2 — 30-day falsification — STATE / CHECKPOINT

REAL_CAPITAL_AUTHORIZED = FALSE. Research only. No orders, no live trading, no capital.

This file is the **resume surface**. A new session (after a token/context cut) must read this file
first, then `PROTOCOL_PREDECLARED_2026-09-29.md`, then resume at the first step that is not `DONE`.
Update this file and push at every checkpoint (`CKPT-n` below).

## Identity

- Branch (harness-assigned, the only branch used): `claude/hopeful-dirac-4ahy2z`
- Base: `09ba64b` (blue governance head at session start)
- Inputs read: `QUANT_NORTH_STAR.md`; A5 `claude/hopeful-hamilton-81rab1@85483fb9f85c6beea36e0af969e3f0a3e939e07f`
  (`research/recus_2026-09/agent5_structural_fragmentation.md`, `agent5_structural_etat.md`);
  A7 `claude/exciting-planck-uq6rir@10c025dca8bb082c5c9c8e012a427a90189bc5fd`
  (`research/recus_2026-09/agent7_edge_archaeology_decay.md`, M5 scripts).
- Required deliverables (this directory):
  - `SETTLEMENT_LIQUIDITY_30D_FALSIFICATION_2026-09-30.md` (report)
  - `SETTLEMENT_LIQUIDITY_STATE_2026-09-30.md` (this file)
  - `scripts/` + `data/` sufficient to reproduce cohort, T_DETERMINED, fills, losses, queue model, result.

## Terminal state

```text
SETTLEMENT_LIQUIDITY_S2 = PENDING   (one of: SURVIVES_FALSIFICATION | REJECTED_NET | REJECTED_FILL_ACCESS |
                                     REJECTED_BOTH | INDETERMINATE_DETERMINATION | INDETERMINATE_QUEUE)
```

## Resume procedure (after any cut)

```bash
cd /home/user/Quant-Trade            # or a fresh clone
git fetch origin claude/hopeful-dirac-4ahy2z && git checkout claude/hopeful-dirac-4ahy2z
git pull origin claude/hopeful-dirac-4ahy2z
cat research/settlement_liquidity/SETTLEMENT_LIQUIDITY_STATE_2026-09-30.md
cd research/settlement_liquidity/scripts
# re-run only steps not DONE; every step is idempotent and skips cached work in data/raw/
```

`data/raw/` is gitignored (large API caches, lost when the container is reclaimed). Every step writes
its compact committed output to `data/` so later steps can resume from git alone; a lost `data/raw/`
only costs re-fetch time (all APIs are public and free).

## Step plan and status

| Step | Script | Output (committed) | Status |
|---|---|---|---|
| S0 | orientation, source probes | this file | DONE (CKPT-0) |
| S1 | `s01_enumerate_markets.py 2026-08-30 2026-09-29 markets_primary` (resumable) | `data/raw/markets_primary.jsonl.gz` (41 MB, not committed) | DONE: 115,574 markets |
| S2 | `s02_classify.py markets_primary` (outcome-blind) | `data/cohort_primary.csv.gz` (all markets + payout/fee/tick fields; self-sufficient for S6) | DONE: 79,589 kept; E1 31,466; E2 4,519 |
| S3 | freeze protocol (before any economics) | `PROTOCOL_PREDECLARED_2026-09-29.md` | DONE (CKPT-1) |
| S4a | `s04a_mlb.py 2026-08-29 2026-09-28` | `data/mlb_games.csv.gz` | DONE: 404 games |
| S4b | `s04b_espn.py markets_primary 2026-08-28 2026-09-29` | `data/espn_events_primary.csv.gz`, `data/pm_espn_map_primary.csv.gz` | DONE: 6,609 PM events → 2,382 ESPN events (1,238 with terminal wallclock) |
| S4c | `s04c_weather.py markets_primary 2026-08-27 2026-10-01` | `data/weather_determination_primary.csv.gz` | DONE: 10,643 / 12,221 verified |
| S4d | `s04d_assemble.py markets_primary` | `data/determination_primary.csv.gz` | DONE (CKPT-2): 36,991 VERIFIED, 36,074 with non-empty window; 42,598 UNVERIFIABLE |
| S5 | `s05_fetch_trades.py primary 14 7200` (resumable per market) | `data/raw/trades/<cid>.json.gz` (not committed; compact extracts in S6) | DONE: 36,087 markets, 0 errors |
| S6 | `s06_accounting.py primary 60` | `data/fills_primary.csv.gz`, `data/fills_contrast_primary.csv.gz`, `data/newcomer_inputs_primary.jsonl.gz`, `data/accounting_summary_primary.json` | DONE (CKPT-4) |
| S7 | `s07_newcomer.py primary` (variants P / S1 / S2) | `data/newcomer_results_primary.json` | DONE (CKPT-4); re-run after S8b if live timed sample >= 20 |
| S8 | `s08_live_queue_monitor.py 30` (read-only, detached; restarted 00:31Z 2026-09-30 with game-start filter fix) | `data/raw/live/*.jsonl` (not committed) → `s08b_live_summary.py` → `data/live_queue_summary.json`, `data/live_queue_markets.csv.gz` | RUNNING. After any worker restart: `cd scripts && (setsid nohup python3 s08_live_queue_monitor.py 30 >> /tmp/claude-0/live_monitor.log 2>&1 < /dev/null &)` — it resumes from finals.jsonl. Needs >= 20 timed post-final markets (UCL + MLB Wild Card 2026-09-30) |
| S9 | decay / weekly | in report | TODO |
| S10 | report + terminal state + push + verify remote HEAD | both deliverables | TODO |

Validation of T_DET (independent source vs Polymarket venue `finishedTimestamp`): source precedes venue by a
median 62–102 s across MLB, NFL/NCAAF, soccer, WNBA, NHL; 5–95% range within about −8.8 to +1 min.

## Established facts (verified this session, 2026-09-29)

- gamma `/markets/keyset?closed=true&order=closedTime&ascending=false&volume_num_min=1000` pages all closed
  markets by close time (offset pagination is capped at 10,000). ≈ 4,500–5,000 markets/day have volume ≥ 1 k$.
- gamma market fields used: `closedTime` (= resolution/close; used as T_RESOLUTION), `umaResolutionStatuses`
  (full proposal/dispute history, e.g. `["proposed","disputed",...,"resolved"]` → dispute detector),
  `outcomePrices` (final payout vector), `sportsMarketType`, `line`, `gameStartTime`, `feeSchedule`
  (sports: taker-only rate 0.05 × p(1−p); makers pay 0).
- gamma sports events carry `finishedTimestamp`, `score`, `gameId` (venue data feed; NOT used as primary
  authority — only as a cross-check / secondary cohort).
- data-api `/trades?market=<conditionId>`: `takerOnly=true` (default) returns taker records only;
  `takerOnly=false` adds maker records in FIFO order inside each tx (e.g. taker SELL 2,150 @0.999 matched
  maker BUY 2,130 then 20). Maker/taker split = set difference. Max offset 10,000, limit 1,000.
- Independent authoritative timestamp sources, all public:
  - MLB: `statsapi.mlb.com/api/v1.1/game/{gamePk}/feed/live` → last play `about.endTime`, `metaData.gameEvents`
    contains `game_finished`. Example TEX@ARI 2026-09-12: final out 03:05:14.7Z; Polymarket finishedTimestamp
    03:06:06.8Z; market closedTime 03:22:58Z → settlement window ≈ 18 min.
  - ESPN `site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event=` → NFL/NCAAF terminal play
    "End of Game" with `wallclock`; soccer `keyEvents` "End Regular Time" with `wallclock`.
  - NWS CLI climate reports with issuance time: IEM AFOS archive `mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=CLINYC`.
- Goldsky orderbook subgraph is deprecated (stale) → not used.
- No public historical L2 order book exists → exact FIFO queue reconstruction is impossible historically;
  a partial-identification bound is required (design in protocol). Identified lower bound: any
  determined-side trade at winning-equivalent price ≤ 0.998 after placement implies the 0.999 bid level was
  empty at that instant (price priority), so a resting newcomer bid would have been first in queue.

## Operational notes

- ESPN returns 403 to browser-like User-Agents from this host; `common.get` uses `Python-urllib/3.12` for espn.com.
- IEM ASOS endpoint intermittently answers "server over capacity"; retry.
- ESPN lower-tier soccer summaries lack timestamped terminal events → UNVERIFIABLE by protocol.
- Weather markets: 5.7k/6.1k resolve on NOAA `weather.gov/wrh/timeseries?site=<ICAO>` (METAR), whole degrees.


## Protocol deviations (disclosed; generic rules, no per-market overrides)

Found by checking source-derived side vs final payout over all 28,967 source-determined markets (classifier QA,
before any fill/P&L of the window was used in a decision). As-frozen output kept as
`data/determination_primary_asfrozen.csv.gz` (35 mismatches); corrected output `data/determination_primary.csv.gz`.

- D1 (MLB matcher): doubleheaders — statsapi lists game 2 at a placeholder start (e.g. 20:10Z); ties in team
  similarity are now broken by the closest scheduled start. Fixed 8 mismatches (BAL@NYY 2026-09-25).
- D2 (team → outcome mapper): mapping must be unique and one-to-one (e.g. "Utah" vs "Utah State",
  "New York City FC" vs "New York Red Bulls", "Real Madrid" vs "Rayo Vallecano de Madrid"); ambiguous → no source
  side (newcomer then falls back to consensus per protocol). Fixed 6 mismatches.
- Residual 21 mismatches / 28,889 (0.073%) are genuine classifier risk and stay in: 18 weather (METAR proxy vs
  NOAA timeseries, mostly daily lows), 3 NHL preseason (MTL–OTT, MTL–TOR; 2 of them disputed on Polymarket).
- Planned sensitivity S1 (not the protocol rule): newcomer bids only when source side == market consensus at t_p.
- S8 monitor: first launch's closed-market check lacked `closed=true` (gamma hides closed markets by default);
  patched and restarted 23:50Z; snapshots before the patch remain valid.

## Findings so far (CKPT-4, 2026-09-30 ~00:35Z)

- Rule 1 (all BUY fills >= 0.998 in [T_DET, T_RES), primary cohort): 119,737 fills, 13,371 markets, 55.62 M$ notional,
  net **+55,810 $ = +0.1003%** (market-cluster 95% CI 0.1002–0.1005%); **6 losing fills / 3 markets, −27 $**
  (Denmark starting-XI flipped after 2 disputes; MLB strikeout prop voided 50/50 after disputes); median lock 0.42 h;
  maker share 97.4% of notional; 3,658 distinct buyers; 9 disputed markets with fills.
  Contrast [T_DET−2h, T_DET): +0.063% with 30 losing fills / 14 markets (−13.6 k$), CI includes 0.
- Newcomer (S100 reference, frozen side rule P): LB fill share 3.23%, CENTRAL 22.9%, UB 26.8%; P&L negative in
  every model (23 losing markets: 15 weather METAR-proxy vs NOAA, 3 contested NHL preseason, 5 stale-consensus).
  Capital sims: ruin (−100%) at every capital level/model. Adverse selection: right side → back of queue; wrong
  side → filled 100%.
- Sensitivity S1 (source ∧ consensus agree; 14,157 markets): LB 3.15% / CENTRAL 35.1% / UB 40.5%; EUR 1k per 30 d:
  LB +9.8, CENTRAL +96, UB +118; EUR 5k: +28 / +256 / +381.
- Protocol state pending live calibration: rule 1 passes; LB < 5% <= UB → INDETERMINATE_QUEUE unless live
  conservative on >= 20 timed markets < 5% (→ REJECTED_FILL_ACCESS).

## Checkpoint log

- CKPT-0 (2026-09-29 ~22:50Z): orientation, source probes, scripts `common.py`, `s01_enumerate_markets.py`.
- CKPT-1 (2026-09-29 ~23:25Z): protocol frozen before economics; MLB timeline; ESPN verifier code; classifier.
- CKPT-2 (2026-09-29 ~23:50Z): full cohort, all verifiers, per-market T_DET assembled; S5 trade fetch and S8 live monitor running.
  If cut here: re-run `s05_fetch_trades.py primary 14 7200` (needs only committed `data/determination_primary.csv.gz`), then S6.
- CKPT-4 (2026-09-30 ~00:35Z): S5 done, S6/S7 results committed; S8 monitor restarted (30 h). Next: S8b when >= 20 timed markets, S7 re-run, report.
