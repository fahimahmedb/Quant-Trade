# Hyperliquid Forced-Liquidation Flow Persistence — measurement closure + frozen minimum test

Date: 2026-10-08
Branch: `sol/scout-crypto-20261008-1847`
Status: **READY_TO_RECORD_ON_A_COMPLIANT_NODE_HOST / NOT EXECUTED**

This continues the existing crypto mechanism scout. It does not reopen candidate search. No F1 outcome was opened, downloaded, computed or modified. No candidate return outcome was consumed while fixing the design below.

## 1. Measurement blocker — final resolution

### Public surfaces verified

| Surface | Verified structure / behavior | Use here |
|---|---|---|
| Market-wide fills | A Hyperliquid non-validating node with `--write-fills --batch-by-block` writes one JSONL envelope per block: `{local_time, block_time, block_number, events}`. Current `events` are pairs `[address, fill]`; the same execution is represented on both counterparties and shares the same `tid`. | **Authoritative event source.** Collapse by `(block_number, coin, tid)` before aggregation. |
| Liquidation marker | `WsFill` carries optional `liquidation = {liquidatedUser?, markPx, method}`, with `method ∈ {market, backstop}`. Public archived/current node-fill examples use the same API-fill shape. | `method=market` = forced order-book liquidation. `backstop` is forced but does not belong to the primary order-book pressure mechanism. |
| Trade direction | Hyperliquid API notation defines trade `side` as aggressor side; current node fills carry `crossed`, and paired fills expose one taker (`crossed=true`) for an ordinary/order-book execution. | Forced direction = taker side of a `method=market` liquidation execution. `B=forced buy` (short liquidated), `A=forced sell` (long liquidated). |
| Timestamps | Fill has `time` in ms. By-block envelope carries chain `block_time`, sequential `block_number`, and node `local_time`. | Event ordering uses fill time; **signal availability uses node `local_time`** so the replay cannot enter before the label was locally observable. |
| BBO | Public WS `bbo` sends BTC/ETH best bid/ask with exchange `time`, only when BBO changes on a block. | Executable entry/exit and stale-quote rejection. Recorder adds local receive time. |
| L2 | Public WS `l2Book` sends `levels=[bids,asks]` with exchange `time`. | Raw audit/context capture; not a tuned event feature. |
| Mark/mid | `activeAssetCtx` includes perp context including mark/mid; `allMids` also exists. | Raw diagnostic capture. Event trigger itself does not use future mark/mid. |
| Public trades | Public WS `trades` exposes `coin, side, px, sz, hash, time, tid, users`; it does **not** provide a global liquidation label. | Redundant live completeness/latency diagnostic only; not the liquidation classifier. |
| Historical fills | Official requester-pays S3 `hl-mainnet-node-data/node_fills_by_block`; older generations use `node_fills`/`node_trades`. | Replay / audit source after freeze. Not a low-latency production signal. |
| Historical L2 | Official requester-pays S3 `hyperliquid-archive/market_data/.../l2Book/...`; uploaded roughly monthly and explicitly may be missing. | Audit only. Prospective test records its own market context. |

Actual structure was checked against exposed archive rows/dataset examples, not documentation alone: current `node_fills_by_block` rows expose `events = [[address, fill], ...]` and paired maker/taker rows sharing `tid`.

### Classification

`LIQUIDATION_CLASSIFICATION = DETERMINISTIC`

A canonical execution is identified by `(block_number, coin, tid)`. Exact duplicate rows/blocks are folded. Paired rows must agree on price, size and fill time. For `liquidation.method == "market"`, the unique `crossed=true` row supplies forced side. A missing `liquidatedUser` does not prevent classification because the protocol marker plus taker side are sufficient. `backstop` and `dir == "Auto-Deleveraging"` are excluded from both forced-market flow and voluntary controls.

`POINT_IN_TIME = TRUE_WITH_LOCAL_AVAILABILITY_TIMESTAMP`

The signal time is not backdated to exchange execution time. For every 5-second bucket, availability is the later of bucket end and the maximum node `local_time` of included fills. Public market frames additionally store local `_recv_ns`; a quote received after decision time is unavailable by construction.

`REPLAYABLE = TRUE`

The raw node envelopes, raw WS frames, deterministic dedup keys and frozen parser define the replay. Conflicting duplicate block heights or any sequential block gap cause hard failure.

`COMPLETE_ENOUGH_FOR_RESEARCH = TRUE_IF_GAP_AUDIT_PASSES`

There is no promise that the public S3 archive is complete/timely, and public issue reports show that non-validating nodes can lag/restart and create gaps. Therefore completeness is an **observed invariant**, not an assumption: the primary run is invalid for any interval with a missing sequential block, conflicting rewind, or missing/stale BBO at required entry/exit. No silent interpolation.

