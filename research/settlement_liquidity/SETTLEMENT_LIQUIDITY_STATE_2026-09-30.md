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
| S1 | `s01_enumerate_markets.py 2026-08-30 2026-09-29 markets_primary` | `data/raw/markets_primary.jsonl.gz` → compact cohort in S2 | RUNNING |
| S2 | metadata survey + exclusion/category classifier (outcome-blind) | `data/cohort_primary.csv.gz` | TODO |
| S3 | freeze protocol (before any economics) | `PROTOCOL_PREDECLARED_2026-09-29.md` | TODO (CKPT-1) |
| S4 | T_DETERMINED verifiers (MLB statsapi, ESPN wallclock, NWS CLI) | `data/determination_primary.csv.gz` | TODO (CKPT-2) |
| S5 | trade fetch (data-api, takerOnly true+false → maker/taker split) | `data/window_trades_primary.jsonl.gz` | TODO (CKPT-3) |
| S6 | fill accounting (all ≥0.998 buys in [T_DET, T_RES), losers kept) | `data/fills_primary.csv.gz`, summary json | TODO (CKPT-4) |
| S7 | newcomer queue model (LB / central / UB) + capital sims €100/500/1k/5k | `data/newcomer_*.json` | TODO (CKPT-5) |
| S8 | live book shadow monitor (queue depth at 0.999 on post-final markets, read-only) | `data/live_queue_*.jsonl.gz` | TODO (optional, CKPT-6) |
| S9 | decay / multi-window (weekly within 30d; optional 2nd 30d window) | in report | TODO |
| S10 | report + terminal state + push + verify remote HEAD | both deliverables | TODO (CKPT-final) |

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

## Findings so far

None economic yet (protocol not frozen; no fills evaluated).

## Checkpoint log

- CKPT-0 (2026-09-29 ~22:50Z): orientation, source probes, scripts `common.py`, `s01_enumerate_markets.py`.
