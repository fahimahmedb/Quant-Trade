# F2 — KALSHI-FLB-OOS-001 — pre-registration and acquisition manifest

Status: **PROPOSED**, published before any market, trade, candle or settlement record is read. Execution is blocked until (a) Codex's challenge window (`ATTENTE[EB2]`, 2026-10-08T16:30Z, plus one reminder) closes, (b) the Kalshi API/market-data terms are read and cleared (`ACQUISITION_TERMS_NOTES_2026-10-08.md`), (c) the harness is separately published, tested, adversarially reviewed and frozen. Paper/shadow research only; no order, account, key or capital.

Authority: Owner chat decision (`Q30_OWNER_DECISION_2026-10-08.md`); PR #22 comment `6061968640`; thresholds per `EDGE_SEARCH_BOARD_CLAUDE_ERRATUM_1_2026-10-08.md`.

## 1. Hypothesis and economic reason

H1: on Kalshi binary contracts, **buying the side priced at least 0.80 at the executable ask, 24 hours before scheduled close, and holding to settlement** earns a positive mean **net** return per dollar at risk after the taker fee, in a window after the published sample.

Reason: takers over-weight small probabilities and pay for immediacy; longshot sellers must lock about 0.90 or more of collateral for a few cents (Bürgi-Deng-Whelan, "Makers and Takers: The Economics of the Kalshi Prediction Market", 46,282 contracts and 12,403 events to April 2025; contracts at or below 10c lose over 60% post-fee for takers; small but significant gains for contracts above 70c). The anomaly is published and decayed in 2025, so the post-cutoff window is the test.

Null: mean net return per contract ≤ 0 on the primary universe.

## 2. Source, endpoints and terms

| Item | Value |
|---|---|
| Base | `https://api.elections.kalshi.com/trade-api/v2` (answered HTTP 200 unauthenticated on 2026-10-08 for `/exchange/status` and `/historical/cutoff`); documentation also lists `https://external-api.kalshi.com/trade-api/v2` |
| Cutoff | `GET /historical/cutoff` (2026-10-08: `market_settled_ts` = 2026-08-09T00:00:00Z) |
| Markets | `GET /historical/markets` (cursor pagination, same filters as live) for markets settled before the cutoff |
| Candles | `GET /historical/markets/{ticker}/candlesticks?start_ts&end_ts&period_interval=60` (fields `end_period_ts`, `yes_bid{open,low,high,close}`, `yes_ask{…}`, `price{…}`, `volume`, `open_interest`; FixedPointDollars strings) |
| Series category | `GET /series/{series_ticker}` (field `category`), resolved through the market's `event_ticker` |
| Terms | **Not yet read** (rulebook returned HTTP 429). Cleared before any acquisition. If registration, key or account is required, F2 is re-routed and no workaround attempted |
| User-Agent / rate | `quant-research-paper-shadow/0.1`, at most 5 requests per second, sequential, backoff on 429 |
| Storage | Raw JSON is hashed and stored outside git; the repository keeps manifests, hashes, counts and derived statistics |

Market-object field names to use (per docs): `ticker`, `event_ticker`, `status`, `result`, `close_time`, `open_time`, `settlement_ts`, `volume_fp`, `market_type`. The historical endpoints' exact schema is confirmed at manifest time; any difference is recorded in the manifest, not silently adapted.

## 3. Window (fixed now, before any record is read)

