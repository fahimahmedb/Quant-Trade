# AGENT 4 — MACRO / PUBLIC-DATA SCOUT

DATE = 2026-10-08
MISSION_CLASS = ONE_SHOT_SCOUT_ONLY
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
F1_TOUCHED = FALSE
A2_TOUCHED = FALSE
EXECUTION_PERFORMED = NONE

## CANDIDATE 1

MECHANISM = Predictable Treasury nominal-coupon auction inventory pressure: short-duration-matched Treasury exposure during the pre-auction concession and test the post-results reversal, initially on the 5-year sector via ZF futures.

ECONOMIC_CAUSAL_CHAIN = PUBLIC_INFORMATION_EVENT: Treasury announces a fixed coupon-auction date, offering size and competitive close in advance -> ECONOMIC_TRANSMISSION: dealers/intermediaries and other risk bearers must absorb new supply and manage inventory/hedges into the auction -> REASON_FOR_DELAYED_OR_IMPERFECT_PRICING: finite balance-sheet/risk-bearing capacity creates temporary flow-driven price pressure even though the supply shock is anticipated -> TRADEABLE_MARKET_RESPONSE: Treasury prices weaken/yields rise before the auction and partially reverse after results/allocation uncertainty clears. The July-2026 New York Fed Staff Report 1188 documents this six-hour inverted-V pattern over 1991-2024 and directly links much of it to order flow; in its 2015-2024 subsample the 5-year sector retains statistically significant pressure. Source: https://www.newyorkfed.org/research/staff_reports/sr1188.html and paper https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf .

WHY_EDGE_CAN_EXIST = This is compensation for warehousing a predictable supply shock, not an information-processing mistake. The recent New York Fed evidence is unusually useful because it shows the effect centered on auction close/results and because the mechanism survives in the most liquid sovereign market. The research target is not to rediscover the cash-bond result, but to test whether a simple, executable futures proxy preserves enough of the pressure after spreads/fees to matter.

WHY_NOT_ARBITRAGED = Arbitrage requires balance sheet, timing risk and inventory capacity exactly when supply is being intermediated. The New York Fed reports that the effect has attenuated in recent years as non-dealer participation increased, so persistence cannot be assumed; that attenuation is a reason to demand a current, costed futures replication rather than extrapolate the historical paper.

PUBLIC_DATA = TreasuryDirect Auction Query and archived announcement/results releases. Auction Query provides announcement/results history for TIPS from 1997 and other security types from 1998 and exports CSV/JSON/XML: https://treasurydirect.gov/auctions/auction-query/ . Treasury explains that each announcement fixes the security, offering amount, auction date, issue/maturity dates and bidding close times: https://www.treasurydirect.gov/auctions/how-auctions-work/ . Original announcement PDFs should be retained as point-in-time evidence for the discovery sample.

VINTAGE_REQUIREMENT = Use only information that existed before the proposed entry: original auction announcement date/time, offering amount, security/term, reopening flag and the announced competitive close. Do not use bid-to-cover, stop-out yield, bidder shares or any result field for the pre-auction leg. Prefer archived original announcement files over a current normalized row whenever a field could have been backfilled. Daylight-saving conversion must use America/New_York for each historical date.

RELEASE_TIMESTAMP_QUALITY = HIGH for the ex-ante event signal. Treasury announces auctions days ahead and the announcement contains the close time; the current upcoming-auctions feed is updated on a stated schedule and original announcements are archived. Coupon competitive bids are typically due at 1:00 p.m. ET and results follow shortly after, but the exact announcement for each event is authoritative. Do not encode a fixed UTC hour across DST.

TRADABLE_PRICE_DATA = CME 5-Year T-Note futures (ZF) via Databento GLBX.MDP3, available since 2010 with event timestamps and OHLCV/BBO schemas down to 1 second/1 minute: https://databento.com/catalog/cme/GLBX.MDP3/futures/ZF . Historical CME access is paid but usage-based and small for narrow event windows; this qualifies as reasonably accessible. Continuous-contract construction must be point-in-time and avoid roll hindsight.

