# Chief Brief

Generated from persistent system state. Do not edit by hand: `python3 scripts/quant.py brief` regenerates it.

- canonical state basis: clean persistent replay of committed inputs through 2026-09-21
- system: `quant-system-v1` in `paper_shadow` mode, status `IDLE`
- boots: 1, ticks: 381, research runs: 2, desk sessions: 377

## System health

No open faults.

Component state:

- `BOOK`: **IDLE** - marked through 2026-09-21
- `BUILD`: **BLOCKED** - 3 open capability gaps
- `CONTROL`: **IDLE** - no work due
- `DATA`: **IDLE** - 6 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SEC_CAPTURE`: **BLOCKED** - SEC identity/contact not configured
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 6, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

- **futures_excess_return_daily** (AVAILABLE) - 174,774 rows, 31 symbols, 2002-01-02 to 2024-03-28, `sha256:2731a881292251f2f754256c0f6feb66ec3168f20a39003b4abe59f960e1b6a6`
  - source: https://github.com/pst-group/pysystemtrade data/futures (adjusted_prices_csv, multiple_prices_csv, csvconfig) @ 8958c49c38b1e4a8c07f0e4375d5e9cb68a087f7
  - caveat: third-party research data (pysystemtrade repository), not an exchange feed; not independently verified against exchange settlements
  - caveat: universe is today's liquid contract list: instruments that were delisted before the snapshot are absent (mild survivorship)
  - caveat: returns are in each contract's local currency; P&L currency translation (second order for a margined futures position) is not modelled
  - caveat: volume is unavailable and written as 0: execution capacity is NOT modelled
  - caveat: index excludes collateral interest: every return is an excess return over cash
  - caveat: roll costs use the repository's current spread and commission estimates for the whole history, which likely understates early-2000s costs
  - caveat: a market closed on a shared session carries its last level forward for at most 5 sessions and is flagged stale=1
- **futures_excess_return_daily_broad** (AVAILABLE) - 780,195 rows, 144 symbols, 1990-01-02 to 2024-03-28, `sha256:da1dc5a4d7130400f4fe945aab11a2555604a3155d258b8eaead06736d6c110d`
  - source: https://github.com/pst-group/pysystemtrade data/futures (adjusted_prices_csv, multiple_prices_csv, csvconfig) @ 8958c49c38b1e4a8c07f0e4375d5e9cb68a087f7
  - caveat: third-party research data (pysystemtrade repository), not an exchange feed; not independently verified against exchange settlements
  - caveat: universe is today's liquid contract list: instruments that were delisted before the snapshot are absent (mild survivorship)
  - caveat: returns are in each contract's local currency; P&L currency translation (second order for a margined futures position) is not modelled
  - caveat: volume is unavailable and written as 0: execution capacity is NOT modelled
  - caveat: index excludes collateral interest: every return is an excess return over cash
  - caveat: roll costs use the repository's current spread and commission estimates for the whole history, which likely understates early-2000s costs
  - caveat: a market closed on a shared session carries its last level forward for at most 5 sessions and is flagged stale=1
  - caveat: sessions are the trading days of SP500; a contract trading on a day SP500 did not trade accrues that move to the next session (no return is lost, it is re-timed)
  - caveat: staggered universe: each contract enters at its first observation
- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **perp_funding_pairs_daily** (AVAILABLE) - 108,874 rows, 244 symbols, 2023-06-08 to 2025-05-15, `sha256:55bbf2946f8886d2ec7643f52b38dbd23676d1b208b249e1098d855a1234a361`
  - source: github.com/guibvieira/freqtrade-hyperliquid-data (Hyperliquid 1h funding, 1d bars) + github.com/LorenzoBaggi/funding_arb (Bybit funding, 1h klines)
  - caveat: third-party snapshots, not verified against the venues
  - caveat: survivorship: only coins still listed when the snapshots were taken
  - caveat: no intraday margin, liquidation or auto-deleveraging modelling in the data
  - caveat: Bybit coverage ends 2025-05; forward data comes from data/feeds/funding
  - caveat: where the Bybit kline snapshot is missing the Bybit leg is valued at the Hyperliquid close (price_proxy=1): cross-venue price divergence is then not modelled for that coin
- **us_calendar_legs_daily** (AVAILABLE) - 10,080 rows, 4 symbols, 2016-09-12 to 2026-09-21, `sha256:36928a7b313ca8993b171f6ef56e939332cc0ddc76ad009115018f9eab9041da`
  - source: derived from us_sector_etf_daily (sha256:7f510dccab22aef3bcd34e57f6c8f0f6d6ba8490519e2615ce8a41591cb837ee) and the scheduled FOMC calendar (90 decision days)
  - caveat: open prices are consolidated opening prints, not executable MOO fills
  - caveat: the overnight leg includes ex-dividend gaps through the adjusted basis
  - caveat: holding <SYMBOL>_ON from open(d) to open(d+1) represents a MOC buy on d and a MOO sell on d+1; the Book charges both fills
  - caveat: inherits every caveat of the source ETF snapshot
- **us_sector_etf_daily** (AVAILABLE) - 30,240 rows, 12 symbols, 2016-09-12 to 2026-09-21, `sha256:7f510dccab22aef3bcd34e57f6c8f0f6d6ba8490519e2615ce8a41591cb837ee`
  - source: Yahoo Finance chart API (public, credential-free)
  - caveat: adj_close is restated retroactively for dividends and splits, so adjusted levels are not strictly point-in-time; returns are standard practice but embed later corporate-action information
  - caveat: the endpoint is an undocumented public JSON API with no availability guarantee and no vendor support
  - caveat: prices are consolidated daily bars, not the venue-level quotes an execution model would eventually need
  - caveat: sessions after the original snapshot were appended from data/feeds (Yahoo chart API via the data-feeds workflow), adj_close rebased at the seam

## SEC Form-4 raw capture (P0 acquisition lane)

- collector `BLOCKED`: SEC identity/contact not configured
- liveness: **COLLECTOR_DID_NOT_RUN**
- coverage: **COVERAGE_UNKNOWN**
- fingerprint/materialization: NOT MATCHED
- raw store: append-only True, content-addressed True, incomplete evidence present False
- request policy: None req/s cap (SEC documented maximum None), concurrency None, poll Nones, backoff None
- cooldown: inactive
- states: `CAPTURED` / `NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL` / `NOT_ADMISSIBLE_FOR_CONFIRMATION`

## Research

Queue: `{'PENDING': 0, 'RUNNING': 0, 'BLOCKED': 3, 'COMPLETED': 2, 'FAILED': 0}`.

- `RESEARCH-XS-EXECUTION-AWARE-RELATIVE-VALUE` - **COMPLETED** REJECT_RESEARCH
- `RESEARCH-XS-DAILY-RELATIVE-VALUE` - **COMPLETED** FILTERED
- `SCAN-FACTOR-RESIDUAL-001` - **BLOCKED** no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` - **BLOCKED** raw SEC/Form-4 acquisition operational; downstream parsing, qualification and scientific admissibility protocol not yet authorized/implemented
- `SCAN-VOLATILITY-SURFACE-001` - **BLOCKED** historical option chains, quotes, rates, dividends, and corporate actions absent

