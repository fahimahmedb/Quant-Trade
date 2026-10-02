# V3 Data Archaeology - 2026-10-02 (S1)

AUTHORITY: REAL_CAPITAL_AUTHORIZED=FALSE, LIVE_TRADING_AUTHORIZED=FALSE, t0=NOT_DECLARED, BUILDER_AUTHORIZED=FALSE. OUTCOME_INFORMATION_USED=FALSE.
Machine-readable inventory: `V3_DATA_INVENTORY_2026-10-02.json` (31 records; fields: coverage, resolution, timestamp semantics, PIT validity, access/cost, limits, status).

## Conduct / quarantine
No Weather market price, book, trade, settlement, wallet or P&L was downloaded or opened. Probes were only: S3 directory listings (prefixes/file names/sizes), documentation pages, Kalshi `/historical/cutoff` (public metadata), and the IEM MOS JSON schema (a forecast product, truncated, not a market). Sample rows of market data used: 0.
Starting hypotheses came from the scout inventory; items I re-verified myself are marked VERIFIED, the rest inherit scout status.

## Findings

### A. Prediction markets
1. **Executable depth history does not exist from any venue.** Polymarket exposes `/book` and websocket live only; no historical book endpoint is documented. Kalshi's `/historical/*` has candlesticks, trades, markets and *account* orders, no market-level book archive.
2. **Polymarket `/prices-history`** returns only `t,p`; the meaning of `p` (last trade vs mid) is undocumented; retention and fidelity limits undocumented. Not a bid/ask.
3. **Fees:** current schedule VERIFIED from docs: taker `C*rate*p*(1-p)`, Weather rate 0.05, makers 0. **No change history or effective dates are documented**, so historical fee reconstruction is NOT_FOUND; use per-market `feeSchedule` from gamma captured forward. Tick size / minimum order history is also undocumented; capture forward.
4. **Kalshi** (VERIFIED live 2026-10-02): cutoffs market_settled/trades 2026-08-03, orders 2026-09-18. Candlesticks carry bid/ask OHLC (top of book, no size) on a different venue and settlement source; auth for the other historical endpoints is UNVERIFIED.
5. **Vendor L2** (PolymarketData ~2025-08+, pmdata.dev ~2026-02+) is claimed, unaudited, paid or unclear; pulling weather data is outcome information, so owner approval and post-freeze use only.
6. **On-chain and HF datasets**: fills and lifecycle only; wallet fields are quarantined.
7. **Gamma metadata is not versioned**; snapshot it daily.

### B. Meteorology
1. **Open-Meteo cannot backfill the R* ensemble-member object** (members ~3 days; Previous Runs deterministic; Historical Forecast stitched and not as-issued).
2. **ECMWF open-data AWS archive (VERIFIED by listing):** first date folder `20230118`, all four cycles (00/06/12/18z) present with `0p4-beta/enfo`; `0p25` present by `20240201` for 00z and 06z; latest folder `20261002`; by 2026-06 the layout has `ifs/`, `aifs-ens/`, `aifs-single/` subprefixes (layout break to handle). Per-step files are about 2.6 GB (byte-range via `.index` required). This is the only true as-issued 51-member backfill route. Object/index GETs from this sandbox returned S3 `SlowDown` on repeated attempts, so **which parameters (`2t`, `mx2t6`, `mn2t6`) exist in 0p4-beta files remains UNVERIFIED**. Daily max rebuilt from this archive is a *different signal object* from Open-Meteo's. IFS cycle 50r1 (May 2026) is a model-version break inside the archive; earlier breaks not enumerated here (OPEN).
3. **dynamical.org mirror**: 2024-04-01+, 00z only, so it cannot reproduce intraday latest-vintage-before-T_entry selection.
4. **IEM MOS (VERIFIED schema, API keyless):** as-issued station forecasts with `runtime` (issuance) and `ftime`; GFS MOS from 2003, NAM 2008, LAMP 2020, NBS 2026-05. US stations only.
5. **GEFS** from 2017 (AWS prefix), **NBM** from 2020-05-18; both as-issued, independent of ECMWF. GEFSv12 reforecast is hindcast, not PIT.
6. **ICON-EPS and GEPS public archives not found**; only forward capture works.
7. **TIGGE / WeatherBench2** give pre-2023 as-issued ensembles but research-only and registration (owner approval).
8. **Observations** (METAR/IEM ASOS, NWS WRH 30-day) are observations. GHCN/ISD are revised; ERA5 is reanalysis. None may stand in for a forecast information set.

### Unresolved
Resolution-source timeline per market (Wunderground vs NOAA) is not established; ECMWF 0p4-beta parameter list; Kalshi auth; ToS of Polymarket and IEM bulk use; full IFS version-break dates. These need either owner approval, retry after throttling, or forward capture.

## Implication for design
Honest historical Weather *market* depth cannot be rebuilt. Valid historical information is forecast-side (ECMWF AWS, GEFS, NBM, MOS) joined to observations; market-side executable information must be captured forward (S2).

## AVAILABLE_NOW
- Polymarket live `/book`, ws, gamma metadata, current fee schedule (forward capture only for depth)
- IEM MOS archive (US stations, keyless)
- NWS WRH/api.weather.gov recent observations (30 days)
- Kalshi `/historical/cutoff` metadata

## ACCESSIBLE_WITH_WORK
- ECMWF IFS ENS as-issued, 2023-01-18+ (byte-range GRIB; params to verify; layout and model-version breaks)
- dynamical.org IFS ENS 2024-04-01+ (00z only)
- GEFS 2017+, NBM 2020+, IEM ASOS archive
- Polymarket `/prices-history`, `/trades`, on-chain/HF fills (context only, quarantine)
- Kalshi bid/ask candlesticks (different venue)
- Open-Meteo Previous Runs (deterministic)
- OWNER_APPROVAL_REQUIRED: vendor L2 (PolymarketData, pmdata.dev), TIGGE/WeatherBench2 registration

## NOT_FOUND
- Historical executable depth (any venue) before ~2025-08; any official venue book archive
- Polymarket fee/tick/min-order change history
- ICON-EPS and GEPS public archives
- Weather-specific L2 for DepthFeed/PolyOrderbooks; Meteostat bulk without key
- Verified resolution-source timeline per market

## NOT_POINT_IN_TIME_VALID
- Open-Meteo Ensemble member history (does not exist) and Historical Forecast (stitched)
- GEFSv12 reforecast (hindcast)
- ERA5/ERA5-Land, GHCN-Daily, ISD (revised observations/reanalysis)
- Polymarket gamma metadata (mutable) and `/prices-history` as an executable price