MINIMUM_DISCRIMINATING_TEST = One fixed-window, no-parameter-search replication in ZF. Sample nominal 5-year Treasury auctions from 2015 through the latest complete historical month. For every event, read the exact competitive close from the original announcement. Evaluate two separately costed legs using executable BBO when available: PRE = short from T-180 minutes to immediately before T; POST = long from T+10 minutes to T+180 minutes (the +10 minute buffer mirrors the paper's robustness treatment for result-release volatility). Predeclare the front/next contract roll rule from contemporaneous volume/open-interest metadata, exclude only exchange halts/data gaps by fixed rules, and charge spread + exchange/broker fee assumptions. Report mean/median net return, sign rate, HAC/event-level uncertainty and 2015-2024 versus 2025-2026 stability without tuning windows. KILL if either direction is absent in futures or total net V-shape is non-positive after conservative costs; KEEP_AS_RESERVE if direction survives but economics/power are weak; PROMOTE_TO_EXPERIMENT_DESIGN only if both legs or the combined V-shape survive costs with stable sign across the recent slice.

EXPECTED_INFORMATION_GAIN = HIGH. A narrow event-window futures replication answers the main unresolved deployment question—whether the documented cash-Treasury pressure transfers to an accessible instrument after costs—without building a harness or consuming a future sealed confirmation window.

ENGINEERING_COST = LOW-MEDIUM. Treasury auction metadata are structured; market-data extraction is only six hours per monthly event for one futures family. Main work is point-in-time contract selection, DST-safe timing and executable-price costing.

MAIN_LEAKAGE_RISK = Using result-only fields in the pre-auction signal; deriving auction times from current conventions instead of original announcements; hindsight continuous-contract rolls; excluding losing macro-overlap days after seeing returns; optimizing the 180/10/180-minute windows; using midpoints without spread/costs.

MAIN_FALSIFICATION = The documented cash-bond pressure does not survive in ZF after executable costs, or the recent 2025-2026 slice has the wrong sign/near-zero magnitude, indicating that published auction pressure is not a usable futures edge.

DATA_OR_VINTAGE_BLOCKER = NONE_FOR_BOUNDED_TEST. Original Treasury announcements and auction history are public. Tradable ZF data require a low-cost market-data source rather than a purely free source.

PRIOR_RANK = 1

## CANDIDATE 2

MECHANISM = Successive NOAA GFS temperature-forecast revisions -> revisions in expected U.S. heating/cooling demand -> Henry Hub natural-gas futures repricing.

ECONOMIC_CAUSAL_CHAIN = PUBLIC_INFORMATION_EVENT: a new GFS forecast cycle becomes publicly available -> ECONOMIC_TRANSMISSION: revised temperatures change expected HDD/CDD, residential/commercial heating demand and power-sector cooling demand, which changes expected storage balances -> REASON_FOR_DELAYED_OR_IMPERFECT_PRICING: translating a large gridded forecast revision into demand/storage impact is computationally and state dependent, and model files are published progressively rather than as one scalar release -> TRADEABLE_MARKET_RESPONSE: NG futures should move in the direction implied by demand-weighted HDD/CDD revisions if the revision is not already fully impounded. EIA explicitly identifies winter/summer weather as major natural-gas demand and price drivers: https://www.eia.gov/energyexplained/natural-gas/factors-affecting-natural-gas-prices.php . A 2026 working paper reports that forecast revisions, rather than realized weather, materially affect natural-gas price discovery: DOI 10.2139/ssrn.6985300.

WHY_EDGE_CAN_EXIST = The raw public information is high-dimensional and a forecast change only matters economically after geographic weighting, horizon aggregation and translation through current storage/supply conditions. That creates a plausible processing-cost channel rather than a simple same-time correlation.

WHY_NOT_ARBITRAGED = Specialized gas desks already ingest weather models, so any residual edge is likely small and short-lived. Persistence would have to come from processing heterogeneity, nonlinearity and differing model/ensemble interpretation, not from ignorance of GFS. This makes the mechanism plausible but much less certain than Candidate 1.

PUBLIC_DATA = NCEI archives GFS analysis/forecast grids; 0.25-degree forecast data are listed from 26-Feb-2021 onward with four cycles per day at 00/06/12/18 UTC: https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast . GFS implementation history is public and documents major model changes: https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/gfs/implementations.php .

VINTAGE_REQUIREMENT = Use the original forecast grid from each operational cycle, never a later analysis/reforecast as a substitute. Signal must be a revision between consecutive vintages over a predeclared CONUS population/demand weighting and fixed forecast horizon. Segment or exclude model-version breaks (notably FV3/GFS v15 in 2019, v16 in March 2021, v16.3 in November 2022) rather than normalizing them with future information.

RELEASE_TIMESTAMP_QUALITY = MEDIUM-LOW until proven. The archive clearly preserves model cycle (00/06/12/18 UTC), but cycle time is not the same as first public availability; operational products can appear with file-specific delays and historical archives do not obviously preserve the true first-public timestamp for each field. A backtest that executes at nominal cycle time would be look-ahead. Promotion therefore requires either defensible historical first-availability metadata or a conservative fixed availability lag demonstrated to dominate publication latency.

TRADABLE_PRICE_DATA = CME Henry Hub Natural Gas futures (NG) via Databento GLBX.MDP3, available since 2010 with UTC event timestamps and 1-second/1-minute OHLCV/BBO schemas: https://databento.com/catalog/cme/GLBX.MDP3/futures/NG .

MINIMUM_DISCRIMINATING_TEST = First run a bounded timestamp audit on a small stratified sample of archived 0.25-degree GFS cycles across 2021-2026. KILL immediately if historical first-availability cannot be proven or safely upper-bounded without an unusably long lag. If the timestamp gate passes, freeze one signal before seeing returns: consecutive-cycle revision in population-weighted CONUS HDD/CDD over forecast days 3-10, with no threshold optimization; execute only after the proven conservative availability time and measure one fixed 120-minute front-NG return with BBO-based costs. KILL if signed returns are null/opposite after the lag and costs; KEEP_AS_RESERVE if direction exists but is unstable across v16/v16.3; PROMOTE_TO_EXPERIMENT_DESIGN only if the effect is directionally stable and economically non-trivial without threshold tuning.

EXPECTED_INFORMATION_GAIN = MEDIUM-HIGH conditional on the timestamp gate: a single hygienic test can distinguish a real forecast-revision channel from a visually compelling but leaked weather backtest. The timestamp audit itself has high information value because failure terminates the idea cheaply.

ENGINEERING_COST = MEDIUM-HIGH. GRIB extraction, population/demand weighting, run-to-run alignment, model-version segmentation and historical publication-latency proof are materially heavier than Candidate 1.

MAIN_LEAKAGE_RISK = Treating GFS cycle time as publication time; using revised/reanalysis weather instead of the operational vintage; computing population/demand weights with future data; crossing model upgrades without segmentation; choosing forecast horizons/thresholds after inspecting NG returns; hindsight futures rolls.

MAIN_FALSIFICATION = After enforcing a defensible publication lag, consecutive GFS HDD/CDD revisions have no stable signed relationship with subsequent NG returns, or the apparent effect disappears across the 2022 model change.

DATA_OR_VINTAGE_BLOCKER = HISTORICAL_FIRST_PUBLIC_AVAILABILITY_OF_GFS_FIELDS_NOT_YET_PROVEN. This is the gating blocker; nominal cycle timestamps alone are insufficient for an anti-look-ahead backtest.

PRIOR_RANK = 2

## SELECTION

TOP_CANDIDATE = Treasury nominal-coupon auction inventory-pressure / reversal in duration-matched futures, starting with 5-year ZF.

WHY_TOP = Highest EXPECTED_DECISION_INFORMATION / (DATA_COST + ENGINEERING_COST + CONTAMINATION_RISK). It has a directly documented causal mechanism and recent 33-year intraday evidence, public point-in-time auction announcements with exact event timing, one accessible futures instrument, fixed literature-derived windows and a cheap executable-cost replication. GFS->NG has a credible economic chain but is gated by historical first-publication timestamps and substantially higher data engineering.

MINIMUM_NEXT_TEST = Run only the bounded ZF auction-window replication specified above. Do not tune windows, add maturities or open a sealed future confirmation set unless the fixed 5-year test earns PROMOTE_TO_EXPERIMENT_DESIGN.

DATA_OR_VINTAGE_BLOCKER = TOP_CANDIDATE: NONE_FOR_BOUNDED_TEST; requires original Treasury announcement timestamps and paid-but-low-cost CME futures data. RESERVE_CANDIDATE: exact historical GFS first-public availability remains unresolved.

DECISION = PROMOTE_TOP_CANDIDATE_TO_ONE_BOUNDED_HISTORICAL_DISCRIMINATING_TEST; KEEP_GFS_NG_AS_RESERVE_PENDING_TIMESTAMP_PROOF.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
