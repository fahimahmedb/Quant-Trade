# Builder D — Passive Forward Data Recorder

Status: **BLOCKED_EXTERNAL_LIVE_PROOF**

Base SHA: `37f298423ca4a100c1c633da2c3c6c2641d8dd8e`

Branch: `builder/forward-market-recorder-v2`

## Delivered

- generic restart-safe passive recorder under `src/quant/recorders/**`;
- public, credential-free Binance market-data plan for BTCUSDT and ETHUSDT Spot + USD-M perpetual;
- exact raw-response byte persistence with SHA-256 content addressing;
- source endpoint, UTC retrieval times, monotonic timings, parser version and HTTP provenance;
- instrument status, depth, funding/mark information and funding-history capture endpoints where publicly available;
- durable `RUN` / `IDLE` state, replay-safe raw storage, state reconciliation after interrupted writes;
- polling-gap, source clock-skew, UTC-clock-regression, HTTP/fetch-error and unclean-restart ledger;
- atomic fsync + rename persistence;
- documented UTC/source rotation and deliberately no automatic retention deletion;
- one-shot CLI only; no daemon/scheduler or long automatic collection;
- JSON schemas and deterministic restart/storage/public-plan tests;
- fail-closed `--proof` mode that succeeds only when the complete public plan has been captured with HTTP 2xx and every persisted raw SHA/provenance field verifies.

## Hard boundaries

There is no API-key or credential loading, account/user endpoint, order endpoint, signal, return/P&L calculation, carry calculation, funding ranking/filter, trade decision, Book mutation or Capital Desk integration.

`src/quant/factory/**` and `src/quant/dataplane/sec_form4.py` are untouched. No trading/execution/live-account code is introduced.

## Live proof status

A real short public run was attempted from the available execution runtime. DNS resolution failed for both configured public Binance hosts with `Temporary failure in name resolution`. The recorder correctly ledgered the fetch failures and returned to `IDLE`, but no public response bytes were captured.

Accordingly, the mandate's live-public-collection Definition of Done is **not** claimed as satisfied. Synthetic fixtures, web documentation, or mocked responses are not substituted for this requirement.

Re-run from a network-enabled checkout with:

```bash
python3 scripts/record_forward_market.py --proof --root /tmp/quant-forward-proof
```

`SUBMITTED_FOR_RED_TEAM` is permitted only after that command completes with `live_provenance_proof.proof == "PASS"` on the exact candidate HEAD. No long-running collection should be enabled before Blue Team separately validates cost, retention, rate limits and applicable Terms of Service.
