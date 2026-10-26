# Passive Forward Market Recorder V2

This package is a Data Plane recorder, not a signal engine. It performs bounded, credential-free public GET captures and persists the exact raw response bytes with provenance.

## Initial public source

The initial plan targets `BTCUSDT` and `ETHUSDT` on Binance Spot and USD-M perpetual market-data endpoints only. Spot uses the market-data-only `data-api.binance.vision` host. USD-M uses public `/fapi/v1` market-data endpoints for exchange status, depth, mark/funding information and funding history.

No API key, account endpoint, order endpoint, websocket user stream, private header, signature, P&L, carry, ranking, return, funding filter, or trading decision exists in this package.

## Durability and layout

A root directory contains:

- `raw/<source_id>/<sha256>.bin`: exact content-addressed response bytes;
- `captures/YYYY-MM-DD/<source_id>/<capture_id>.json`: provenance and timing metadata;
- `gaps/YYYY-MM-DD/<source_id>/<gap_id>.json`: polling-gap, clock-skew, UTC-regression, fetch-error and unclean-restart ledger;
- `state/recorder_state.json`: atomic restart state and per-source cursor.

Raw bytes are de-duplicated by SHA-256. Metadata/state/gaps use temp-file + fsync + atomic rename. On startup, the state cursor is reconciled from already committed capture metadata so an interruption between capture persistence and state persistence cannot silently replay the sequence. The recorder returns to `IDLE` in `finally` and does not import or write the Book or Capital Desk.

## Rotation / retention / ToS gate

Rotation is directory-only by UTC date and source. **No automatic deletion/pruning exists.** Retention is therefore indefinite by default so irreplaceable forward bytes are not silently discarded.

Long-running or scheduled collection is intentionally not implemented. Before any daemon/scheduler is added, Blue Team must explicitly validate expected storage/network cost, retention policy, rate limits and applicable Terms of Service. The shipped CLI is one-shot only.
