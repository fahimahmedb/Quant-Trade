# AGENT 2 — PREDICTION MARKETS SCOUT

DATE = 2026-10-08
MISSION_CLASS = ONE_SHOT_SCOUT_ONLY
REAL_CAPITAL_AUTHORIZED = FALSE
F1_TOUCHED = FALSE
EXECUTION_PERFORMED = NONE

## CANDIDATE 1

MECHANISM = Favourite–longshot bias / systematic overpricing of low-probability event contracts, expressed as buying the complementary side (or equivalent) rather than buying the longshot.

MARKET_STRUCTURE = Binary prediction/event contracts with prices interpretable as probabilities and eventual 0/1 settlement. Primary test venue: Kalshi resolved contracts; Polymarket can be used later as an external replication venue if terms/data permit.

WHY_EDGE_CAN_EXIST = Probability weighting, heterogeneous/noisy beliefs, lottery-like demand and capital/transaction frictions can make very low-probability outcomes trade above realized frequencies. Recent evidence is directly relevant: a July 2026 Kalshi unemployment-market study reports statistically significant overpricing for contracts below $0.30; a separate July 2026 CPI study does not find the same broad effect, which argues for a category-conditioned test rather than assuming universality. An October 2026 NBER working paper also reports favourite–longshot bias in most political prediction markets in its historical sample.

WHY_PERSIST = The distortion can persist if marginal longshot demand is less price-sensitive than informed/capital-constrained supply, and if the return to correcting small probability errors is reduced by fees, spread, capital lock-up and event-specific limits. Persistence is therefore expected to be strongest in thin, longer-dated or retail-salient tails, not uniformly across all markets.

DATA_SOURCE = Kalshi public market-data API: trades endpoint exposes ticker, price, quantity and timestamp; market/candlestick endpoints are documented in the same public API. Settlement/outcome metadata can be joined from market endpoints. Official docs: https://docs.kalshi.com/api-reference/market/get-trades . Supporting evidence: https://papers.ssrn.com/sol3/Delivery.cfm/7110758.pdf?abstractid=7110758&mirid=1 ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7087538 ; https://www.nber.org/papers/w35846 .

TERMS_OR_ACCESS_RISK = Public read-only market data appears available through documented endpoints, but API limits, historical-retention rules and any jurisdiction/account restrictions must be rechecked before operationalization. No trading access is required for the discriminating test.

MINIMUM_DISCRIMINATING_TEST = Using resolved historical contracts only, freeze one pre-resolution observation rule (for example last eligible trade or VWAP at fixed horizons such as 24h and 7d before close), bin prices ex ante (e.g. 0.01–0.10, 0.10–0.20, 0.20–0.30, 0.30–0.70, >0.70), and compare mean quoted probability with realized win frequency. Require minimum sample counts per bin, cluster uncertainty by event/series, exclude post-resolution or ambiguous-settlement prints, and compute net expected return of the complementary side under conservative spread/fee assumptions. Primary falsifier: no monotone negative calibration error in the low-probability bins after event/series controls and costs.

EXPECTED_INFORMATION_GAIN = HIGH. One historical-only pass can determine whether the effect exists outside the already-published unemployment slice, whether it is category-specific, and whether magnitude survives realistic costs without consuming a future sealed confirmation set.

MAIN_LEAKAGE_RISK = Selecting categories, price cutoffs, horizons or liquidity filters after seeing their realized calibration; duplicate observations from the same event; using last prices contaminated by resolution information; treating highly correlated brackets as independent samples.

PRIOR_RANK = 1

## CANDIDATE 2

MECHANISM = Cross-outcome structural pricing inconsistency in mutually exclusive/exhaustive multi-outcome events: executable basket prices temporarily violate the event identity after spreads, fees and available depth are accounted for.

MARKET_STRUCTURE = Polymarket multi-outcome negative-risk events. Official mechanics state that only one outcome can win and that one No share in an outcome can be atomically converted into one Yes share in every other outcome. This creates explicit cross-market identities that executable quotes should respect. Polymarket uses a CLOB with observable bids/asks and public order-book endpoints.

WHY_EDGE_CAN_EXIST = Separate order books can update asynchronously after information shocks; liquidity can be fragmented across outcomes; stale makers, heterogeneous inventory and discrete tick/depth can create short-lived basket mispricings even though the contracts are economically linked.

WHY_PERSIST = Only transiently. Atomic negative-risk conversion is itself a strong arbitrage mechanism, so any edge must exceed taker fees, spread, depth depletion, latency and conversion/settlement friction. Augmented negative-risk events also introduce changing named outcomes and an "Other" bucket, creating semantic risk that can deter arbitrage but can also invalidate naive basket tests.

DATA_SOURCE = Polymarket official CLOB/order-book and market APIs. Price history is publicly documented at https://docs.polymarket.com/api-reference/markets/get-prices-history . Negative-risk mechanics: https://docs.polymarket.com/concepts/negative-risk . Order-book mechanics: https://docs.polymarket.com/concepts/prices-orderbook . Current fee schedule: https://docs.polymarket.com/trading/fees .

TERMS_OR_ACCESS_RISK = Read-only public data is sufficient for scouting, but an operational strategy would require rechecking geographic availability, protocol/version details, fee category, conversion path and whether every outcome set is truly complete. Augmented negative-risk "Other" definitions are a specific contract-design hazard.

MINIMUM_DISCRIMINATING_TEST = Read-only simultaneous snapshots across complete named outcomes of a sample of negative-risk events. Compute depth-aware executable basket bounds using best asks/bids plus current taker fees and conservative conversion costs; reject any apparent opportunity that depends on midpoint prices, unavailable depth, unnamed placeholders or changing "Other" semantics. Primary falsifier: no positive net basket violation above a predeclared safety margin across a sufficiently broad snapshot sample.

EXPECTED_INFORMATION_GAIN = MEDIUM-HIGH because the test is cheap and sharply falsifiable, but expected persistence is lower than Candidate 1 because the venue explicitly provides atomic cross-outcome conversion.

MAIN_LEAKAGE_RISK = Using non-synchronous quotes; comparing midpoint rather than executable prices; treating augmented-neg-risk placeholders as a fixed exhaustive partition; ignoring depth or fee changes; selecting only visually anomalous events.

PRIOR_RANK = 2

## SELECTION

TOP_CANDIDATE = Favourite–longshot bias in resolved prediction/event contracts, tested cross-category on Kalshi.

WHY_TOP = It has direct recent empirical support on one Kalshi vertical, conflicting evidence on another vertical, broad historical support in prediction markets, and a fully historical read-only discriminating test. That combination gives high expected information gain without opening a live experiment or spending a future confirmation sample. Candidate 2 is structurally cleaner but likely more efficiently arbitraged by Polymarket's own negative-risk conversion mechanism.

MINIMUM_NEXT_TEST = Historical-only calibration/return study on Kalshi resolved contracts across several predeclared event categories and fixed pre-close horizons, with event-level clustering, strict anti-leakage rules and conservative net-cost estimates. Do not reserve or consume a future sealed holdout unless the historical discovery slice survives.

TERMS_BLOCKER = NONE_FOR_READ_ONLY_DISCOVERY, subject to rechecking API retention/rate limits and venue terms before any operational phase. Trading authorization remains absent.

NEXT_DECISION = AUTHORIZE_ONE_BOUNDED_HISTORICAL_FLB_DISCRIMINATING_TEST_OR_STOP. Do not execute live orders, do not allocate real capital, and do not open a future sealed confirmation set at scout stage.

REAL_CAPITAL_AUTHORIZED = FALSE
