# EDGE SEARCH BOARD — independent Codex shortlist

Date: 2026-10-08. Status: `PREREGISTERED_NO_OUTCOME_DATA_ACQUIRED`.

## 1. Scope and controls

This is Codex's independent ranking, produced before convergence with the Builder's list. The Owner's priority reset controls: search for economically meaningful edge first; keep A2 and the cost diagnostic parked unless their result can change an edge decision. Public documentation, papers and dataset specifications were inspected; no outcome series was downloaded or read.

Every candidate is a research hypothesis, not a strategy or current opportunity. Acquisition requires a separately named source and immutable manifest. No item authorizes live trading, Book mutation, credentials, paid access, or capital.

## 2. Ranked board

| Rank | Family | Hypothesis / economic mechanism | Prior evidence for / against | Status | Smallest public data required (not acquired) | Cheapest falsification test | Main risks | Expected information gain | Effort |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | Crypto perpetual funding reversal | Extreme cross-sectional funding reflects crowded leveraged positioning; after the funding timestamp, the expensive side should underperform after funding, fees and slippage. Limits-to-arbitrage and liquidation risk can sustain the premium. | Venue documentation establishes timestamped funding and mark/index prices; crowded-trade reversal is plausible. Against: funding may compensate genuine directional risk, and public anomalies are crowded. | NEW | Binance USD-M: funding history, mark/index prices and 1-minute klines for BTCUSDT, ETHUSDT and the eight next-largest continuously listed USDT perpetuals; exact endpoint/date cut to be named by Owner. | Freeze 2021-01-01–2025-12-31; rank funding at each common settlement; long bottom decile/short top decile for one interval; compare net return with funding included against same-sign carry and zero. | Delistings, changing intervals/caps, survivorship, liquidation, look-ahead at settlement, venue-specific fills, many thresholds. | High: rejects or supports a mechanism in one compact venue-native panel. | Medium |
| 2 | Weather forecast revisions → natural-gas repricing | Changes in population-weighted heating/cooling-degree forecasts alter expected demand before slower participants fully reprice gas; revisions, not realized weather levels, are the causal information event. | NOAA documents archived GEFS forecast cycles and ensembles; EIA documents storage fundamentals. Against: forecast upgrades create regime breaks; gas is highly efficient and storage/supply shocks confound the relation. | MODIFIED / WEATHER RESURRECTION | NOAA GEFS archived forecast vintages (2 m temperature, issue time retained); EIA working-gas releases; a separately named executable gas proxy with causal prices. Minimal mechanism screen needs NOAA vintages plus Henry Hub daily prices; tradability requires named futures/ETF data. | For winter only, compute fixed-region HDD revision from 00Z to 12Z using weights frozen before outcomes; regress/sign-test next executable return after availability, controlling storage-release days; reject if sign is unstable or net proxy return is nonpositive. | Vintage leakage, model-version changes, spatial-weight tuning, release timing, overlapping horizons, nontradable spot proxy, weather-season selection. | High: directly decides whether weather information deserves renewed A2 work. | High |
| 3 | Filing-timestamp PEAD under limited attention | Large standardized earnings surprises disclosed when attention/liquidity is low should diffuse more slowly, producing post-acceptance drift net of factors and costs. | SEC exposes acceptance timestamps and point-in-time filings/XBRL. PEAD has extensive prior literature. Against: well known/crowded; XBRL amendments and delayed price data can introduce leakage. | MODIFIED | SEC submissions and companyfacts archives with acceptance timestamps; CRSP-equivalent public daily/open prices would be required, or a precisely named public price source and survivorship-complete universe. | Freeze one fiscal-quarter cohort; compute surprise only from facts accepted by time `t`; enter next open after acceptance (or second next open after after-hours); double-sort surprise × low-attention proxy; reject on factor-adjusted, costed holdout. | XBRL restatements, filing/publication timestamp mismatch, survivorship, microcaps, corporate actions, factor exposure, multiple definitions of surprise/attention. | High but acquisition/provenance burden is high. | High |
| 4 | Post-EIA storage-release gas underreaction | A storage surprise relative to a fixed public baseline may be incorporated over hours rather than instantly during liquidity or weather regimes. | Scheduled EIA releases are timestamped and economically linked to inventories. Against: consensus expectations are not freely archived; using actual-minus-seasonal without expectations weakens the mechanism. | NEW | EIA vintage release values/times plus named intraday gas futures; optionally a public, frozen expectation proxy. | Event study with one fixed surprise definition and 5/30/120-minute windows; reject if post-release move disappears after spread/slippage or reverses across seasons. | Timestamp alignment, unavailable consensus, event-day confounds, futures rolls, bid/ask bounce. | Medium-high. | Medium-high |
| 5 | ETF close/open liquidity pressure reversal | Predictable close imbalance and creation/redemption pressure can overshoot the close and reverse overnight or next morning. | Institutional close auctions and ETF flows create mechanical demand. Against: imbalance feeds may be proprietary; existing local panel has no point-in-time imbalance/flow. | NEW | Official exchange auction-imbalance messages or a named public proxy; ETF shares-outstanding/flow vintage; minute trades/quotes. | One ETF, fixed imbalance extreme, next-open reversal net of auction/market spread; reject if only close-to-close beta remains. | Data accessibility, publication latency, selection of proxy, corporate actions, capacity. | Medium. | High |
| 6 | Prediction-market cross-venue consistency | Contracts resolving the same event can temporarily violate logical/probability bounds across venues because capital and settlement rules are fragmented. | Contract specifications and order books make constraints testable. Against: superficially identical contracts often differ in resolution and fees; access/history may be incomplete. | NEW | Named public venue contract specs, timestamped order books/trades, fees and resolution rules for one matched event set. | Hand-match ten contracts before prices; test executable bound violations after fees with synchronous quotes; reject if all gaps are explained by wording or latency. | Contract semantic mismatch, sparse depth, API history, jurisdiction, inability to execute both legs. | Medium-high. | Medium |
| 7 | Overnight versus intraday attribution of prior local signals | Existing rejected signals may hide distinct overnight and intraday mechanisms even when total return is null. This is diagnostic, not a new edge claim. | The local panel contains open and close fields; prior B2/B4 tests aggregate return paths. Against: the validation window is spent and any discovered split would be post hoc. | RESURRECTED, DIAGNOSTIC ONLY | Existing fingerprinted local panel only; no acquisition. | Attribute fixed prior signals into close→open and open→close without selecting variants; stop after descriptive sign/stability report. | Post-hoc slicing, adjusted-price semantics, reused validation, no fresh confirmation window. | Low-medium: can explain a rejection but cannot validate an edge. | Low |

