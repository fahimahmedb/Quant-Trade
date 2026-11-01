# disc-crypto-book-pressure-prospective-l1-v0

EXPLORATORY, pre-declared 2026-10-11T22:25:50.501096+00:00, head 8e820f454f018a5c7bc7b61bf8002797b4a813d8.

- ID: disc-crypto-book-pressure-prospective-l1-v0
- mechanism: signed top-of-book liquidity pressure may predict a very short subsequent price move.
- who_pays: liquidity takers demanding immediacy; maker inventory and adverse selection compete with this signal.
- why_persist: fleeting inventory pressure may persist despite arbitrage, but taker fees/latency can dominate it.
- level: L1.
- question: can one lagged imbalance expression on public XBTUSD quotes even clear a simple taker-cost hurdle in one short prospective window? A favorable perfect-direction bound may kill this exact fast taker expression cheaply.
- proxy: official public BitMEX quote REST https://www.bitmex.com/api/v1/quote?symbol=XBTUSD&count=1&reverse=true ;21 scheduled snapshots at5s intervals, starting once after this declaration is published. Cached official Swagger accessed2026-10-11 supports public quote data; no new archive, account or parallel persistent collector.
- known_biases: one roughly100s Sunday window, tiny dependent sample, REST latency/receipt not actual exchange order arrival, potentially cached quotes, sizes only top of book, inverse-contract payoff approximated as linear percentage for screening, no depth fills/funding/risk/position sizing. No general market/regime claim. Short-lived pressure differs from closed carry/F1; no funding strategy or old outcome replay.
- fixed_rule: receive21quotes with local send/receive monotonic+UTC timestamps and source timestamp. Per request timeout<=3s and body<=16384B; wait only to scheduled slots; totalprocess<=120s/2MiB. Each slot attempted once, no retries, no request after any non200/malformed/oversize response. Require positive bid/ask and sizes, bid<=ask, quote no more than10s stale or1s future relative to receipt. Trade at snapshot i using sign((bidSize-askSize)/(bidSize+askSize)) from snapshot i-1; entry i at adverse ask(long)/bid(short), exit i+1 at adverse bid(long)/ask(short). Price differences divided by entry mid; zero imbalance => abstain. Adjacent source timestamps must increase and observed quote gap be between1 and12s; invalid intervals reported, not silently treated as fills. Require>=12 valid nonzero-signal trades among19 possible and at least60s total quote-time span; otherwise PARK_DATA. All raw observations and invalidity flags retained.
- cost_assumption: observed crossing bid/ask plus5bp per side fee and1bp total extra slippage centrally; stress10bp/side+1bp. Fixed assumptions, not verified user fee tier. No funding charged for this100s window if it avoids a venue funding boundary; if crosses00/08/16UTC => PARK rather than silently omit. No capital or live claim.
- upper_bound: additionally report absolute next-snapshot mid change in bp ignoring all spreads and with perfect hindsight direction, less11bp central cost. This is a deliberately unattainable favorable bound, not a second tradable strategy. No selection of winning intervals or new horizon. One actual expression + one registered bound,2cost scenarios; M_effective UNKNOWN.
- max_time_minutes:60 agent min; acquisition hard120s,21requests,zero retry; no unattended loop after this one window.
- kill_if: adequate sample and every valid interval favorable perfect-direction bound<=0; OR actual mean central-net<=0. KILL exact lagged5s top-book taker expression in this sampled regime only, not all book-pressure mechanisms or horizons. Mere negative small sample does not statistically establish long-run negative expectancy.
- promote_if: adequate sample, actual central-net mean>=5bp, stress-net positive and both chronological halves positive. Otherwise PARK. PROMOTE_HIGH prohibited with this tiny proxy. Positive gets one prospective nonoverlapping out-of-window L2 replication with fixed horizon before any heavy archive.
- uncertainty: descriptive range/mean/median, valid counts, duration and number of positive trades; no fabricated significance or Sharpe for dependent100s sample.
- prior_exposures: PRIVATE_UNKNOWN; cached BitMEX metadata/catalogue only; known literature on imbalance; prior closed carry and other exposure preserved. New venue/sample does not reset historical multiplicity.
- RESULT: 21 HTTP200 response records, all identical77bytes; required BBO fields missing. Zero valid trades; no financial statistic. Capture violated the stop-on-first-malformed clause due to empty AssertionError text; details and original result hash in adjacent quality JSON.
- DECISION: PARK (PARK_DATA / CAPTURE_INVALID). No rerun or mechanism rejection.
- NEXT: single capture and single calculation; interrupted/partial remains exposed and cannot be retried automatically.

This is the third data-test attempt this pass (VX, France, this capture). SEC was a metadata-only pre-test PARK with zero economic/data-test execution, not a fourth test.
