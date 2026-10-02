# External data inventory for a Weather Forward V3 pre-registration

Date: 2026-10-02. Role: research scout. Read-only; no repo change; no commit.
Grounding: `/tmp/claude-0/arch/research/weather_forward/WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md` (section 3 rule R*, section 14.3 STATION_TABLE, section 23).

## 0. Conduct statement (OUTCOME_INFORMATION quarantine)

- No Weather market price, book, trade, settlement, resolution, wallet or P&L series was downloaded, opened or analysed.
- Only documentation and vendor or marketing pages were read, plus three kinds of metadata probe:
  - HTTP status codes.
  - Directory listings of public weather-model buckets: date prefixes and file names only.
  - One tiny Open-Meteo forecast call for a single point, used as a reachability test. It returned a current-day forecast number, which was discarded.
- Incidental exposure, disclosed for the record:
  - A web-search result list contained the title of a third-party page that states a weather outcome for one city on 2026-10-01. Not opened, not used.
  - The same list contained the title of a community GitHub repo whose name suggests a Weather bot. Not opened.
  - Neither touched the V2 Weather market data.
- Every claim has a URL. "UNVERIFIED" means a single weak source, a conflict between sources, or a claim by the vendor itself.
- Vendor claims are marketing statements and have not been audited.
- Reachability is not permission. Terms of service still apply; Polymarket ToS text could not be read (UNVERIFIED).

## 1. Reachability from this sandbox (GET or HEAD, status only)

The outbound proxy was working. Some hosts return 503 or 405 to HEAD but 200 to GET. Details are in the table.

| Host | Result | Note |
|---|---|---|
| gamma-api / clob / data-api .polymarket.com | HEAD 405/200/405; GET 301/200 | Reachable. |
| docs.polymarket.com | 200 | |
| api.open-meteo.com, ensemble-api, previous-runs-api, historical-forecast-api (.open-meteo.com) | HEAD 503; **GET 200** (one-point test) | Reachable; HEAD is unsupported. One later call to `/v1/ecmwf` timed out. archive-api was not GET-tested. customer-api returns 401 (needs a paid key). |
| ecmwf-forecasts.s3.amazonaws.com, noaa-gefs-pds, noaa-gefs-retrospective, noaa-nbm-grib2-pds, noaa-gfs-bdp-pds, openmeteo.s3.amazonaws.com | 200 | S3 listings work. |
| data.ecmwf.int, www.ecmwf.int, ecds.ecmwf.int, cds.climate.copernicus.eu | 200 | |
| data.source.coop, stac.dynamical.org | 200 | |
| huggingface.co | 200 | Kaggle: HEAD 404, GET 200. |
| github.com / api.github.com | 400 | Reachable but not usable for repo traffic. Use the github MCP or the proxy-injected git config. |
| mesonet.agron.iastate.edu (IEM) | 200 | MOS JSON API 200. |
| aviationweather.gov, api.weather.gov, www.weather.gov, nomads.ncep.noaa.gov, www.ncei.noaa.gov, ftp.cpc.ncep.noaa.gov, psl.noaa.gov | 200 | |
| opendata.dwd.de | 200 | |
| dd.weather.gc.ca | HEAD reset once, then GET 200 | Flaky. |
| api.elections.kalshi.com (`/trade-api/v2/historical/cutoff`) | 200 | Public cutoff metadata. |
| kalshi.com | 429 | Rate-limited front page. docs.kalshi.com: 308 redirect, fetched fine. |
| thegraph.com, polygon-rpc.com | 200 | |
| Vendors: polymarketdata.co, pmdata.dev, depthfeed.com, polyorderbooks.com, gribstream.com | 200 | |
| meteostat.net | 200 | api.meteostat.net 403 and bulk.meteostat.net 403 (needs a key, or the host blocks the proxy). |
| **dash.cloud.google.com** | **proxy 502 on CONNECT** | Policy denial per the proxy log. Not needed. |
| storage.googleapis.com | 400 | Reachable. The gs://weatherbench2 bucket was not tested. |
| metaculus.com | 403 | |
| api.goldsky.com | 404 | Reachable; the subgraph URL is unknown. |

**Nothing needed for V3 is network-blocked.**