## 3. Top-three pre-registrations

The three tests below are maximally different in venue, mechanism and data-generating process. They are frozen before any outcome acquisition. Exact acquisition manifests, hashes and availability timestamps must be recorded before calculation.

### P1 — `CRYPTO-FUNDING-REV-001`

- **Universe:** BTCUSDT, ETHUSDT plus the eight largest eligible USDT perpetuals by trailing notional measured only before the frozen start; eligibility and delist rules fixed in the manifest.
- **Clock:** common funding timestamps. Signal uses the last published funding rate known at settlement; entry is the first tradable minute strictly after settlement; exit immediately before the next common funding timestamp.
- **Rule:** rank funding cross-sectionally; equal-risk long bottom 20%, short top 20%, beta-neutral to BTC with beta estimated on trailing 30 calendar days; no parameter search.
- **Costs:** realized funding cash flow, published taker fee, two half-spreads from contemporaneous quotes when available, and 10 bp round-trip stress. No liquidation leverage; gross exposure 1.
- **Split:** first 70% of timestamps discovery, final 30% sealed holdout; one look only. Family count starts at one.
- **Gate:** holdout net mean > 0, t >= 2.5, both halves positive, stress net > 0, no asset > 35% of positive P&L. Otherwise `FAMILY_REJECTED`.