Strategy lifecycle: `RESEARCH` 1

- **STR-XS-EXECUTION-AWARE-RELATIVE-VALUE-xs_momentum_l21_z0.5_h5_b0.05** - lifecycle `RESEARCH`, evaluation track
  - out of sample: -5.56% net, beta -0.058, turnover 33x/yr, t=-0.35 against a required 3.20
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 76 rebalances, 301 no-trade, 0 vetoed

## Strongest evidence and rejections

Latest lesson: xs_momentum_l21_z0.5_h5_b0.05 was rejected out of sample (-5.56% net). The signal was gross-negative (-0.78%), so the hypothesis itself is wrong here, not merely too expensive to trade. Its t-statistic of -0.35 is far below the 3.20 required after 36 expressions were tried on this dataset, so the result is indistinguishable from search luck. Market beta was -0.058 against a benchmark that returned +36.80%, so -2.13% of the result is passive exposure rather than skill.

Lessons recorded: 5.

Lane priorities after learning: `xs_daily_relative_value` 24.0, `xs_execution_aware_relative_value` 24.0

## Capital state

- authoritative ledger `quant-shadow-book` (CAPITAL, paper_shadow)
- NAV 1,000,000.00 USD from 1,000,000.00 initial (+0.00%)
- cash 1,000,000.00, realized 0.00, fees 0.00
- 0 open positions, gross 0.00x, net +0.000x
- 377 sessions marked, 0 fills, inception 2025-03-21, last 2026-09-21

## Decision quality

- evaluation ledger NAV 988,369.90 (-1.16%) over 377 sessions and 503 fills
- rejections scored: 1 (true rejects 1, false rejects 0, undetermined 0)
- counterfactual P&L of rejected strategies: -11,630.10
- desk tickets: {'BOOKED': 76, 'NO_TRADE': 301}

## Blockers and capability gaps

- `SCAN-FACTOR-RESIDUAL-001` blocked: no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` blocked: raw SEC/Form-4 acquisition operational; downstream parsing, qualification and scientific admissibility protocol not yet authorized/implemented
- `SCAN-VOLATILITY-SURFACE-001` blocked: historical option chains, quotes, rates, dividends, and corporate actions absent
- build task `BUILD-SCAN-FACTOR-RESIDUAL-001`: point-in-time dataset for the factor_residual lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-FACTOR-RESIDUAL-001)
- build task `BUILD-SCAN-INSIDER-FILINGS-001`: authorized parsing / qualification / scientific admissibility path for the insider_filings lane (acceptance: an authorized downstream Form-4 protocol can consume captured raw evidence without violating the P0 visibility firewall)
- build task `BUILD-SCAN-VOLATILITY-SURFACE-001`: point-in-time dataset for the volatility_surface lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-VOLATILITY-SURFACE-001)

## Next autonomous action

blocked on a dependency for SCAN-FACTOR-RESIDUAL-001: no survivorship-controlled security and factor panel