Markets with `settlement_ts` in **[2025-05-01T00:00:00Z, 2026-07-31T23:59:59Z]** (after the paper's April 2025 cutoff, before the 2026-08-09 historical cutoff). The whole window is sealed and read once. There is no discovery split: the published paper is the discovery.

## 4. Universe filters (all fixed, none depends on an outcome)

1. `market_type` = binary; combo/multivariate (MVE) markets excluded.
2. `close_time − open_time` ≥ 24 h (the paper's rule; removes hourly resets), using the creation-time schedule fields, not early-close edits.
3. Final `volume_fp` ≥ 1,000 contracts (approximation of the paper's $1,000 volume; stated, not tuned).
4. Series `category` known. Primary universe: category ≠ `Sports`. Sports is reported, not gating. Unresolved categories are excluded and counted.
5. Signal candle exists: a 60-minute candle whose `end_period_ts` lies in (T−25 h, T−24 h], where T = scheduled `close_time`. Else the market is skipped and counted (availability does not depend on the outcome).
6. At the signal candle: spread `yes_ask.close − yes_bid.close` ≤ 0.20, and both close fields present.
7. `result` in {yes, no}; voided/scalar/empty results excluded and counted.

## 5. Rule

At the signal candle: `ask_yes = yes_ask.close`, `ask_no = 1 − yes_bid.close`. Buy YES if `ask_yes ≥ 0.80`; buy NO if `ask_no ≥ 0.80`; if both qualify (crossed book) skip. One contract per market. Hold to settlement. The 0.80 threshold, the T−24 h time and the filters are fixed; no grid.

Net return per contract: `(payoff − ask − fee) / (ask + fee)`, payoff = 1 if the bought side wins else 0.
- Fee: the taker fee schedule published by Kalshi at manifest time, recorded with its source and retrieval time **before** any outcome is read. Fallback (documented in the paper): `ceil_to_cent(0.07 × P × (1 − P))` for one contract at price P, which is conservative because rounding is applied per contract. Stress: +0.01 per contract.
- Maker fills are not simulated (queue position and adverse selection are unobservable). Capacity, collateral lock-up and net return per capital-day are reported, not gating.

## 6. Statistic, gate and rejection rules

- Unit of analysis: **event** (average of the contract returns within an event), then clusters by UTC calendar date of `close_time` (standard errors robust to same-day dependence). Statistic: mean net return per contract, one-sided t.
- **Gate (family threshold, fixed):** `CONFIRMED` iff one-sided `t ≥ 2.128` (m = 1, α_family = 0.05/3; `ERRATUM_1`) **and** the stress mean is > 0 **and** at least half of calendar months in the window have a positive mean **and** the number of date clusters is at least 250.
- Target effect for exclusion: +1.0% net mean per contract. Power statement (ASSUMED sd, to be replaced by the measured sd in the report): with a per-event sd of about 0.20, detecting +1% at t = 2.128 requires about (2.128·0.20/0.01)² ≈ 1,800 independent clusters; +2.5% requires about 290.
- `REJECTED` iff not confirmed **and** the one-sided 95% upper bound `mean + 1.645·se` < +1.0% **and** the date-cluster count is at least 250.
- Otherwise `INCONCLUSIVE_UNDERPOWERED`. No re-test at a laxer threshold; no other cut.
- Non-gating reports: Sports; per-category; price buckets (0.80–0.90, 0.90–0.95, 0.95–1.00); the mirror longshot (ask ≤ 0.20) side; by month; maximum drawdown of a one-contract-per-market equal-capital simulation; fee share of gross P&L.

## 7. Acquisition and integrity requirements

1. The candidate market list (tickers, close/settle times, hash) is the first acquisition; the harness records every request's URL, UTC time, status, byte count and sha256, plus cursor chains.
2. If projected acquisition exceeds 12 hours at 5 requests per second, a deterministic subsample is used: keep tickers whose `sha256(ticker)` first byte is < 0x80 (about 50%), applied before reading any candle or result. The decision is made from the market-list size only.
3. The harness reads only manifest files; result directory pre-created; result written once (`x` mode); filesystem snapshots; late-mutation invalidation; `sys.dont_write_bytecode`; frozen dependencies; no network in the analysis stage.
4. Adversarial review of the harness by an agent independent of its author before the single execution.
5. `RESULT → LESSON → PRIORITY UPDATE → NEXT ACTION` is recorded in the work queue for every outcome, including a null.

## 8. Known limits (disclosed)

Hourly candles give a close of the signal hour, not the book at an exact instant; last-price effects are avoided by using bid/ask closes, but a close may lag the hour's final quote. Order-book depth is not available, so size and slippage are not modelled. Many contracts in one event or on one day are correlated, which is why clustering is by date. The anomaly is public; decay is expected. A positive result is a screen for shadow follow-up, not authority for the Book.