### P2 — `GEFS-HDD-NG-001`

- **Season/universe:** November–March, CONUS population weights frozen from a named census vintage; no region selection after outcomes.
- **Signal:** change in ensemble-mean 1–15 day HDD between consecutive 00Z GEFS forecast cycles, using only vintages whose issue/availability times precede the return window.
- **Return:** first named executable gas proxy price after forecast availability to the same clock next day; EIA storage-release windows excluded by a rule frozen in the manifest.
- **Controls:** gas level, prior five-day gas return and contemporaneously available storage deviation; forecast-system version indicators fixed from NOAA metadata.
- **Split:** earliest 70% winters discovery, latest 30% sealed holdout; one regional aggregate, one horizon and one sign.
- **Gate:** predicted sign must match the mechanism, holdout net return/t-stat must be positive/≥2.5, at least two holdout winters positive, and no winter >50% of positive P&L. A spot-only screen may establish mechanism, never tradability.

### P3 — `SEC-PEAD-ATTN-001`

- **Universe:** U.S. common stocks with timely 10-Q/10-K XBRL facts, price and market-cap availability; exclusions fixed before outcomes.
- **Signal:** standardized year-over-year diluted EPS surprise using only the first accepted filing version; attention indicator is filing outside 09:30–16:00 ET. No analyst-consensus data.
- **Clock:** SEC acceptance timestamp; enter next regular-session open after at least 30 minutes of public availability; hold 20 sessions.
- **Portfolio:** quintile long–short, value-capped weights, sector neutral; compare high- versus low-attention interaction. Costs 10 bp round-trip central and 30 bp stress.
- **Split:** calendar discovery through 2022, sealed 2023–2025 holdout, one look; exclude issuers lacking a complete point-in-time history rather than backfilling.
- **Gate:** holdout factor-adjusted alpha > 0, t >= 2.5, stress alpha > 0, both half-holdouts positive, and no issuer >5% of positive P&L. Otherwise reject.

## 4. Shared acquisition and evidence contract

1. Owner names each acquisition because public outcome data remain reserved; this board proposes the smallest dataset and does not download it.
2. Before any result, persist source URL/endpoint, request parameters, retrieval time, license/terms note, raw hashes, row/time bounds, missingness and an immutable train/holdout manifest.
3. Preserve original timestamps and vintages; no revised series may silently replace information available at decision time.
4. Pool trial counts across economically equivalent expressions and disclose all exclusions. No dataset switching resets the family count.
5. A negative result persists as `RESULT -> LESSON -> PRIORITY UPDATE -> NEXT ACTION`; no unregistered variant follows.
6. A positive screen earns independent reproduction and validation only. It is not a current opportunity, Book authorization or capital decision.

## 5. Source basis inspected without outcome acquisition

- Binance derivatives API documentation: funding history, funding timestamps, rates and mark/index fields — <https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/rest-api/Get-Funding-Info>.
- NOAA/NCEI GEFS specification and archive coverage — <https://www.ncei.noaa.gov/products/weather-climate-models/global-ensemble-forecast>.
- EIA weekly working-gas definitions and history — <https://www.eia.gov/dnav/ng/NG_STOR_WKLY_S1_W.htm>.
- SEC EDGAR submissions/companyfacts API and bulk archives — <https://www.sec.gov/search-filings/edgar-application-programming-interfaces>.
- SEC acceptance-timestamp explanation — <https://www.sec.gov/about/webmaster-frequently-asked-questions>.

## 6. Route

`INDEPENDENT BOARD -> COMPARE WITH BUILDER BOARD -> OWNER NAMES AT MOST THE SMALLEST REQUIRED ACQUISITIONS -> FREEZE MANIFESTS -> RUN CHEAP SCREENS -> INDEPENDENTLY FALSIFY SURVIVORS`

Until then: `OUTCOME_DATA_ACQUIRED = FALSE`, `EDGE_FOUND = FALSE`, `A2_REOPENED = FALSE`, `REAL_CAPITAL_AUTHORIZED = FALSE`.
