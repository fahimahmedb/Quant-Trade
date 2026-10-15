# Quant-Trade Legacy Economic Research Inventory

Status: CHECKPOINT_1_RECOVERY_IN_PROGRESS

Reconciliation date: 2026-10-15
Base branch at branch creation: `research/edge-lab-continuous`
Mission: historical economic research reconciliation only.

## Governance invariants

- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- No new signal-to-future-return or PnL calculation is authorized or performed by this reconciliation.
- Historical result immutability applies. Missing historical facts are recorded as `UNKNOWN`, not reconstructed.
- Operational/readiness evidence is kept separate from economic evidence.

## Recovery surfaces already identified

1. Legacy autonomous-research memory (`research/memory.jsonl`, `research/opportunity_map.json`).
2. Weather V1/V2/V3/V4 branches, independent Astra re-audits, Owner decisions and Blue governance artifacts.
3. Edge Lab / V4.2 discovery experiments, result JSONs, prospective registrations and qualification artifacts.
4. SEC Form 4 census branches and historical workflow evidence.
5. Current paused-lane qualification records and mission-supplied Owner recovery facts.

## Preliminary recovered economic families

- NASDAQ short-horizon time-series reversal (legacy TSR-NDX-001).
- Weather-forward/weather-linked mechanism family (V1/V2/V3/V4 lineage).
- SEC Form 4 insider-purchase clustering / EOD research family.
- CFE VIX term-premium / futures-curve expression.
- Treasury 5Y auction concession and ZF auction-pressure variants.
- France OAT/Bund fiscal/political spread repricing.
- Binance extreme-funding reversal.
- Crypto book-pressure prospective experiment.
- CFTC ES leveraged-funds sentiment extremes.
- Month-end pension rebalance SPY/TLT.
- Sector-relative ETF shock reversal.
- Stock/bond joint-stress rebound.
- Russell deletion calendar basket.
- Corporate-action prospective protocol families (CEF rights/DRIP, ETF liquidation, odd-lot priority, reverse-split cash-in-lieu/round-up, SPAC redemption floor).
- Policy-announcement repricing, Hyperliquid forced-flow and F2 lanes (status reconciliation pending exact provenance binding).
- MLB/soccer/weather replication and Box Office families (repository archaeology pending; mission input says prior results existed, but no result will be recreated if artifacts cannot be recovered).

## Confirmed immutability examples

- `research/memory.jsonl`: TSR-NDX-001 was historically `REJECT_RESEARCH`; do not retest the same fixed expression merely because a later framework is cleaner.
- `disc-sector-relative-shock-reversal-l1-v1.result.json`: `KILL_EXPRESSION`, not a family-wide kill.
- `disc-stockbond-joint-stress-rebound-l1-v1.result.json`: `KILL_EXPRESSION`, not a family-wide kill.
- `disc-market-sentiment-cftc-es-leveraged-extremes-l1-v1.result.json`: `PARK_DATA`; economics never opened.
- `disc-monthend-pension-rebalance-spytlt-l1-v1.result.json`: `PARK_DATA`; frozen adequacy gate failed and economics were not computed.
- `disc-treasury-5y-auction-concession-l1-v1.result.json` and `disc-zf-auction-pressure-daily-l1-v1.result.json`: `PARK_DATA`; source adequacy failure is not an economic rejection. Outcome exposure, where recorded, is retained in trial/pristine accounting.
- `disc-france-oat-bund-l1-v0.result.json` and `disc-france-oat-bund-l1-v1-public-daily-route.result.json`: `PARK_DATA`; no broader France thesis is killed.
- CFE reader repair may be `PROMOTE_EXPRESSION` without constituting a new economic test or `EDGE_VALIDATED` result.

This file will be replaced by the final auditable inventory after ancestry, duplicate, trial and evidence reconciliation are complete.
