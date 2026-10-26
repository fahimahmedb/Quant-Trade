# CFE / VX — L2 zero-cost access qualification

Date: 2026-10-12
Branch: `research/edge-lab-continuous`
Parent expression: `disc-cfe-vix-term-premium-l1-v2-reader`
Economic outcomes accessed by this qualification: **NO**
Paid data/account/key used: **NO**

## Decision

`PARK_DATA`

The completed L1 VX expression remains `PROMOTE_EXPRESSION`, not alpha and not V3-admitted. This qualification asked only whether a **distinct, recent, complete, authorized, zero-paid-cost** package exists that is sufficient to separate volatility-risk compensation from residual alpha while supporting execution/risk/capital qualification.

## Verified public surfaces

- Cboe CFE historical futures page exposes VX/VXT price-and-volume detail and daily volume/open interest, including current years: https://www.cboe.com/markets/us/futures/market-statistics/historical-data/futures/
- Cboe daily futures settlement page exposes current VX settlement prices and CSV download: https://www.cboe.com/markets/us/futures/market-statistics/settlement/futures/daily
- Historical CFE archive exposes older VX price/volume files: https://www.cboe.com/markets/us/futures/market-statistics/historical-data/settlement-archive
- Cboe market statistics exposes futures settlement / market-statistics surfaces, including top-of-book as a market-data category: https://www.cboe.com/data/market-statistics
- The complete CFE Futures Trade Data product is commercial DataShop material. It includes `trade_datetime`, `trade_price`, `trade_size`, `bid`, `ask`, order timestamps/ids and settlement fields; historical availability is stated from March 2018 to present and the page explicitly offers purchase/subscription: https://datashop.cboe.com/cfe-futures-trades
- Cboe market-data services describe licensed top-of-book/full-depth and historical products: https://www.cboe.com/data/market-data-services
- Website terms permit limited personal non-commercial viewing/printing/downloading and restrict broader copying/storage/derivative use absent consent: https://www.cboe.com/terms

## Qualification result

Free public data are sufficient for settlement-level/descriptive research and current delayed/public market-statistics inspection. They do **not** establish a distinct zero-cost historical execution package with the bid/ask/trade detail needed for the requested L2 discrimination. The richer execution fields are exposed through a proprietary purchasable/licensed DataShop product.

Therefore no new VX economic experiment is authorized from this qualification. In particular:

- do not replay the completed 36-contract L1 expression;
- do not retry the refused H2022 route;
- do not reinterpret `PROMOTE_EXPRESSION` as residual alpha;
- do not buy Cboe data or create an account;
- do not promote to V3 on this evidence.

## Next decision

Per the predeclared alternative, stop spending cycles on VX access qualification and locate/reuse the existing SEC Form-4 census work before rebuilding anything.

Known existing source branch: `builder/sec-form4-census-v2a` at HEAD `08dcfc39b4b22e0b25e54edde7b6accbb2bc4502` when checked on 2026-10-12. The branch contains the frozen census semantics and tooling. Its latest workflow run is failed and the expected committed `artifacts/sec_form4_census/` directory is not present at that HEAD, so the next action is **artifact/proof recovery/lookup first**, not a fresh SEC crawl.

Search existing workflow artifacts/cache/provenance and earlier proven outputs. If no reusable deterministic census is recoverable cheaply, return `PARK_DATA` for this dependency and move to the next high-leverage Discovery candidate. Any Form-4 return test must be separately predeclared before price/outcome access and must use public filing observability (`event_time`), not transaction date, as the information clock.