Network-policy note: the `read_documentation` topic `environment.network` was not read, because no host needed unblocking.

## 2. Group A. Prediction-market history for weather contracts

### A1 to A5 table

| # | Source | What it holds | URL | Coverage | Point-in-time valid? | Access / licence / cost | Rate limit | Reachable | V3 relevance | Risks |
|---|---|---|---|---|---|---|---|---|---|---|
| A1a | Polymarket CLOB `/prices-history` | Per-token price series: `t`, `p` (only). Params `startTs`, `endTs`, `interval` (max, all, 1m, 1w, 1d, 6h, 1h), `fidelity` (minutes). | https://docs.polymarket.com/developers/CLOB/timeseries | Retention is undocumented. Resolved markets return empty below about 12 h granularity. | The `p` field is not defined in the docs: last trade or mid is UNVERIFIED. It is **not** a bid or ask. | Public, no key; ToS unread (UNVERIFIED) | CLOB 1,000 req/10 s on this route (https://docs.polymarket.com/api-reference/rate-limits) | Yes | Descriptive price context only. Cannot give executable asks. | Coarse fidelity on closed markets: https://github.com/Polymarket/py-clob-client/issues/216 |
| A1b | Polymarket data-api `/trades` | Public trade tape with `price`, `size`, `side`, `timestamp`, `conditionId`, `transactionHash`, plus wallet fields (`proxyWallet`, `name`, `pseudonym`) | https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets | Offset capped at 10,000 per window; deeper history via separate start/end windows | Fills are real, timestamped events. They show executed prices only, not the standing book. | Public, no auth | v2 `/trades` 300 req/10 s | Yes | Fill-level price context. Avoid the wallet fields (quarantine). | Not a depth source. Sparse in quiet buckets. |
| A1c | Polymarket CLOB `/book`, `/books`, websocket `market` channel | **Live** bids and asks with sizes. `timestamp` is the book snapshot time. `/books` takes up to 500 tokens. The websocket sends `book` and `price_change` events. | https://docs.polymarket.com/trading/orderbook ; https://docs.polymarket.com/developers/CLOB/websocket/market-channel | **Live only.** The docs describe no historical book endpoint. | Valid now only. Matches V2's own forward capture (spec 12). | Public | `/book` 1,500 req/10 s | Yes | This is the only first-party route to executable asks, and it works only if V2 or V3 captures it forward in real time. | **Historical executable depth does not exist from the venue.** |
| A1d | Polymarket gamma `/events`, `/markets` | Metadata only: titles, buckets, descriptions, tick size, `feeSchedule`, `closed` flag | https://docs.polymarket.com/api-reference/introduction | Includes closed events; V2 already uses it | Metadata is not versioned (a point-in-time caveat). | Public | `/events` 500 req/10 s, `/markets` 300 req/10 s | Yes | Station and event universe; survivorship reconstruction (spec 23). | Listing at a later date may omit or alter events. Snapshot it daily. |
| A2 | On-chain (Polygon CTF Exchange `OrderFilled` events; CTF split/merge/redeem), via RPC or subgraph | **Fills and lifecycle only.** Matching is off-chain, so resting orders and cancels never reach the chain. | https://chainstack.com/polymarket-api-for-developers/ ; https://arxiv.org/html/2606.04217v1 | Contract life, Nov 2022 onward | True on-chain timestamps, block-level | Free via public RPC; heavy; subgraph URL not located (api.goldsky.com root 404) | RPC dependent | Yes (polygon-rpc.com 200) | Independent check of fills and settlement timing. Cannot recover the book. | Maker and taker addresses give wallet identities (quarantine). |
| A3a | PolymarketData (vendor) | Prices, metrics and **1-minute L2 book snapshots**, REST with API key; has a weather page. Claims "L2 snapshots from August 2025 onward". | https://www.polymarketdata.co/polymarket-historical-data ; https://www.polymarketdata.co/polymarket-weather-data | Start date not stated on the weather page; "August 2025" is from search-result text (UNVERIFIED) | Captured snapshots, not auditable; 1-minute grid, not tick | Paid tiers Trader, Pro, Ultra, Enterprise; **prices not public** (https://www.polymarketdata.co/pricing) | Not stated | Yes | Could supply post-hoc minute-grid books for the weather universe after Aug 2025. | **Pulling this is outcome information.** Provenance and capture gaps unauditable. Use only after the freeze, as a descriptive cross-check. |
| A3b | pmdata.dev (vendor) | Tick-by-tick L2 snapshots and updates, trades; Parquet at `/v1/polymarket/l2/{YYYY/MM/DD}/{slug}.parquet`; has a weather page | https://pmdata.dev/polymarket-order-book-data ; https://pmdata.dev/ | **Since 2026-02**; websocket capture, "99.9% completeness" (vendor claim) | Live websocket capture, plausibly point-in-time | Free start; paid tiers not public | Not stated | Yes | Best-documented vendor depth, but under 8 months of history. | Same quarantine issue. Weather coverage and ToS unread. |
| A3c | DepthFeed | Raw CLOB deltas plus normalised books | https://polymarketpricedata.com/historical-data | Rolling 7/30/90 days, or full archive on the Desk plan; **crypto only** (BTC, ETH, SOL, XRP, DOGE, BNB, HYPE) | Genuine capture | Paid; price not public | Not stated | Yes | **No weather.** | Not useful. |
| A3d | PolyOrderbooks | L2 snapshots, 60 s buckets on the free tier, 1 s on paid | https://dev.to/polyorderbooks/how-to-get-historical-polymarket-order-book-data-for-backtesting-olc | Crypto markets in the examples | Captured | Free and paid tiers | Not stated | Yes | Weather coverage is not shown. | UNVERIFIED for weather. |
| A4 | Community datasets (Hugging Face, GitHub) | **Fills and market metadata only; no book depth.** | see A5 below | 2022 to mid-2026 | On-chain timestamps | Free; licence varies | n/a | Yes | Backtest-style context only. | Quarantine. Large (50 to 160 GB). |
| A5a | Kalshi `/historical/*` (market candlesticks, trades) | Candlesticks with `yes_bid` and `yes_ask` OHLC, `price` OHLC, `volume`, `open_interest`; period 1, 60 or 1440 min; 5,000 per request | https://docs.kalshi.com/api-reference/historical/get-historical-market-candlesticks ; https://blog.predictefy.com/kalshi-historical-data | About mid-2021 onward (third-party blog; UNVERIFIED); live window about 2 months, then the historical namespace | Bid/ask **OHLC** on a candle grid. Real quotes, but no sizes. | Candlestick schema lists no auth. Cutoff endpoint returned 200. Other historical data may need auth. | Not stated | Yes | **Best available proxy for executable quotes, but top-of-book only**, on a different venue and different settlement source. | A different market. Order-book snapshots are not offered (see below). |
| A5b | Kalshi order-book history | **None documented.** Resting orders are never archived. | https://blog.predictefy.com/kalshi-historical-data ; https://docs.kalshi.com/getting_started/historical_data | n/a | n/a | n/a | n/a | n/a | Not obtainable. | A third-party claim, but consistent with the official docs listing no book endpoint. |