## 2. Raw prospective capture — minimal schema

### A. Authoritative forced/voluntary flow

Run a mainnet non-validating node with at least:

```bash
hl-visor run-non-validator \
  --write-fills \
  --batch-by-block \
  --disable-output-file-buffering
```

Official node guidance currently recommends roughly 16 vCPU / 128 GB RAM / 500 GB SSD for a non-validator. The experiment harness does not weaken the test if the host is unavailable; it stays `NOT_READY_TO_EXECUTE` until such a host exists.

Raw unit retained byte-for-byte:

```text
node_fills_by_block JSONL line
  local_time: ISO timestamp on recorder/node host
  block_time: chain block timestamp
  block_number: sequential chain block number
  events: [[user_address, fill], ...]

fill required for BTC/ETH:
  coin, px, sz, side, time, hash, oid, tid, crossed, dir
  liquidation? { liquidatedUser?, markPx, method }
```

### B. Market context

`record_hl_public_ws.py` subscribes without account credentials to BTC and ETH:

- `trades`
- `bbo`
- `l2Book`
- `activeAssetCtx`

Every received JSON frame is stored raw with `_recv_ns = local receive time`. Session connects/disconnects are separately journaled. No trading action exists in the recorder.

## 3. Frozen minimum discriminating test — NO GRID SEARCH

Everything in this section is frozen before candidate outcome exposure.

### Universe

Exactly the main Hyperliquid perp markets `BTC` and `ETH`. One pooled primary statistic; no per-coin selection or replacement.

### Canonical trade and forced-flow definition

1. Collapse node fill rows by `(block_number, coin, tid)`.
2. Exact duplicate rows are folded.
3. Ordinary/order-book execution requires exactly one `crossed=true` row after dedup.
4. `liquidation.method == market` => forced-market execution.
5. `liquidation.method == backstop` => excluded from primary flow.
6. Any `dir == Auto-Deleveraging` => excluded from both forced and voluntary primary flow.
7. Notional = exact decimal `px × sz`.
8. Side sign: `B=+1`, `A=-1`.

### Bucket / event definition

- Non-overlapping **5-second exchange-time buckets**.
- Baseline liquidity/activity = arithmetic mean of **total aggressive notional** in the immediately preceding **60 buckets = 5 minutes**, using zero for a bucket with no trade.
- Forced gross = sum of market-liquidation notional in the bucket.
- Forced signed = forced buys minus forced sells.
- Directional purity = `abs(forced_signed) / forced_gross`.
- **Trigger** iff:
  - baseline > 0;
  - forced gross >= **1.00 ×** preceding-5-minute mean total aggressive notional;
  - directional purity >= **0.80**;
  - current BBO is available and no more than **2 seconds old** at decision availability time.
- `t0` = `max(bucket_end, latest node local_time among fills in trigger bucket)`.
- After a trigger, **60-second same-coin cooldown**. Any further qualifying bucket inside cooldown is part of the same cascade for dependence control and cannot create another event.

The 5-second aggregation is short relative to the protocol's 30-second partial-liquidation cooldown. The single 30-second outcome horizon below is mechanically tied to that documented cooldown rather than selected from returns.

### Forced-flow normalization

Primary event intensity:

```text
forced_norm = forced_signed_notional / preceding_5m_mean_total_aggressive_notional
```

No percentile, z-score, quantile or alternative threshold is inspected after recording starts.

### Voluntary aggressive-flow control

Each forced event gets at most one control, selected **only from the prior 24 hours**, same coin and same direction, without replacement. A control bucket must have zero forced-market liquidation notional and nonzero voluntary signed aggressive flow.

Hard calipers, frozen now:

- `abs(voluntary_norm / forced_norm)` in `[0.50, 2.00]`;
- pre-bucket 60-second realized absolute variation ratio vs event in `[0.50, 2.00]`;
- absolute difference in pre-bucket 60-second signed return <= event's pre-bucket realized absolute variation;
- valid <=2-second-old BBO at control decision time.

Among eligible controls choose the minimum deterministic score:

```text
|flow_ratio - 1|
+ |rv_ratio - 1|
+ |pre_return_control - pre_return_event| / pre_rv_event
```

Tie => earlier control bucket. Controls after the forced event are forbidden.

### ONE outcome horizon

Exactly **30 seconds after decision availability `t0`**. No 1s/5s/10s/60s alternatives are calculated for decision-making.

### Executable price / cost assumption

For the forced event and its control:

