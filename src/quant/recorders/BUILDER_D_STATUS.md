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
- JSON schemas and deterministic restart/storage/public-plan/proof tests;
- fail-closed `--proof` mode that requires the complete 14-source BTCUSDT+ETHUSDT public plan, fresh captures from the current proof run, HTTP 2xx, exact persisted raw SHA-256, parser version, endpoint provenance, UTC timestamps and monotonic timing;
- proof-mode fail-fast on the first network fetch error so a DNS/network outage cannot turn the required short run into a long sequence of repeated failures.

## Verification

The deterministic Builder D suite currently passes **17/17** targeted `test_forward_recorder_*` tests, including restart recovery, state-lag reconciliation, raw replay/deduplication, polling gaps, clock regression, HTTP/fetch errors, credential-header absence, proof rejection of stale captures, proof rejection of non-2xx responses, proof rejection of corrupted raw bytes and bounded fail-fast behavior.

## Hard boundaries

There is no API-key or credential loading, account/user endpoint, order endpoint, signal, return/P&L calculation, carry calculation, funding ranking/filter, trade decision, Book mutation or Capital Desk integration.

`src/quant/factory/**` and `src/quant/dataplane/sec_form4.py` are untouched. No trading/execution/live-account code is introduced.

## Live proof status

Direct public-network attempts from the available execution runtime fail DNS resolution for the configured Binance public hosts with `Temporary failure in name resolution`.

The exact proof path is fail-closed: on a fresh store it attempted one public source, captured zero responses, recorded one `fetch_error`, returned the durable state to `IDLE`, and reported `live_provenance_proof.proof == "FAIL"` with zero verified sources. No prior capture can satisfy a later failed proof run because every source must advance its durable sequence during that proof invocation.

Accordingly, the mandate's live-public-collection Definition of Done is **not** claimed as satisfied. Synthetic fixtures, web documentation, cached captures, or mocked responses are not substituted for this requirement.

Re-run from a network-enabled checkout with:

```bash
python3 scripts/record_forward_market.py --proof --root /tmp/quant-forward-proof
```

`SUBMITTED_FOR_RED_TEAM` is permitted only after that command completes with `live_provenance_proof.proof == "PASS"` on the exact candidate HEAD. No long-running collection should be enabled before Blue Team separately validates cost, retention, rate limits and applicable Terms of Service.