### A5 community datasets

| Dataset | What | Licence | Coverage | Book depth? | URL |
|---|---|---|---|---|---|
| TimeSeventeen/Polymarket-v1 | `OrderFilled` tape (about 1.2 B rows), CTF lifecycle events, cleaned daily layers | CC-BY-4.0 | 2022-11-21 to 2026-04-28 | **No.** The card says explicitly there is no CLOB quote-level data or resting depth. | https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1 |
| SII-WANGZJ/Polymarket_data | `orderfilled.parquet` and `trades.parquet` (163 GB total, 1.9 B records); market metadata columns | Not stated on the page (UNVERIFIED) | Not clearly stated | No snapshots | https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data ; https://github.com/SII-WANGZJ/Polymarket_data |
| benjessel/polymarket_trades | Every `OrderFilled` fill with maker and taker | Not stated | Through 2026-07-20 | No | https://huggingface.co/datasets/benjessel/polymarket_trades |
| vgregoire/polymarket-users | Reconciled end-user trades | Not stated | 2022-11-11 to 2026-03-29 | No | https://huggingface.co/datasets/vgregoire/polymarket-users |
| BrockMisner/polymarket-btc-updown | Crypto only | Not stated | n/a | n/a | https://huggingface.co/datasets/BrockMisner/polymarket-btc-updown |
| Kaggle | Not found in the searches | n/a | n/a | n/a | n/a |