- long-direction entry = most recently **received** ask available by `t0`;
- long-direction exit = most recently **received** bid available by `t0+30s`;
- short-direction entry = available bid at `t0`;
- short-direction exit = available ask at `t0+30s`;
- either quote older than 2 seconds => pair unscorable;
- fixed taker fee = **5 bp per side**, i.e. **10 bp round trip**, deliberately above the current base Hyperliquid perp tier-0 taker fee of 4.5 bp; observed spread is already embedded via BBO prices.

No impact model is added at this screen because the question is whether the continuation exists at all at top-of-book size. Any later capacity study is a separate preregistered experiment.

### ONE primary statistic

For each matched pair:

```text
D_i = executable_net_return(forced event, same direction)
    - executable_net_return(matched voluntary control, same direction)
```

**Primary statistic = mean(D_i), pooled across BTC+ETH.**

Inference: t-statistic for the mean using a sandwich/cluster correction with **UTC calendar day as the cluster**. BTC and ETH cascades on the same day therefore do not count as independent days.

### Frozen KILL / KEEP / PROMOTE

No decision before at least **50 scored matched pairs** spanning at least **10 distinct UTC days**.

- `PROMOTE` iff all hold:
  1. mean paired difference >= **+5 bp**;
  2. mean absolute executable net return of forced events > 0;
  3. UTC-day-cluster t >= **2.0**;
  4. at least **60% of UTC-day mean paired differences are positive**.
- `KILL` iff minimum sample is met and UTC-day-cluster t <= **-1.645** for the paired difference.
- otherwise `KEEP`; before minimum sample => `KEEP_UNDERPOWERED`.

Promotion means only “worth a separately preregistered validation/capacity experiment”. It does not authorize capital or live trading.

## 4. Completeness / latency / publication gates

The run hard-fails or excludes the affected pair if any of the following occurs:

- missing sequential `block_number` in the complete node-fill capture;
- same block number replayed with conflicting block time/content;
- paired fill disagreement on time/price/size;
- no unique taker for a non-backstop trade;
- unknown liquidation method;
- recorder disconnect overlapping the information required for entry/exit;
- BBO absent or >2 seconds stale at event/control entry or exit.

Node `local_time - block_time` and WS `_recv_ns - exchange time` are recorded as publication-latency diagnostics. They cannot be used to choose a different event threshold or horizon.

## 5. Implementation persisted with this freeze

Directory:

`research/edge_search/scouts/hl_liquidation_v1/`

Files:

- `HL_LIQUIDATION_V1_FROZEN_SPEC_2026-10-08.md`
- `hl_liquidation_harness.py`
- `record_hl_public_ws.py`
- `test_hl_liquidation_harness.py`

Synthetic suite covers:

1. liquidation vs voluntary fill classification;
2. duplicate block/event folding;
3. out-of-order input timestamps with deterministic replay order;
4. missing L2/BBO rejection;
5. multiple forced fills aggregated once each after maker/taker collapse;
6. event/cascade clustering cooldown;
7. no use of quote information received after `t0`;
8. conflicting duplicate block fail-closed;
9. missing sequential block fail-closed;
10. ADL exclusion from voluntary controls.

Local result before push:

```text
python -m unittest -v
11 tests passed
python -m py_compile hl_liquidation_harness.py record_hl_public_ws.py
PASS
```

## 6. Readiness

`CANDIDATE_1_STATUS = MEASUREMENT_BLOCKER_RESOLVED`

`READY_TO_RECORD = TRUE_ON_COMPLIANT_NODE_HOST`

The code and frozen schema are sufficient to begin prospective raw capture once a mainnet non-validating node host is available and clock-synchronized.

`READY_TO_EXECUTE = FALSE_IN_CURRENT_ENVIRONMENT`

Reason: this agent environment is not a Hyperliquid node host and cannot satisfy the official non-validator resource/network requirements. Running only the public `trades` WebSocket would lose the global liquidation label and is explicitly forbidden as a substitute.

`NEXT_ACTION = provision/reuse one compliant Hyperliquid non-validating-node host; launch the frozen node flags + raw public-WS recorder; accumulate prospective BTC/ETH data; run the single frozen harness once the minimum sample is reached.`

## 7. Public verification basis

Primary/public references used for structure/mechanics only, not candidate outcomes:

- Hyperliquid Docs — WebSocket subscriptions/data types: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions
- Hyperliquid Docs — Historical data: https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data
- Hyperliquid Docs — L1 data schemas: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/nodes/l1-data-schemas
- Hyperliquid Docs — Liquidations: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations
- Hyperliquid Docs — Fees: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees
- Official node repository: https://github.com/hyperliquid-dex/node
- Public current-format archive examples/schema cross-check: QuickNode Hyperliquid Trades Dataset and public `hyperliquid-node-fills-by-block` dataset viewer. These were used only to validate field layout/pair structure, not returns.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