### A. Plain statement: executable depth versus last trade or mid

- **Cannot ever provide point-in-time executable ask or bid depth** (past, from the venue): Polymarket REST and websocket history, the on-chain data, all HF/GitHub fills datasets, and Kalshi (no book history).
- **Last trade or mid only:** Polymarket `/prices-history`, `/trades`, subgraphs and on-chain data, Polymarket-v1, SII-WANGZJ, benjessel, vgregoire.
- **Top-of-book quotes (no sizes), different venue:** Kalshi historical candlesticks (`yes_bid` and `yes_ask` OHLC).
- **Executable depth, third-party only:**
  - Vendor-captured L2 on Polymarket: PolymarketData (1-minute grid, "from August 2025", paid, UNVERIFIED) and pmdata.dev (tick, from 2026-02).
  - Both are unaudited and only recent. Both would have to be bought after the V3 freeze.
  - Nothing from before August 2025 exists as depth.
- **Honest conclusion:** executable depth for Weather is obtainable **only by forward capture** (V2's own book capture), or from a vendor covering roughly the last 8 to 14 months.

## 3. Group B. Archived NWP forecasts as issued

| # | Source | What | URL | Coverage | Members / resolution / lead | Point-in-time? | Licence / cost | Reachable | V3 relevance | Risks |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | **Open-Meteo Ensemble API** (the R* source) | Live and recent ensemble. `past_days` and `start_date` exist but "up to three days of historical data" for members. | https://open-meteo.com/en/docs/ensemble-api ; https://open-meteo.com/en/docs/ensemble-mean-api | Member history about 3 days. Ensemble **means and spreads** since about 2026-03 (UNVERIFIED). One user reported a drop from about 3 weeks to about 24 h on 2026-01-08. | `ecmwf_ifs025`: 51 members, 0.25 degree, 3-hourly, 15 days, updated every 6 h | True vintage only while live. **There is no history of individual members to backfill.** | CC-BY 4.0 data; free tier is non-commercial. Free limits 600 per minute, 5,000 per hour, 10,000 per day, 300,000 per month. Professional tier "unlocks historical, climate and ensemble data"; price not public. https://open-meteo.com/en/pricing ; https://open-meteo.com/en/terms | Yes (GET 200) | Continuing V2's own forward vintage capture is the only way to keep the exact R* object. | The 30-day bias window cannot be backfilled from Open-Meteo. Past-days behaviour changes (https://github.com/open-meteo/open-meteo/issues/1665). |
| B2 | Open-Meteo **Previous Runs API** | "Day-N-ago" forecast values from fixed lead offsets (`_previous_day1`..`7`) | https://open-meteo.com/en/docs/previous-runs-api | Most models since January 2024; GFS 2 m temperature since March 2021 | **Deterministic models. No ensemble support is documented.** | As-issued by lead offset, not by run | Non-commercial, commercial or self-hosted options | Yes (GET 200) | Deterministic covariate or sanity benchmark. Cannot rebuild the 51-member dressed CDF. | Not the R* object. |
| B3 | Open-Meteo **Historical Forecast API** | Stitched first hours of successive runs | https://open-meteo.com/en/docs/historical-forecast-api | About 2021/2022 depending on model; ECMWF IFS HRES from January 2017 | Hourly, deterministic | **Not as-issued** (stitched analyses). The docs say "not suitable for long time series due to model version changes". | CC-BY; non-commercial free | Yes (GET 200) | Cheap, but the leakage-prone stitch. Avoid for pre-registered validation. | Not point-in-time at lead. |
| B4 | Open-Meteo **Single Runs API** | Whole single model runs selectable by `run=` | https://open-meteo.com/en/docs/single-runs-api | Most models only from 2026-04-02; IFS HRES 9 km from 2024-03-14 | No ensembles documented here | True run | Non-commercial, commercial or self-hosted | Not tested | Little. | Too short. |
| B5 | Open-Meteo open data on AWS (`s3://openmeteo`, us-west-2) | Run-based data kept about 3 months; rolling time series indefinitely | https://github.com/open-meteo/open-data | Model forecasts from December 2023 or later | Ensemble contents are not listed | Run data is point-in-time, but only about 3 months deep | CC-BY-4.0; free | Yes (200) | Possible short backfill; ensemble inclusion is UNVERIFIED. | Format is a custom "OM-files" format; needs their library. |
| B6 | **ECMWF open data on AWS** (`ecmwf-forecasts`, eu-central-1) | IFS ENS (`enfo`), HRES (`oper`), waves, plus AIFS. GRIB2 with `.index` sidecars for byte-range access. | https://registry.opendata.aws/ecmwf-forecasts/ ; https://www.ecmwf.int/en/forecasts/datasets/open-data | **Listed by prefix:** first date folder **20230118** (`0p4-beta` stream). `0p25` folders first seen **20240201**. Dates run through 2026-10-02. | ENS: 51 members, 00/06/12/18 UTC; 0 to 144 h 3-hourly, 150 to 360 h 6-hourly (06/18 UTC runs to 144 h). Parameters include `2t`, `mx2t6`, `mn2t6`. Whether early `0p4-beta` files carry `mx2t6` and whether all four cycles exist then is UNVERIFIED. | **True as-issued vintages** (each run in its own date/time prefix) | CC-BY-4.0 plus ECMWF terms; free; anonymous S3 | Yes (listing 200) | **Best route to backfill the exact IFS ENS 51-member objects for the 30-day bias window and for pre-2026 history.** | Each step file is multi-GB (about 6 GB observed) so selective byte-range reads are needed. IFS cycle changes (50r1 on 2026-05-13) alter the model within the archive. Daily max rebuilt from 3-hourly `2t` or 6-hourly `mx2t6` differs from Open-Meteo's daily max, so it is a **different signal object** from R*. |
| B7 | ECMWF open-data server | Rolling archive of the latest 12 runs (about 2 to 3 days) | https://www.ecmwf.int/en/forecasts/datasets/open-data | Last 2 to 3 days | same as B6 | True | Free | Yes | No history beyond B6. | Short. |
| B8 | **dynamical.org ECMWF IFS ENS** (Icechunk Zarr; on AWS Open Data) | Analysis-ready archive; dimensions `init_time`, `ensemble_member`, `lead_time` | https://dynamical.org/catalog/ecmwf-ifs-ens-forecast-15-day-0-25-degree/ ; https://registry.opendata.aws/dynamical-ecmwf-ifs-ens/ ; STAC https://stac.dynamical.org/ecmwf-ifs-ens-forecast-15-day-0-25-degree/collection.json | **init_time from 2024-04-01 to present; 00 UTC runs only** | 51 members (1 control + 50), 0.25 degree, 19 variables, 3-hourly then 6-hourly. `temperature_2m` is present; explicit max/min variables are not listed. | As-issued per `init_time`, but a derived and re-gridded mirror | CC BY 4.0 plus ECMWF terms; free | Yes (STAC 200) | Much easier than raw GRIB for a V3 backfill. | **00 UTC only**, so it cannot reproduce "greatest `captured_at` before T_entry" vintage selection (spec section 3) for intraday T_entry. Late-delivery issues exist: https://github.com/dynamical-org/reformatters/issues/1149 |
| B9 | **TIGGE** (ECMWF/CMA archive, 13 centres) | Multi-model ensembles including ECMWF, NCEP, UKMO, CMC, JMA, KMA, CMA, BoM, Météo-France | https://www.ecmwf.int/en/research/projects/tigge ; https://ecds.ecmwf.int/datasets/tigge-forecasts?tab=overview | October 2006 onward | Ensemble sizes 12 to 51; 6-hourly output (third-party text) | As-issued archive | **Research purposes only; registration required.** The 48-hour delay mentioned in the task could not be confirmed (UNVERIFIED). | ecds.ecmwf.int 200 | Gives non-ECMWF ensembles and long pre-2023 history for covariates. | Registration conflicts with the no-credentials rule unless the owner approves. Research-only licence. |
| B10 | **GEFS** operational on AWS (`noaa-gefs-pds`) | 21 members, 4 cycles/day, 16 days | https://registry.opendata.aws/noaa-gefs/ | Prefixes begin `gefs.20170101` (listing) | 0.5/0.25 degree depending on product; variable coverage not confirmed here (UNVERIFIED) | As-issued | NODD open data policy; attribution for unaltered data | Yes (200) | **Independent model family** (NCEP), 2017 onward. A strong independent covariate. | Large grids; GEFS v12 change in 2020. |
| B11 | **GEFSv12 reforecast** (`noaa-gefs-retrospective`) | Hindcast, not as-issued | https://registry.opendata.aws/noaa-gefs-reforecast/ ; https://psl.noaa.gov/forecasts/reforecast2/ | 2000 to 2019 | 5 members daily at 00 UTC; 11-member weekly out to 35 days | **Not as-issued** (hindcast with the same model) | Open | Yes (200) | Climatological calibration only. | Not usable for point-in-time validation. |
| B12 | **NBM** (`noaa-nbm-grib2-pds`, `noaa-nbm-pds`) | NCEP blend, 2.5 km CONUS; hourly cycles | https://registry.opendata.aws/noaa-nbm/ ; https://www.nco.ncep.noaa.gov/pmb/products/blend/ | Prefixes begin `blend.20200518` (listing) | Core hourly; QMD at 00/06/12/18 UTC; 264 to 384 h | As-issued | NODD open | Yes | **Calibrated US guidance** (a strong covariate for US stations). | US only. Percentile products need verification. |
| B13 | **MOS archive at IEM** | GFS MOS (since 2003-12-16), NAM MOS (2008-12-09), LAMP (2020-07-12), NBS/NBE (from 2026-05-05) | https://mesonet.agron.iastate.edu/mos/ | as listed | station-based, daily max/min | **As-issued text bulletins** | © Iowa State University; API `/api/1/mos.json?station=KAMW&model=GFS`; no explicit rate limit | Yes (200) | **Long, station-specific, as-issued statistical forecast history** for US ICAO stations. A good independent covariate. | US stations only. The terms of use for bulk research have not been read. |
| B14 | ICON-EPS / ICON-EU-EPS (DWD) | Ensemble | https://opendata.dwd.de/weather/nwp/ ; https://source.coop/dynamical/dwd-icon-grib | DWD keeps about 24 h. The Source Cooperative mirror begins 2025-10-08 and covers **ICON-EU deterministic only**, not the EPS. | n/a | n/a | CC BY 4.0 | Yes | None for history. | An EPS archive does not exist publicly (needs your own collection from now). |
| B15 | GEM / GEPS (Environment Canada) | 20 members + control | https://eccc-msc.github.io/open-data/msc-datamart/readme_en/ | MSC datamart keeps about 30 days. The Environment Canada archive costs C$118 per hour (cost recovery). | n/a | n/a | n/a | Yes (flaky) | Via TIGGE only. | None. |
| B16 | WeatherBench 2 | `gs://weatherbench2/datasets/ifs_ens/` (ENS from TIGGE, 2018 to 2022, 50 members) | https://weatherbench2.readthedocs.io/en/latest/data-guide.html | 2018 to 2022 | 0.2 degree to 2023 | As-issued (from TIGGE) | **Research purposes only** (TIGGE terms) | Bucket host reachable; bucket not tested | Possible pre-2023 coverage. | Research-only; global grids at coarse subsetting. |
| B17 | GribStream (third-party API) | ECMWF IFS/AIFS, GFS and others via API; free token | https://gribstream.com/blog/ecmwf-real-time-catalogue-open-data-2025 | Not stated (UNVERIFIED) | n/a | As-of semantics not documented | Free token; paid plans not seen | Yes | A convenience alternative. | Not verifiable. |

### B summary

- **Open-Meteo cannot backfill the R* object.**
  - Individual ensemble members are kept for about 3 days.
  - Previous Runs has no ensembles.
  - Historical Forecast is stitched, not as-issued.
- Backfilling the same 51-member ECMWF IFS ENS is possible from the ECMWF AWS archive, from 2023-01-18 at 0.4 degrees and from about 2024-02 at 0.25 degrees. It is a different pipeline from Open-Meteo, so it gives a new signal definition.

## 4. Group C. Observations and settlement-type sources (inventory only)

| Source | What | URL | Coverage | Point-in-time? | Licence / access | Reachable | Notes |
|---|---|---|---|---|---|---|---|
| NWS/WRH Time Series Viewer | METAR/SPECI observations, up to 720 h (30 days) | https://www.weather.gov/wrh/timeseries | Last 30 days only | Live view | Public web page; use `api.weather.gov` instead of scraping | 200 | The spec's template source. 30-day cap, no archive. |
| api.weather.gov | NWS API; observations and forecasts | https://www.weather.gov/documentation/services-web-api | Recent only (retention not stated) | Live | Open data, free; User-Agent header required; rate limit "not public" | 200 | Not an archive. |
| IEM ASOS/METAR archive | Worldwide airport observations, 30+ variables, updated every 10 min | https://mesonet.agron.iastate.edu/request/download.phtml | Archive from NCEI ISD, MADIS 1-minute ASOS and other feeds; start year not stated | Archive; "very little quality control" | Free download; limit 1,000 station-years for specified stations | 200 | Reconstructs the daily max from METAR. The METAR-derived max need not equal the official climate report. |
| IEM CLI (NWS Daily Climate Report) | Official daily highs and lows from climate reports | dataset page 404 (https://mesonet.agron.iastate.edu/info/datasets/cli.html); contact the maintainer | UNVERIFIED | UNVERIFIED | UNVERIFIED | Page 404 | Check the IEM API pages. |
| aviationweather.gov | METAR/TAF data API | https://aviationweather.gov/data/metar/ | Short window (UNVERIFIED) | Live | Open | 200 | Observation capture, not an archive. |
| NCEI GHCN-Daily | TMAX/TMIN, 100,000+ stations in 180 countries | https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily | 1833 onward; rebuilt weekly | **Not point-in-time**: records get revised and replaced | HTTPS and AWS; no explicit licence statement | 200 | Final-quality daily extremes; the 45 to 60 day archive lag matters for US data. |
| NCEI ISD / Global Hourly | Hourly surface observations, 20,000+ stations | https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database | 1901 onward | Revised | Open web services | 200 | |
| Meteostat | Aggregated station data | https://dev.meteostat.net/license | Varies | Aggregated; mixed | **CC BY-NC 4.0**; the JSON API goes through RapidAPI (key); bulk host returned 403 | 200 front page; bulk and API 403 | Non-commercial licence; API needs a key, so it is not usable under the rules. |
| OurAirports `airports.csv` | Coordinates, elevation, time zone | https://davidmegginson.github.io/ourairports-data/airports.csv | Snapshot | n/a | Public domain per project (UNVERIFIED) | 200 | Already the spec's source. |

Weather Underground: Polymarket's current resolution source is described as Wunderground history for many cities (https://polymarket.com/weather, third-party report). The spec says NOAA WRH for the primary cohort. I did not fetch Wunderground; the `api.weather.com` host answers 401 (a key is needed).

## 5. Group D. Other covariates known before T_entry

| Covariate | Source and URL | Coverage | As-issued availability | Licence | Notes |
|---|---|---|---|---|---|
| Daily temperature normals | NOAA U.S. Climate Normals 1991-2020: https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals | About 7,300 US stations with daily max/min | Fixed 30-year product, known in advance; v1.0.1 (23 stations recalculated in 2023) | Not stated | US only. A global source would be needed for non-US stations (WMO normals; not checked). |
| ERA5 / ERA5-Land reanalysis | via Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api ; or the Copernicus CDS | ERA5 from 1940 (0.25 degree), ERA5-Land from 1950 (0.1 degree) | 5-day delay (ERA5T), so it cannot feed same-day features. It can build climatology and past anomalies. | CC-BY | Reanalysis, not as-issued. |
| AO / NAO daily indices | CPC: https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/ao.shtml | AO daily since Jan 1950 | The analysis part is daily 00Z GFS-based; forecasts also shown | US government | Index is computed from the GFS analysis; use only the as-of-t0 value. |
| Sea-surface temperature anomalies | NOAA OISST v2.1: https://www.ncei.noaa.gov/products/optimum-interpolation-sst | Daily from 1981-09-01 at 0.25 degree | Preliminary versus final values differ (lag not documented) | Not stated | Would need preliminary-versus-final handling to be point-in-time. |
| Soil moisture and ENSO | Not verified in this pass | n/a | n/a | n/a | UNVERIFIED. |
| MOS and NBM station guidance | see B12, B13 | | As-issued | | Strong, independent, available before T_entry for US stations. |
| Other-model ensemble guidance | see B10, B9 | | As-issued | | |

## 6. Group E. More independent dates, stations or contract types

| Option | Mechanics | Data availability | Reachable | Differences from Weather Forward |
|---|---|---|---|---|
| Kalshi daily high/low temperature (KXHIGH*, KXLOW*) | Bracket markets for about 20 US cities (third-party list; the Kalshi help article gives no count) | Historical candlesticks with bid/ask OHLC (A5a); no book depth | Yes | A different venue and fee structure. **Settlement source conflict:** the Kalshi help article says NWS (https://help.kalshi.com/en/articles/13823837-weather-markets); several third-party pages say the daily temperature series moved to The Weather Company in August 2026. UNVERIFIED. |
| Kalshi hourly temperature | Directional above/below contracts, settle about 25 to 35 min after close, The Weather Company source | Same candlestick API | Yes | Very different horizon; cannot be tested with T_entry = game_start minus 6 h. |
| Kalshi monthly precipitation | KXRAIN*M monthly totals (NYC, CHI, DEN, SEA, DAL), settle on NWS (third-party) | Candlesticks | Yes | Monthly cumulative, not daily. |
| Kalshi hurricane / snow | KXHUR*, snow series; hurricane settles on NHC (third-party) | Candlesticks | Yes | Rare events; few independent dates. |
| Polymarket other weather | Precipitation by month, hurricane and tropical-storm events, global temperature rank (https://polymarket.com/weather) | Same Polymarket APIs | Yes | Cumulative or monthly mechanics. Hurricane and ENSO questions are not independent daily draws. |
| Metaculus / Manifold weather questions | Not assessed. Metaculus returned 403 from the sandbox. | n/a | Metaculus 403; Manifold 200 | Play-money or reputation markets; no executable prices. |

Independence note: adding stations in the same weather regime or sharing the same NWP model does not add independent dates. A different forecast family (GEFS, NBM) adds a separate error source rather than separate market dates.

## 7. Group F. Shortlist and what is not obtainable

### Top 5 (value-to-effort order)

1. **Keep forward capture of the Polymarket book and Open-Meteo ensemble exactly as V2 does.** It is the only source of true executable asks and of the exact R* signal object. Risk: no history; the sample size grows only with calendar time.
2. **ECMWF IFS ENS from the AWS open-data bucket** (B6; or the dynamical.org mirror B8 as a shortcut). Backfills as-issued 51-member vintages. Risk: it is a different pipeline from Open-Meteo, so any backfilled bias window is a different signal object. dynamical.org is 00 UTC only.
3. **NBM and MOS station guidance** (B12, B13) for US stations. Independent calibrated guidance, as-issued, free, long. Risk: US only; `NBS/NBE` text archive at IEM starts only 2026-05; terms for bulk use unread.
4. **GEFS operational archive** (B10) as a second, independent ensemble family. Risk: large files; variable and resolution details unverified; the 2020 system change.
5. **Kalshi temperature history** (A5a), only as a post-freeze cross-venue descriptive check. Risk: different settlement source (possibly changed in August 2026), top-of-book only, and any price pull is outcome information.

Vendor L2 books (A3a, A3b) are intentionally not in the top 5, for the reasons in the risks column.

### Not obtainable (do not plan around these)

- Historical executable bid/ask depth from Polymarket itself: no first-party archive exists.
- Any Polymarket order-book depth from before about August 2025 (the earliest vendor claim; February 2026 for pmdata.dev).
- Order-book history on Kalshi.
- Historical Open-Meteo `ecmwf_ifs025` individual ensemble members older than about 3 days.
- A public DWD ICON-EPS or Environment Canada GEPS archive (24 h and about 30 days of retention; GEPS archive retrieval is cost-recovery).
- Resting orders and cancellations from the chain (matching is off-chain).
- Meteostat via the API or bulk host without a key (403 from this sandbox).

## 8. Open items for the owner (not done here)

- Registering for TIGGE is a credentialed step; it needs owner approval.
- Vendor access costs are not public; any purchase is a paid-resource decision for the owner.
- Reading Polymarket's ToS for automated reads and data use was not possible (page text not returned).
