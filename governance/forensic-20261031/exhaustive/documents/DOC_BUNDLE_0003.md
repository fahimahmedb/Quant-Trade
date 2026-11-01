===== DOCUMENT 001 =====
BLOB: 9d56eabe848ebf6ab85cb25bd3efaad4f0c8b4df
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 2
PATHS: CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/9d56eabe848ebf6ab85cb25bd3efaad4f0c8b4df.txt
BYTES: 6327
ENCODING_STATUS: UTF8
SHA256_CONTENT: 9464cf0b6f12a648defc0a0ad07b67c52942fc7ee557eb3f8d78c60de10e2fcd
----- CONTENT START -----
# Chief Brief

Generated from persistent system state. Do not edit by hand: `python3 scripts/quant.py brief` regenerates it.

- canonical state basis: clean persistent replay of committed inputs through 2026-09-11
- system: `quant-system-v1` in `paper_shadow` mode, status `IDLE`
- boots: 1, ticks: 381, research runs: 2, desk sessions: 377

## System health

No open faults.

Component state:

- `BOOK`: **IDLE** - marked through 2026-09-11
- `BUILD`: **BLOCKED** - 3 open capability gaps
- `CONTROL`: **IDLE** - no work due
- `DATA`: **IDLE** - 2 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SEC_CAPTURE`: **BLOCKED** - SEC user agent/contact not configured; capture fails closed
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 2, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **us_sector_etf_daily** (AVAILABLE) - 30,168 rows, 12 symbols, 2016-09-12 to 2026-09-11, `sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1`
  - source: Yahoo Finance chart API (public, credential-free)
  - caveat: adj_close is restated retroactively for dividends and splits, so adjusted levels are not strictly point-in-time; returns are standard practice but embed later corporate-action information
  - caveat: the endpoint is an undocumented public JSON API with no availability guarantee and no vendor support
  - caveat: prices are consolidated daily bars, not the venue-level quotes an execution model would eventually need

## SEC Form-4 raw capture (P0 acquisition lane)

- collector `BLOCKED`: SEC user agent/contact not configured; capture fails closed
- liveness: **COLLECTOR_DID_NOT_RUN**, last attempt never, last validated discovery never
- coverage: **COVERAGE_UNKNOWN** - no validated discovery poll has completed yet
- last result: `none`
- continuity cursor: `not established`
- work in flight: no
- raw store: 0 bytes, append-only True, content-addressed True, incomplete evidence present False
- request policy: None req/s cap (SEC documented maximum None), concurrency None, poll Nones, backoff None
- cooldown: none, requests spent 0
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
  - out of sample: -6.08% net, beta -0.062, turnover 33x/yr, t=-0.39 against a required 3.20
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 76 rebalances, 301 no-trade, 0 vetoed

## Strongest evidence and rejections

Latest lesson: xs_momentum_l21_z0.5_h5_b0.05 was rejected out of sample (-6.08% net). The signal was gross-negative (-1.37%), so the hypothesis itself is wrong here, not merely too expensive to trade. Its t-statistic of -0.39 is far below the 3.20 required after 36 expressions were tried on this dataset, so the result is indistinguishable from search luck. Market beta was -0.062 against a benchmark that returned +38.34%, so -2.37% of the result is passive exposure rather than skill.

Lessons recorded: 5.

Lane priorities after learning: `xs_daily_relative_value` 24.0, `xs_execution_aware_relative_value` 24.0

## Capital state

- authoritative ledger `quant-shadow-book` (CAPITAL, paper_shadow)
- NAV 1,000,000.00 USD from 1,000,000.00 initial (+0.00%)
- cash 1,000,000.00, realized 0.00, fees 0.00
- 0 open positions, gross 0.00x, net +0.000x
- 377 sessions marked, 0 fills, inception 2025-03-13, last 2026-09-11

## Decision quality

- evaluation ledger NAV 993,757.74 (-0.62%) over 377 sessions and 521 fills
- rejections scored: 1 (true rejects 0, false rejects 0, undetermined 1)
- counterfactual P&L of rejected strategies: -6,242.26
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

----- CONTENT END -----
===== END DOCUMENT 001 =====

===== DOCUMENT 002 =====
BLOB: a53c8a617d6fa215a3202e3cdfab2c8f494d21d4
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 1
PATHS: CHIEF_BRIEF.md
BYTES: 5586
ENCODING_STATUS: UTF8
SHA256_CONTENT: 63a887724a07c5a289de33a92aff176d91d8b9aceefffcdae64afceb49c84b1e
----- CONTENT START -----
# Chief Brief

Generated from persistent system state. Do not edit by hand: `python3 scripts/quant.py brief` regenerates it.

- generated at: 2026-09-13T19:57:54.066122+00:00
- system: `quant-system-v1` in `paper_shadow` mode, status `IDLE`
- boots: 1, ticks: 382, research runs: 2, desk sessions: 378

## System health

No open faults.

Component state:

- `BOOK`: **IDLE** - marked through 2026-09-11
- `BUILD`: **BLOCKED** - 3 open capability gaps
- `CONTROL`: **IDLE** - no work due
- `DATA`: **IDLE** - 2 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 2, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **us_sector_etf_daily** (AVAILABLE) - 30,168 rows, 12 symbols, 2016-09-12 to 2026-09-11, `sha256:97b4653ca827809162f21f0cee47f76e28b1ed5cc5ef2278e4e8a7681d7aa1ab`
  - source: Yahoo Finance chart API (public, credential-free)
  - caveat: adj_close is restated retroactively for dividends and splits, so adjusted levels are not strictly point-in-time; returns are standard practice but embed later corporate-action information
  - caveat: the endpoint is an undocumented public JSON API with no availability guarantee and no vendor support
  - caveat: prices are consolidated daily bars, not the venue-level quotes an execution model would eventually need

## Research

Queue: `{'PENDING': 0, 'RUNNING': 0, 'BLOCKED': 3, 'COMPLETED': 2, 'FAILED': 0}`.

- `RESEARCH-XS-EXECUTION-AWARE-RELATIVE-VALUE` - **COMPLETED** REJECT_RESEARCH
- `RESEARCH-XS-DAILY-RELATIVE-VALUE` - **COMPLETED** REJECT_RESEARCH
- `SCAN-FACTOR-RESIDUAL-001` - **BLOCKED** no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` - **BLOCKED** point-in-time filing feed absent
- `SCAN-VOLATILITY-SURFACE-001` - **BLOCKED** historical option chains, quotes, rates, dividends, and corporate actions absent

Strategy lifecycle: `RESEARCH` 2

- **STR-XS-DAILY-RELATIVE-VALUE-xs_momentum_l21_z0.5_h1_b0** - lifecycle `RESEARCH`, evaluation track
  - out of sample: -13.16% net, beta -0.070, turnover 75x/yr, t=-0.97 against a required 3.08
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 375 rebalances, 0 no-trade, 2 vetoed
- **STR-XS-EXECUTION-AWARE-RELATIVE-VALUE-xs_momentum_l21_z0.5_h5_b0.05** - lifecycle `RESEARCH`, evaluation track
  - out of sample: -7.27% net, beta -0.063, turnover 33x/yr, t=-0.49 against a required 3.20
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 76 rebalances, 301 no-trade, 0 vetoed

## Strongest evidence and rejections

Latest lesson: xs_momentum_l21_z0.5_h5_b0.05 was rejected out of sample (-7.27% net). The signal was gross-negative (-2.61%), so the hypothesis itself is wrong here, not merely too expensive to trade. Its t-statistic of -0.49 is far below the 3.20 required after 36 expressions were tried on this dataset, so the result is indistinguishable from search luck. Market beta was -0.063 against a benchmark that returned +35.91%, so -2.26% of the result is passive exposure rather than skill.

Lessons recorded: 5.

Lane priorities after learning: `xs_daily_relative_value` 24.0, `xs_execution_aware_relative_value` 24.0

## Capital state

- authoritative ledger `quant-shadow-book` (CAPITAL, paper_shadow)
- NAV 1,000,000.00 USD from 1,000,000.00 initial (+0.00%)
- cash 1,000,000.00, realized 0.00, fees 0.00
- 0 open positions, gross 0.00x, net +0.000x
- 378 sessions marked, 0 fills, inception 2025-03-12, last 2026-09-11

## Decision quality

- evaluation ledger NAV 983,622.24 (-1.64%) over 378 sessions and 2690 fills
- rejections scored: 2 (true rejects 0, false rejects 0, undetermined 2)
- counterfactual P&L of rejected strategies: -16,377.76
- desk tickets: {'BOOKED': 451, 'NO_TRADE': 301, 'VETOED': 2, 'BLOCKED': 2}

## Blockers and capability gaps

- `SCAN-FACTOR-RESIDUAL-001` blocked: no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` blocked: point-in-time filing feed absent
- `SCAN-VOLATILITY-SURFACE-001` blocked: historical option chains, quotes, rates, dividends, and corporate actions absent
- build task `BUILD-SCAN-FACTOR-RESIDUAL-001`: point-in-time dataset for the factor_residual lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-FACTOR-RESIDUAL-001)
- build task `BUILD-SCAN-INSIDER-FILINGS-001`: point-in-time dataset for the insider_filings lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-INSIDER-FILINGS-001)
- build task `BUILD-SCAN-VOLATILITY-SURFACE-001`: point-in-time dataset for the volatility_surface lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-VOLATILITY-SURFACE-001)

## Next autonomous action

blocked on a dependency for SCAN-FACTOR-RESIDUAL-001: no survivorship-controlled security and factor panel


----- CONTENT END -----
===== END DOCUMENT 002 =====

===== DOCUMENT 003 =====
BLOB: aa787f307c47fd3b7d97aec7f4d51fccafa22b3b
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 1
PATHS: CHIEF_BRIEF.md
BYTES: 10503
ENCODING_STATUS: UTF8
SHA256_CONTENT: c7b0d3fc4bf08728a3268064631b1b58b7c84b78405580abcecc637b5dc5d863
----- CONTENT START -----
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

----- CONTENT END -----
===== END DOCUMENT 003 =====

===== DOCUMENT 004 =====
BLOB: d17c432b6f1b9b4c834f427e10ff4301b3774a4a
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 1
PATHS: CHIEF_BRIEF.md
BYTES: 6011
ENCODING_STATUS: UTF8
SHA256_CONTENT: 80a912d93c3086c62059e6e7c09528c072c861b6039141632bc7fa63fd31a0ed
----- CONTENT START -----
# Chief Brief

Generated from persistent system state. Do not edit by hand: `python3 scripts/quant.py brief` regenerates it.

- canonical state basis: clean persistent replay of committed inputs through 2026-09-11
- system: `quant-system-v1` in `paper_shadow` mode, status `IDLE`
- boots: 1, ticks: 381, research runs: 2, desk sessions: 377

## System health

No open faults.

Component state:

- `BOOK`: **IDLE** - marked through 2026-09-11
- `BUILD`: **BLOCKED** - 3 open capability gaps
- `CONTROL`: **IDLE** - no work due
- `DATA`: **IDLE** - 2 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SEC_CAPTURE`: **BLOCKED** - SEC user agent/contact not configured; capture fails closed
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 2, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **us_sector_etf_daily** (AVAILABLE) - 30,168 rows, 12 symbols, 2016-09-12 to 2026-09-11, `sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1`
  - source: Yahoo Finance chart API (public, credential-free)
  - caveat: adj_close is restated retroactively for dividends and splits, so adjusted levels are not strictly point-in-time; returns are standard practice but embed later corporate-action information
  - caveat: the endpoint is an undocumented public JSON API with no availability guarantee and no vendor support
  - caveat: prices are consolidated daily bars, not the venue-level quotes an execution model would eventually need

## SEC Form-4 raw capture (P0 acquisition lane)

- collector `BLOCKED`: SEC user agent/contact not configured; capture fails closed
- liveness: **COLLECTOR_DID_NOT_RUN**, last attempt never, last validated discovery never
- coverage: **COVERAGE_UNKNOWN** - no validated discovery poll has completed yet
- last result: `none`
- continuity cursor: `not established`
- work in flight: no
- raw store: 0 bytes, append-only True, content-addressed True, incomplete evidence present False
- request policy: None req/s cap (SEC documented maximum None), concurrency None, poll Nones, backoff None
- cooldown: none, requests spent 0
- states: `CAPTURED` / `NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL` / `NOT_ADMISSIBLE_FOR_CONFIRMATION`

## Research

Queue: `{'PENDING': 0, 'RUNNING': 0, 'BLOCKED': 3, 'COMPLETED': 2, 'FAILED': 0}`.

- `RESEARCH-XS-EXECUTION-AWARE-RELATIVE-VALUE` - **COMPLETED** REJECT_RESEARCH
- `RESEARCH-XS-DAILY-RELATIVE-VALUE` - **COMPLETED** FILTERED
- `SCAN-FACTOR-RESIDUAL-001` - **BLOCKED** no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` - **BLOCKED** point-in-time filing feed absent
- `SCAN-VOLATILITY-SURFACE-001` - **BLOCKED** historical option chains, quotes, rates, dividends, and corporate actions absent

Strategy lifecycle: `RESEARCH` 1

- **STR-XS-EXECUTION-AWARE-RELATIVE-VALUE-xs_momentum_l21_z0.5_h5_b0.05** - lifecycle `RESEARCH`, evaluation track
  - out of sample: -6.08% net, beta -0.062, turnover 33x/yr, t=-0.39 against a required 3.20
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 76 rebalances, 301 no-trade, 0 vetoed

## Strongest evidence and rejections

Latest lesson: xs_momentum_l21_z0.5_h5_b0.05 was rejected out of sample (-6.08% net). The signal was gross-negative (-1.37%), so the hypothesis itself is wrong here, not merely too expensive to trade. Its t-statistic of -0.39 is far below the 3.20 required after 36 expressions were tried on this dataset, so the result is indistinguishable from search luck. Market beta was -0.062 against a benchmark that returned +38.34%, so -2.37% of the result is passive exposure rather than skill.

Lessons recorded: 5.

Lane priorities after learning: `xs_daily_relative_value` 24.0, `xs_execution_aware_relative_value` 24.0

## Capital state

- authoritative ledger `quant-shadow-book` (CAPITAL, paper_shadow)
- NAV 1,000,000.00 USD from 1,000,000.00 initial (+0.00%)
- cash 1,000,000.00, realized 0.00, fees 0.00
- 0 open positions, gross 0.00x, net +0.000x
- 377 sessions marked, 0 fills, inception 2025-03-13, last 2026-09-11

## Decision quality

- evaluation ledger NAV 993,757.74 (-0.62%) over 377 sessions and 521 fills
- rejections scored: 1 (true rejects 0, false rejects 0, undetermined 1)
- counterfactual P&L of rejected strategies: -6,242.26
- desk tickets: {'BOOKED': 76, 'NO_TRADE': 301}

## Blockers and capability gaps

- `SCAN-FACTOR-RESIDUAL-001` blocked: no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` blocked: point-in-time filing feed absent
- `SCAN-VOLATILITY-SURFACE-001` blocked: historical option chains, quotes, rates, dividends, and corporate actions absent
- build task `BUILD-SCAN-FACTOR-RESIDUAL-001`: point-in-time dataset for the factor_residual lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-FACTOR-RESIDUAL-001)
- build task `BUILD-SCAN-INSIDER-FILINGS-001`: point-in-time dataset for the insider_filings lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-INSIDER-FILINGS-001)
- build task `BUILD-SCAN-VOLATILITY-SURFACE-001`: point-in-time dataset for the volatility_surface lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-VOLATILITY-SURFACE-001)

## Next autonomous action

blocked on a dependency for SCAN-FACTOR-RESIDUAL-001: no survivorship-controlled security and factor panel

----- CONTENT END -----
===== END DOCUMENT 004 =====

===== DOCUMENT 005 =====
BLOB: de973fcf93950655a1c695e48bff12e4e4e3101f
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 2
PATHS: CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/de973fcf93950655a1c695e48bff12e4e4e3101f.txt
BYTES: 11822
ENCODING_STATUS: UTF8
SHA256_CONTENT: f31cbcda4ed3fc095d96ddb9721d8df26f632de6adc8516f9abf86b040a036bf
----- CONTENT START -----
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
- `DATA`: **IDLE** - 7 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SEC_CAPTURE`: **BLOCKED** - SEC identity/contact not configured
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 7, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

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
- **perp_funding_hl_dydx_daily** (AVAILABLE) - 156,628 rows, 286 symbols, 2023-11-13 to 2026-09-24, `sha256:68a2ac4be84a133dcbb7af2aba28fc21b58eac7ca51ddd443cf15396475a8e22`
  - source: Hyperliquid public info API (meta, fundingHistory, candleSnapshot 1d) + dYdX v4 public indexer (perpetualMarkets, historicalFunding, candles 1DAY); 7959 responses, sha256 per response in data/fast_rail/h002/provenance.jsonl.gz
  - caveat: venue APIs queried directly; not independently cross-checked against a third-party archive
  - caveat: delisted coins are included where both venues still serve history (Hyperliquid meta isDelisted, dYdX FINAL_SETTLEMENT)
  - caveat: a day is kept only with >= 22 hourly settlements and a traded daily candle on both venues; nothing is filled in
  - caveat: close is the daily candle's last trade; thin dYdX markets can print stale closes, which adds cross-venue price noise to the pair
  - caveat: prices are per price_scale tokens (data/fast_rail/h002/coins.json) and Hyperliquid k-coins are converted to per-token; returns are unaffected
  - caveat: HL volume notional = base volume x daily close (approximation)
  - caveat: no intraday margin, liquidation or auto-deleveraging modelling in the data
  - caveat: coin names are matched by ticker; a re-used ticker would pair different assets
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

----- CONTENT END -----
===== END DOCUMENT 005 =====

===== DOCUMENT 006 =====
BLOB: e6e123c271303216d626de5aa3a234915da92d9c
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 1
PATHS: CHIEF_BRIEF.md
BYTES: 5191
ENCODING_STATUS: UTF8
SHA256_CONTENT: 4d1953e2c98853d4f7ad1050c368da8cfb9b06e0ee9946a63645f1eb68b7670e
----- CONTENT START -----
# Chief Brief

Generated from persistent system state. Do not edit by hand: `python3 scripts/quant.py brief` regenerates it.

- generated at: 2026-09-13T20:59:15.811204+00:00
- system: `quant-system-v1` in `paper_shadow` mode, status `IDLE`
- boots: 2, ticks: 385, research runs: 2, desk sessions: 378

## System health

No open faults.

Component state:

- `BOOK`: **IDLE** - marked through 2026-09-11
- `BUILD`: **BLOCKED** - 3 open capability gaps
- `CONTROL`: **IDLE** - no work due
- `DATA`: **IDLE** - 2 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 2, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **us_sector_etf_daily** (AVAILABLE) - 30,168 rows, 12 symbols, 2016-09-12 to 2026-09-11, `sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1`
  - source: Yahoo Finance chart API (public, credential-free)
  - caveat: adj_close is restated retroactively for dividends and splits, so adjusted levels are not strictly point-in-time; returns are standard practice but embed later corporate-action information
  - caveat: the endpoint is an undocumented public JSON API with no availability guarantee and no vendor support
  - caveat: prices are consolidated daily bars, not the venue-level quotes an execution model would eventually need

## Research

Queue: `{'PENDING': 0, 'RUNNING': 0, 'BLOCKED': 3, 'COMPLETED': 2, 'FAILED': 0}`.

- `RESEARCH-XS-EXECUTION-AWARE-RELATIVE-VALUE` - **COMPLETED** REJECT_RESEARCH
- `RESEARCH-XS-DAILY-RELATIVE-VALUE` - **COMPLETED** FILTERED
- `SCAN-FACTOR-RESIDUAL-001` - **BLOCKED** no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` - **BLOCKED** point-in-time filing feed absent
- `SCAN-VOLATILITY-SURFACE-001` - **BLOCKED** historical option chains, quotes, rates, dividends, and corporate actions absent

Strategy lifecycle: `RESEARCH` 1

- **STR-XS-EXECUTION-AWARE-RELATIVE-VALUE-xs_momentum_l21_z0.5_h5_b0.05** - lifecycle `RESEARCH`, evaluation track
  - out of sample: -6.08% net, beta -0.062, turnover 33x/yr, t=-0.39 against a required 3.20
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 76 rebalances, 301 no-trade, 0 vetoed

## Strongest evidence and rejections

Latest lesson: xs_momentum_l21_z0.5_h5_b0.05 was rejected out of sample (-6.08% net). The signal was gross-negative (-1.37%), so the hypothesis itself is wrong here, not merely too expensive to trade. Its t-statistic of -0.39 is far below the 3.20 required after 36 expressions were tried on this dataset, so the result is indistinguishable from search luck. Market beta was -0.062 against a benchmark that returned +38.34%, so -2.37% of the result is passive exposure rather than skill.

Lessons recorded: 5.

Lane priorities after learning: `xs_daily_relative_value` 24.0, `xs_execution_aware_relative_value` 24.0

## Capital state

- authoritative ledger `quant-shadow-book` (CAPITAL, paper_shadow)
- NAV 1,000,000.00 USD from 1,000,000.00 initial (+0.00%)
- cash 1,000,000.00, realized 0.00, fees 0.00
- 0 open positions, gross 0.00x, net +0.000x
- 377 sessions marked, 0 fills, inception 2025-03-13, last 2026-09-11

## Decision quality

- evaluation ledger NAV 993,742.87 (-0.63%) over 377 sessions after execution-time revaluation
- rejections scored: 1 (true rejects 0, false rejects 0, undetermined 1)
- counterfactual P&L of rejected strategies: -6,165.57
- desk tickets: {'BOOKED': 76, 'NO_TRADE': 301, 'BLOCKED': 1}

## Blockers and capability gaps

- `SCAN-FACTOR-RESIDUAL-001` blocked: no survivorship-controlled security and factor panel
- `SCAN-INSIDER-FILINGS-001` blocked: point-in-time filing feed absent
- `SCAN-VOLATILITY-SURFACE-001` blocked: historical option chains, quotes, rates, dividends, and corporate actions absent
- build task `BUILD-SCAN-FACTOR-RESIDUAL-001`: point-in-time dataset for the factor_residual lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-FACTOR-RESIDUAL-001)
- build task `BUILD-SCAN-INSIDER-FILINGS-001`: point-in-time dataset for the insider_filings lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-INSIDER-FILINGS-001)
- build task `BUILD-SCAN-VOLATILITY-SURFACE-001`: point-in-time dataset for the volatility_surface lane (acceptance: a validated, fingerprinted dataset unblocks SCAN-VOLATILITY-SURFACE-001)

## Next autonomous action

blocked on a dependency for SCAN-FACTOR-RESIDUAL-001: no survivorship-controlled security and factor panel

----- CONTENT END -----
===== END DOCUMENT 006 =====

===== DOCUMENT 007 =====
BLOB: f06094ba74612da38972619ffc7b65b8fa670bab
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 1
PATHS: CHIEF_BRIEF.md
BYTES: 7336
ENCODING_STATUS: UTF8
SHA256_CONTENT: 0976a6deab551ac120687cfa384e3944a68b25062792ddaf110c13fe13d74fd3
----- CONTENT START -----
# Chief Brief

Generated from persistent system state. Do not edit by hand: `python3 scripts/quant.py brief` regenerates it.

- canonical state basis: clean persistent replay of committed inputs through 2026-09-11
- system: `quant-system-v1` in `paper_shadow` mode, status `IDLE`
- boots: 1, ticks: 381, research runs: 2, desk sessions: 377

## System health

No open faults.

Component state:

- `BOOK`: **IDLE** - marked through 2026-09-11
- `BUILD`: **BLOCKED** - 3 open capability gaps
- `CONTROL`: **IDLE** - no work due
- `DATA`: **IDLE** - 3 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SEC_CAPTURE`: **BLOCKED** - SEC identity/contact not configured
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 3, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

- **futures_excess_return_daily** (AVAILABLE) - 177,419 rows, 31 symbols, 2002-01-02 to 2024-03-28, `sha256:9489b9cf4346ed3ecd389d4983c15380172985ef382945f411c841ead5a75981`
  - source: https://github.com/pst-group/pysystemtrade data/futures (adjusted_prices_csv, multiple_prices_csv, csvconfig) @ 8958c49c38b1e4a8c07f0e4375d5e9cb68a087f7
  - caveat: third-party research data (pysystemtrade repository), not an exchange feed; not independently verified against exchange settlements
  - caveat: universe is today's liquid contract list: instruments that were delisted before the snapshot are absent (mild survivorship)
  - caveat: returns are in each contract's local currency; P&L currency translation (second order for a margined futures position) is not modelled
  - caveat: volume is unavailable and written as 0: execution capacity is NOT modelled
  - caveat: index excludes collateral interest: every return is an excess return over cash
  - caveat: roll costs use the repository's current spread and commission estimates for the whole history, which likely understates early-2000s costs
  - caveat: a market closed on a shared session carries its last level forward for at most 5 sessions and is flagged stale=1
- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **us_sector_etf_daily** (AVAILABLE) - 30,168 rows, 12 symbols, 2016-09-12 to 2026-09-11, `sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1`
  - source: Yahoo Finance chart API (public, credential-free)
  - caveat: adj_close is restated retroactively for dividends and splits, so adjusted levels are not strictly point-in-time; returns are standard practice but embed later corporate-action information
  - caveat: the endpoint is an undocumented public JSON API with no availability guarantee and no vendor support
  - caveat: prices are consolidated daily bars, not the venue-level quotes an execution model would eventually need

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
  - out of sample: -6.08% net, beta -0.062, turnover 33x/yr, t=-0.39 against a required 3.20
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 76 rebalances, 301 no-trade, 0 vetoed

## Strongest evidence and rejections

Latest lesson: xs_momentum_l21_z0.5_h5_b0.05 was rejected out of sample (-6.08% net). The signal was gross-negative (-1.37%), so the hypothesis itself is wrong here, not merely too expensive to trade. Its t-statistic of -0.39 is far below the 3.20 required after 36 expressions were tried on this dataset, so the result is indistinguishable from search luck. Market beta was -0.062 against a benchmark that returned +38.34%, so -2.37% of the result is passive exposure rather than skill.

Lessons recorded: 5.

Lane priorities after learning: `xs_daily_relative_value` 24.0, `xs_execution_aware_relative_value` 24.0

## Capital state

- authoritative ledger `quant-shadow-book` (CAPITAL, paper_shadow)
- NAV 1,000,000.00 USD from 1,000,000.00 initial (+0.00%)
- cash 1,000,000.00, realized 0.00, fees 0.00
- 0 open positions, gross 0.00x, net +0.000x
- 377 sessions marked, 0 fills, inception 2025-03-13, last 2026-09-11

## Decision quality

- evaluation ledger NAV 993,757.74 (-0.62%) over 377 sessions and 521 fills
- rejections scored: 1 (true rejects 0, false rejects 0, undetermined 1)
- counterfactual P&L of rejected strategies: -6,242.26
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

----- CONTENT END -----
===== END DOCUMENT 007 =====

===== DOCUMENT 008 =====
BLOB: fd8480820bcaf491fa5ffae734efb53c4011ce4a
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 13
PATHS: CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/fd8480820bcaf491fa5ffae734efb53c4011ce4a.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/default/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/CHIEF_BRIEF.md
BYTES: 6117
ENCODING_STATUS: UTF8
SHA256_CONTENT: ea51dce2437bd9de17b7782a0ee3cb82a7200cca5a04b3d313c5779b15aa1c1b
----- CONTENT START -----
# Chief Brief

Generated from persistent system state. Do not edit by hand: `python3 scripts/quant.py brief` regenerates it.

- canonical state basis: clean persistent replay of committed inputs through 2026-09-11
- system: `quant-system-v1` in `paper_shadow` mode, status `IDLE`
- boots: 1, ticks: 381, research runs: 2, desk sessions: 377

## System health

No open faults.

Component state:

- `BOOK`: **IDLE** - marked through 2026-09-11
- `BUILD`: **BLOCKED** - 3 open capability gaps
- `CONTROL`: **IDLE** - no work due
- `DATA`: **IDLE** - 2 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SEC_CAPTURE`: **BLOCKED** - SEC identity/contact not configured
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 2, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **us_sector_etf_daily** (AVAILABLE) - 30,168 rows, 12 symbols, 2016-09-12 to 2026-09-11, `sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1`
  - source: Yahoo Finance chart API (public, credential-free)
  - caveat: adj_close is restated retroactively for dividends and splits, so adjusted levels are not strictly point-in-time; returns are standard practice but embed later corporate-action information
  - caveat: the endpoint is an undocumented public JSON API with no availability guarantee and no vendor support
  - caveat: prices are consolidated daily bars, not the venue-level quotes an execution model would eventually need

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
  - out of sample: -6.08% net, beta -0.062, turnover 33x/yr, t=-0.39 against a required 3.20
  - failed: net_profitable_after_modeled_costs, profitable_in_both_subperiods, still_profitable_at_2x_costs, t_statistic_survives_multiple_testing
  - desk: 76 rebalances, 301 no-trade, 0 vetoed

## Strongest evidence and rejections

Latest lesson: xs_momentum_l21_z0.5_h5_b0.05 was rejected out of sample (-6.08% net). The signal was gross-negative (-1.37%), so the hypothesis itself is wrong here, not merely too expensive to trade. Its t-statistic of -0.39 is far below the 3.20 required after 36 expressions were tried on this dataset, so the result is indistinguishable from search luck. Market beta was -0.062 against a benchmark that returned +38.34%, so -2.37% of the result is passive exposure rather than skill.

Lessons recorded: 5.

Lane priorities after learning: `xs_daily_relative_value` 24.0, `xs_execution_aware_relative_value` 24.0

## Capital state

- authoritative ledger `quant-shadow-book` (CAPITAL, paper_shadow)
- NAV 1,000,000.00 USD from 1,000,000.00 initial (+0.00%)
- cash 1,000,000.00, realized 0.00, fees 0.00
- 0 open positions, gross 0.00x, net +0.000x
- 377 sessions marked, 0 fills, inception 2025-03-13, last 2026-09-11

## Decision quality

- evaluation ledger NAV 993,757.74 (-0.62%) over 377 sessions and 521 fills
- rejections scored: 1 (true rejects 0, false rejects 0, undetermined 1)
- counterfactual P&L of rejected strategies: -6,242.26
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

----- CONTENT END -----
===== END DOCUMENT 008 =====

===== DOCUMENT 009 =====
BLOB: fe1a499b0c5d97f70b7d80c7dda3e5ee356687ad
REPRESENTATIVE_PATH: CHIEF_BRIEF.md
PATH_COUNT: 2
PATHS: CHIEF_BRIEF.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/fe1a499b0c5d97f70b7d80c7dda3e5ee356687ad.txt
BYTES: 12414
ENCODING_STATUS: UTF8
SHA256_CONTENT: 12880fb0248514714bd64c697d660acc745fa2a15fde5990fe338dc09515caec
----- CONTENT START -----
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
- `DATA`: **IDLE** - 8 datasets available
- `FILLS`: **IDLE** - no session due
- `LEARNING`: **IDLE** - 5 lessons recorded
- `RESEARCH`: **BLOCKED** - no survivorship-controlled security and factor panel
- `RISK`: **IDLE** - no session due
- `SCAN`: **IDLE** - no session due
- `SEC_CAPTURE`: **BLOCKED** - SEC identity/contact not configured
- `SIZE`: **IDLE** - no session due
- `VET`: **IDLE** - no session due

## Data

Registry health: `{'AVAILABLE': 8, 'STALE': 0, 'INVALID': 0, 'MISSING': 0}`.

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
- **hl_listings_daily** (AVAILABLE) - 10,844 rows, 222 symbols, 2023-06-08 to 2026-09-26, `sha256:875483cc9343b113b6d7a7592c4241c34a6739eff884df3bc7047509ff8e02a6`
  - source: Hyperliquid public info API (POST https://api.hyperliquid.xyz/info: meta incl. isDelisted, candleSnapshot 1d, fundingHistory); raw responses and manifest in data/raw/fast_rail/h006
  - caveat: main-dex perps only (HIP-3 builder-deployed dexs excluded)
  - caveat: coins first traded before 2023-06-01 are incumbents at API history start and are never new listings
  - caveat: coins covered only from listing to listing + 45 days; HL.BTC over the whole funding history
  - caveat: delisted coins included (55 with rows): no survivorship by construction
  - caveat: listing day itself is partial and usually dropped (< 22 funding prints)
  - caveat: coins that ever closed below 1 USD are quoted per 1000 units (price_scale=1000) so six-decimal storage keeps return precision; volume is USD notional
  - caveat: no intraday margin, liquidation, auto-deleveraging or borrow modelling
  - caveat: 209 eligible listings in meta
- **nasdaq_composite_daily** (AVAILABLE) - 1,251 rows, 1 symbols, 2021-07-13 to 2026-07-10, `sha256:ba0a84803fee43f4b6b984d86a93d23c7b73e8a2630fa4e8e6e55290769d6a14`
  - source: operator-supplied historical export committed to the repository
  - caveat: price index without dividends; not a tradable instrument
  - caveat: no corporate-action or constituent history
- **perp_funding_hl_dydx_daily** (AVAILABLE) - 10,416 rows, 10 symbols, 2023-11-13 to 2026-09-26, `sha256:d8dcbbc1f5886203a7792f80fed6b2340db1c0a26e95f0e015ef0adb0d38ace9`
  - source: api.hyperliquid.xyz/info (fundingHistory, candleSnapshot 1d) + indexer.dydx.trade/v4 (historicalFunding, candles 1DAY); raw responses in data/raw/fast_rail/h002 with manifest.json (url, fetched_at, sha256)
  - caveat: venue APIs fetched once at build time; a later refetch may differ if a venue revises history
  - caveat: survivorship: only coins listed on both venues at fetch time
  - caveat: universe chosen by trailing median notional on both venues (volume only)
  - caveat: no intraday margin, liquidation or auto-deleveraging modelling in the data
  - caveat: dYdX v4 volumes are thin; capacity is bound by the dYdX leg
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

----- CONTENT END -----
===== END DOCUMENT 009 =====

===== DOCUMENT 010 =====
BLOB: 02b0cdbe57e3b58a34ffdf837ae16df5a4a0be0e
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 2
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/02b0cdbe57e3b58a34ffdf837ae16df5a4a0be0e.txt
BYTES: 6029
ENCODING_STATUS: UTF8
SHA256_CONTENT: 4b2e44f87bb7405582b6ab8f9beae4191bd97c37a9e1cdac3648903a5498ece3
----- CONTENT START -----
# Quant - Claude Code operating context

This file is intentionally short because Claude Code loads it every session. Put standing project rules here and task procedures in `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal project objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` is the highest authority.

Do not redefine Quant around the subsystem currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No real-capital authority is granted by this file. Current engineering work remains paper/shadow unless the project owner explicitly changes that boundary.

## Current authority / restart surface

Before substantial work:
1. Read `QUANT_NORTH_STAR.md`.
2. Read `NEXT_BUILD_MISSION.md` (compact live router).
3. Read `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` (live state file; its content is newer than its filename).
4. Read `handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md`.
5. Check pending, not-yet-ratified owner-delegated decisions: `handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md` (evidence: `handoff/CLAUDE_PROJECT_REVIEW_AUDIT_2026-09-23.md`).
6. Read the exact branch-specific mission/handoff named by current Blue governance, after verifying its live branch HEAD and CI (branch heads can be newer than master governance).
7. Read only the architecture, code and tests relevant to that exact mission.

`handoff/BLUE_MASTER_V2_STATE_2026-09-20.md` and `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md` are historical snapshots, not restart authority.

`STATE.md` and `CHIEF_BRIEF.md` are runtime/research snapshots, not current project-routing authority.
`CLAUDE_CURRENT_MISSION.md` is now a router and must not contain a frozen historical mission.
The repository default branch is currently historical and is not authority.

Do not import the whole of `AGENTS.md` into every session; use the current governance files above as the compact routing surface.

## Builder role

Claude Code is the Builder / Quant Engineer. Choose local implementation details autonomously, but do not redefine the product around the easiest component to finish.

Prefer coherent capability over local elegance. Avoid extra abstractions, files, agents and refactors unless they directly advance the current mission or repair a demonstrated invariant.

Ordinary coding failures, negative research results and blocked research lanes are not project stop conditions. Record them and continue with the highest-value executable work.

## Integrity invariants

Use one causal information timeline across research, paper/shadow decisions and the Book. Research evidence must describe the executable paper/shadow strategy rather than a more favorable backtest object.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate them separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

A state enum is not a capability. Do not claim decay management, historical strategy versioning, liveness or other behavior unless evidence actually drives it.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

## Ultracode / multi-agent discipline

Project settings enable Ultracode with a small workflow size guideline. Use parallel agents when workstreams are genuinely independent, need isolated context or benefit from adversarial review.

Do not spawn agents for trivial reads, one-file edits, sequential debugging or work that requires one shared evolving state.

For substantive changes, separate implementation from independent economic/research-integrity and runtime/restart review, then synthesize once in the lead agent.

Avoid duplicated exploration. Give each agent one distinct question and require a concise result.

## Token discipline

Use targeted search and file slices before full-file reads. Do not repeatedly restate architecture or facts already established in the repository.

Do not revisit a settled implementation choice unless new evidence contradicts it or a test fails.

Keep progress updates short. Put durable truth in code, tests, `STATE.md` and generated artifacts rather than long chat summaries.

Use `/compact` or a fresh session when the task changes materially. Use `/quant-orient` after branch/context changes instead of rereading everything manually.

## Verification

Normal V1 verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
```

Passing tests is necessary, not sufficient. Add adversarial tests for the specific failure mode being repaired. Use `/quant-proof` before declaring a major milestone complete.

## Git behavior

Follow the exact branch ownership and mutation permissions in the current Blue mission/handoff. Do not infer a current PR or branch from historical files.

Do not merge, force-push, delete branches, move frozen refs or perform irreversible external actions unless the current mission explicitly authorizes that operation.

Commit coherent checkpoints and keep durable mission state in GitHub rather than chat.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, experiment, worker, lane or subsystem completed or failed.

----- CONTENT END -----
===== END DOCUMENT 010 =====

===== DOCUMENT 011 =====
BLOB: 0dc20cc5e6ca00bc28e67a13f24ae2b62e9258d7
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 3
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/0dc20cc5e6ca00bc28e67a13f24ae2b62e9258d7.txt | audit/owner-recovery/20261026/pass-01/snapshots/default/CLAUDE.md
BYTES: 4254
ENCODING_STATUS: UTF8
SHA256_CONTENT: dd1479f22f583edcdbbbbb97f68dc0407f40fa6c81367f70feabee82e120f10b
----- CONTENT START -----
# Quant-Trade — Claude operating context

Keep this file compact. It is a standing router, not a frozen mission.

## Mandatory orientation

Before substantial work:

1. read `QUANT_NORTH_STAR.md`;
2. read `governance/CURRENT_PROJECT_STATE_2026-10-20.md`;
3. read CP12 on `audit/forensic-checkpoint-20261019`;
4. resolve the exact current branch + live HEAD;
5. read only branch-specific code/tests/evidence needed for the assigned mission.

Do **not** use September Blue handoffs, CP11, `STATE.md`, `CHIEF_BRIEF.md`, old PR text, branch age, or the default branch's code snapshot alone to infer current authority.

## Current lines

- Oracle H24 V1: `builder/oracle-economic-loop-recovery-20261019` — `LIVE_RUNTIME_V1`;
- Oracle V2 Core: `builder/oracle-v2-core-20261020` — `LIVE_V2_BUILD`;
- Live Lab: current Oracle canonical/integration rails — `RECONCILIATION_REQUIRED`;
- audit: `audit/forensic-checkpoint-20261019` — CP10 scientific/runtime baseline + CP12 organizational/cleanup authority;
- default `blue/master-v2-2026-09-20`: temporary routing/historical portal, not latest implementation authority.

V1 and V2 may advance concurrently. Always reacquire HEAD immediately before writes.

## CP12 cleanup rule

`CHECKPOINT_011.md` is superseded preliminary work for deletion decisions.

The old mass-cleanup scripts are intentionally disabled.

Do not delete/archive a diverged branch merely because a later-looking V2 branch exists. CP12 has proven material unabsorbed sources including Research Factory Core, Evidence/Identity, SEC Census, aggressive Research OS, Edge Lab, Legacy reconciliation and Design V1, plus unresolved Live Lab and Weather consolidation.

Current semantic registries are on the audit branch:

- `governance/WORKSTREAM_INDEX_2026-10-20.md`
- `governance/OWNER_DECISIONS_2026-10-20.md`
- `governance/SCIENTIFIC_MEMORY_INDEX_2026-10-20.md`
- `governance/WORKFLOW_DISPOSITION_2026-10-20.md`
- `governance/REPOSITORY_AUTHORITY_REGISTRY_2026-10-20.md`

Current V2 policy keeps `destructive_git_operations_authorized = false`.

## Permanent authority boundary

Unless a later explicit Owner artifact changes it:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Operational qualification, CI/tests, validator/Astra PASS, frozen hypotheses, model output or repository cleanup grant none of these authorities.

## Scientific/runtime invariants

- never fabricate data/evidence;
- preserve PIT timing, source provenance, exposure history and immutable historical results;
- UNKNOWN is not evidence of independence or PASS;
- structural similarity is not empirical correlation;
- absent admissible returns, empirical correlation remains unavailable/unknown and marginal portfolio contribution remains not estimated;
- preserve producer / validator-red-team / integrator separation;
- persistent mutations must be restart-safe and idempotent;
- model commentary is not scientific proof;
- negative, blocked and unexecuted experiments are scientific memory;
- one local PASS is not a family-level/economic-edge claim.

## V2 discipline

V2 Core currently strengthens scientific state/contracts on top of qualified V1 runtime mechanics. It is not evidence that all historical product/data/research capabilities have been absorbed.

Before replacing an old source, prove one of:

- `CAPABILITY_IMPORTED`;
- `SCIENTIFIC_MEMORY_INDEXED`;
- `OWNER_DECISION_INDEXED`;
- `SUPERSEDED_WITH_PROOF`;
- `EXPLICITLY_REJECTED_WITH_REASON`.

Do not spawn another competing top-level architecture.

## Branch lifecycle discipline

New temporary branches must not become permanent clutter. Every completed workstream should end in a durable disposition: active, absorbed, capability imported, scientific memory indexed, Owner decision indexed, or explicitly rejected.

Prefer coherent large milestones to micro-branch proliferation.

## Completion standard

For substantive work leave:

- exact branch + HEAD provenance;
- coherent code/evidence;
- appropriate adversarial/regression tests;
- truthful authority/result status;
- updated durable registry/routing only if state actually changed;
- clear next legitimate action.
----- CONTENT END -----
===== END DOCUMENT 011 =====

===== DOCUMENT 012 =====
BLOB: 477f74ee83ed7539b44055a3004457d919ff7be3
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 3
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/477f74ee83ed7539b44055a3004457d919ff7be3.txt | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v1/CLAUDE.md
BYTES: 10241
ENCODING_STATUS: UTF8
SHA256_CONTENT: de09e119545b8a5df69e79e9920de7b54d25615c351a23e7881e276d2006a5eb
----- CONTENT START -----
# Quant — Claude Code operating context

This file is intentionally compact because Claude Code loads it every session. Keep standing project rules here; keep task-specific procedures in the relevant mission, runtime roadmap, or `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` remains the highest project-level authority.

Do not redefine Quant around whichever subsystem is currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No file in this repository silently grants real-capital or live-trading authority.

## Current Oracle H24 operational truth

For branch `builder/oracle-economic-loop-recovery-20261019`, the canonical live roadmap is:

`research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md`

As of the verified 2026-10-20 checkpoint, Oracle H24 V1 is classified:

`ORACLE_H24_V1_OPERATIONALLY_QUALIFIED`

Qualified release:

`f3943830e20b05d926d3013501573b8b21fdace7`

V1 has verified exact-release CI, local GPT-OSS inference, durable GitHub task/receipt/artifact state, claim/lease recovery, natural systemd scheduling, a genuine VM reboot, automatic model/timer recovery, and a natural post-reboot worker transition correlated to GitHub.

Do **not** reinterpret this as proof of positive economic expectancy, scientific completeness of every research engine, Forward Farm operation, Live Lab UI completeness, real-capital safety, or live-trading readiness.

The permanent Oracle authority boundary remains:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

A future phase may change one of these only through explicit governed Owner authorization. Never infer authority from task status, model output, test success, or operational uptime.

## Reacquisition order

Before substantial work, first resolve the current branch and exact HEAD.

### If on the Oracle recovery / H24 branch

Read in this order:

1. `QUANT_NORTH_STAR.md`
2. fresh HEAD of `builder/oracle-economic-loop-recovery-20261019`
3. `research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md`
4. current `research/research_os/tasks/*.json` relevant to the active lineage
5. newest linked receipts, artifacts and events
6. repaired-release canary artifact `research/research_os/artifacts/AAA-ORACLE-H24-CANARY-f3943830e20b05d9/qualification-5f9807e6bd84fc5a.json` when runtime qualification detail is needed
7. CP5 / CP4 / CP3 only when historical detail is required

The Oracle timer may mutate durable GitHub state while an agent is working. Never rely on a previously remembered HEAD before a write.

### Otherwise

Use the current Blue/governance routing surfaces for that branch. Historical September files such as `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`, `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`, and `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md` remain branch-context documents, but they are **not** a substitute for the Oracle roadmap on the Oracle H24 branch.

`CLAUDE_CURRENT_MISSION.md`, `STATE.md`, `CHIEF_BRIEF.md`, repository default branch state, old PR text, and old chat summaries must not override fresher branch-specific canonical evidence.

## Builder / project-execution role

Claude Code is a Builder / Quant Engineer operating inside the governed project. Choose local implementation details autonomously, but do not redefine product scope or authority.

Optimize for **verified progress per intervention**:

- prefer one large coherent work package over many microtasks;
- split only genuinely independent work when wall-clock gain exceeds coordination cost;
- batch Owner/root commands into the smallest safe bounded intervention;
- delegate to another AI only substantial independent packages with exact branch/base SHA, scope, surfaces, invariants, evidence, forbidden actions, acceptance tests and handoff format;
- treat external-agent output as advisory until reconciled against fresh GitHub state and required runtime evidence;
- combine investigation, implementation, tests, evidence and durable documentation in the same package when practical;
- do not stop because one lane, test or experiment failed if other high-value executable work remains.

Prefer coherent capability over local elegance. Avoid new abstractions, files, agents, branches and refactors unless they directly advance the current mission or repair a demonstrated invariant.

## Oracle concurrency and Git discipline

On autonomous Oracle branches, GitHub is canonical shared memory and may change between reads.

Before every mutation:

1. reacquire fresh branch HEAD;
2. reacquire the current task/receipt/artifact state involved;
3. preserve autonomous commits;
4. write only after confirming the intended base still makes sense.

Never force-push, reset, rewind, delete autonomous evidence, or overwrite a newer Oracle transition to recover from a conflict. If HEAD advances concurrently, reacquire and reconcile.

Commit coherent checkpoints. Do not create serial documentation commits for every minor observation.

## Evidence hierarchy and model-output boundary

GitHub evidence can prove durable repository state, commit ancestry, receipts and artifacts. It cannot by itself prove live host state such as systemd service health, a reboot, current boot identity, or local inference. Runtime claims require corresponding host/runtime evidence.

Local model output is research commentary, not authority. In particular, Oracle qualification explicitly classifies representative model reasoning as `UNVERIFIED_MODEL_COMMENTARY`. Never promote generated prose to evidence merely because the model ran successfully.

A state enum is not a capability. A passing operational qualification is not a scientific result. A frozen hypothesis is not an economic result. Preserve these distinctions.

## Research and economic integrity

Use one causal information timeline across research, paper/shadow decisions and the Book. Never inspect future outcomes to tune a supposedly pre-outcome hypothesis.

Research evidence must describe the executable paper/shadow object rather than a more favorable backtest object.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions, receipts, candidates or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

Structural similarity is not empirical correlation. Where admissible return data is unavailable, correlation and marginal portfolio contribution remain unknown/not estimated.

## V1 closed / V2 boundary

Oracle H24 V1 is operationally closed. Do not silently extend V1 and then describe new work as already-qualified.

Further Oracle work should begin from an explicit V2 or separately governed specification. Candidate V2 topics include:

- scientific depth and acceptance criteria for Quant, Fundamental, Event/Documents, Institutional/Forced Flows and Validator engines;
- stronger fault injection and restart/idempotency tests;
- reusable release/upgrade operating contract;
- Portfolio Map evidence boundaries;
- Live Lab native ingress/UI proof;
- Forward Farm only if prospective observation is separately authorized;
- economic experiment paths only if separately authorized.

Operational V1 proof remains valid only for properties not materially invalidated by later code/deployment changes. Do not rerun completed qualification gates by habit; do rerun the affected gate when a later change can invalidate what it proved.

## Multi-agent discipline

Use parallel agents only when workstreams are genuinely independent, require isolated context, or benefit from adversarial review. Do not spawn agents for trivial reads, one-file edits, sequential debugging, or multiple writers against the same evolving state.

For substantive changes, separate implementation from independent scientific/economic-integrity and runtime/restart review when that separation adds value, then synthesize once in the lead agent.

Avoid duplicated exploration. Give each agent one distinct responsibility and require a concise durable result.

## Token discipline

Use targeted search and file slices before full-file reads. Do not repeatedly restate architecture or facts already established in canonical repository evidence.

Do not revisit a settled implementation choice unless new evidence contradicts it or a relevant test fails.

Keep progress updates short. Put durable truth in code, tests, roadmaps and generated artifacts rather than long chat summaries.

Use `/compact` or a fresh session when the task changes materially. After branch/context changes, reacquire through the canonical router rather than rereading the entire repository.

## Verification

Passing tests is necessary, not sufficient. Verify the specific property being claimed.

For code changes, run the narrow affected tests plus the relevant broader regression/CI path. Add adversarial coverage for the demonstrated failure mode being repaired.

For runtime claims, bind exact release SHA, host/runtime evidence, GitHub evidence and authority state. Never substitute a simulated/manual wake for a property that specifically requires a natural scheduled wake.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, research candidate, worker, lane or subsystem completed or failed.

----- CONTENT END -----
===== END DOCUMENT 012 =====

===== DOCUMENT 013 =====
BLOB: 7b73f2a069e23c50bfb50e19349ceeea05228dcb
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 10
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/7b73f2a069e23c50bfb50e19349ceeea05228dcb.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/CLAUDE.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/CLAUDE.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/CLAUDE.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/CLAUDE.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/CLAUDE.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/CLAUDE.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/CLAUDE.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/CLAUDE.md
BYTES: 10908
ENCODING_STATUS: UTF8
SHA256_CONTENT: 6f0f899768639c57838292bdad8e595da5164b41262a1d055c923900a7216287
----- CONTENT START -----
# Quant — Claude Code operating context

This file is intentionally compact because Claude Code loads it every session. Keep standing project rules here; keep task-specific procedures in the relevant mission, runtime roadmap, or `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` remains the highest project-level authority.

Do not redefine Quant around whichever subsystem is currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No file in this repository silently grants real-capital or live-trading authority.

## Current Oracle state

Oracle H24 V1 is operationally qualified on release:

`f3943830e20b05d926d3013501573b8b21fdace7`

Canonical V1 roadmap:

`research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md`

V1 proved exact-release CI, local GPT-OSS inference, durable GitHub task/receipt/artifact state, claim/lease recovery, natural systemd scheduling, genuine VM reboot recovery and natural post-reboot continuation.

Do not reinterpret V1 as proof of positive economic expectancy, scientific completeness of all research engines, Forward Farm operation, Live Lab UI completeness, real-capital safety or live-trading readiness.

## Active V2 implementation mission

Working branch:

`builder/oracle-v2-core-20261020`

Owner authorization on 2026-10-20: execute the Oracle Research OS V2 Core build autonomously from the challenged v0.3 architecture.

This authorization opens implementation only. The authority boundary remains:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Do not infer authority from task state, model output, tests, runtime health, Owner implementation approval or V2 readiness.

V2 Core target system status:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`

Strongest candidate-level status:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY`

Both are pre-outcome process claims only. They never mean profitable, alpha-proven or economically validated.

## Owner override — P0-D lifted

The prior V2 candidate proposed server-side canonical-ref protection / fast-forward-only branch enforcement as P0-D.

Owner decision: **P0-D is lifted and is not an implementation blocker.**

Therefore V2 Core MUST NOT require GitHub branch protection, rulesets, or server-side force-push prevention as a Definition-of-Done gate.

Operating discipline still forbids agents from force-pushing, rewinding, resetting or deleting autonomous evidence during normal project work. This is an operating rule, not a server-side qualification requirement.

GitHub remains the qualified initial orchestration backend under bounded-writer operation. A future backend migration requires an explicit migration gate and one authoritative orchestration source at a time.

## V2 architectural laws

1. **Research / Evaluation separation.** Research, Evidence and Validation remain outcome-blind. Evaluation is architecturally present but sealed while economic/prospective authority is false.
2. **Capability isolation over convention.** Future outcome access must not rely only on code choosing not to read an available file. Evaluation credentials/storage are a distinct capability boundary when activated.
3. **Research Epochs.** Every research trial belongs to a versioned epoch with knowledge cutoff, export policy, close policy, feedback-release policy, research policy, model-routing policy and lineage metadata.
4. **Precommitted closure.** After the first evaluation export, epoch close policy cannot silently change.
5. **Feedback lineage.** Economic feedback, once separately authorized and released in a future phase, may influence successor epochs only and may never rewrite historical Producer/Validator/trial state.
6. **Human/Supervisor blinding.** An actor that can influence an active blinded epoch must not observe sealed outcomes without contaminating that epoch.
7. **Model leakage accounting.** `SOURCE_PIT` and `MODEL_PIT` are distinct. Historical LLM idea generation is not assumed provably PIT merely because documentary sources are PIT.
8. **Trial accounting from ideation.** Multiplicity starts before CandidateHypothesis freeze; generated/discarded alternatives and retries remain traceable.
9. **Validator independence.** Information, retrieval, cognition and state isolation matter; different worker names alone do not prove independence.
10. **Multidimensional scientific state.** Scientific maturity, experiment readiness, portfolio relationship and authority are separate axes.
11. **Structural overlap is not empirical correlation.** Without admissible return data, empirical correlation and marginal portfolio contribution remain unknown/not estimated.
12. **Explicit research policy.** Forced Flows or any family priority is configurable/versioned policy, not a hidden scheduler belief.
13. **Explainable scheduling.** Undefined narrative concepts such as `HIGH_VALUE_CANDIDATE` must not drive priority; selection carries reason codes and policy version.
14. **Atomicity over artificial serialization.** The invariant is one authoritative atomic transition per claim. Initial resource policy may keep heavy local inference and authoritative writes bounded to one at a time.
15. **Negative knowledge is scoped.** Failure carries assumptions, regime context and revisit conditions; it does not mean an idea is false forever.
16. **No dual orchestration truth.** Any future SQLite/PostgreSQL promotion requires explicit migration proof and a single authoritative backend.
17. **Evaluation feedback is one-way while an epoch is active.** Only schema/integrity acknowledgements may cross back before governed feedback release.
18. **History remains epistemically honest.** Later learning never rewrites what the system knew, generated, discarded, prioritized or validated earlier.

## Reacquisition order on the V2 branch

Before substantial work:

1. read `QUANT_NORTH_STAR.md`;
2. resolve the fresh HEAD of `builder/oracle-v2-core-20261020`;
3. read this file;
4. read the canonical V2 architecture/spec and V2 roadmap under `research/research_os/` once created;
5. read only the code/tests relevant to the current V2 work package;
6. use V1 roadmap/checkpoints only for properties inherited from V1.

Do not route this branch through stale September Blue handoffs unless a current V2 file explicitly points there.

## Builder / project-execution role

Claude Code or another Builder may choose implementation details autonomously inside the governed V2 scope.

Optimize for verified progress per intervention:

- prefer one large coherent work package over many microtasks;
- split only genuinely independent work when wall-clock gain exceeds coordination cost;
- combine investigation, implementation, tests, evidence and durable documentation where practical;
- delegate only substantial independent packages with exact branch/base SHA, invariants, acceptance tests and handoff format;
- external-agent output remains advisory until reconciled against repository evidence;
- do not stop because one worker, lane, test or candidate fails if other high-value executable work remains.

Prefer coherent capability over local elegance. Avoid abstractions, agents, branches and refactors that do not directly advance V2 acceptance criteria.

## Oracle concurrency and Git discipline

GitHub is shared durable memory and may change between reads.

Before every mutation:

1. reacquire fresh branch HEAD;
2. reacquire the relevant task/receipt/artifact state;
3. preserve autonomous commits;
4. reconcile if HEAD advanced.

Never force-push, reset, rewind or delete autonomous evidence as a conflict-recovery tactic.

P0-D being lifted means server-side branch protection is not required; it does **not** authorize unsafe Git operations.

## Evidence hierarchy and model-output boundary

GitHub evidence proves repository state, ancestry, receipts and artifacts. It does not by itself prove host state, boot identity, model health or runtime execution.

Local or hosted model prose is not evidence by itself. Model output remains `UNVERIFIED_MODEL_OUTPUT` until bound to admissible evidence or deterministic checks.

A state enum is not a capability. Passing operational qualification is not a scientific result. A frozen hypothesis is not an economic result.

## Research and economic integrity

Never inspect future outcomes to tune a supposedly pre-outcome hypothesis.

Never fabricate market data. Preserve provenance, timestamps, PIT caveats, retrieval manifests, hashes and transformations.

Every persistent state mutation must remain restart-safe and idempotent. Crash plus replay must not duplicate sessions, receipts, candidates, freezes or attribution.

Research trials begin at ideation, not at candidate freeze. Keep discarded alternatives and retries attributable.

Where model-weight hindsight cannot be ruled out, record that limitation instead of claiming historical discovery ability.

## V1 / V2 boundary

V1 remains closed and qualified for the properties it actually proved.

V2 Core may reuse those mechanisms but must independently qualify new scientific properties introduced by V2.

Forward Farm remains closed while prospective observation is unauthorized. Economic evaluation remains sealed while economic experiment authority is false. Real capital and live trading remain closed.

## Verification

Passing tests is necessary, not sufficient. Verify the exact property claimed.

For code changes, run narrow affected tests plus relevant broader regression/CI. Add adversarial tests for each new V2 invariant.

For V2 Core qualification, required evidence must include at least:

- Research Epoch freeze and close-policy immutability;
- trial accounting from ideation;
- explicit `SOURCE_PIT` / `MODEL_PIT` classification;
- CandidateCore plus family-extension validation;
- independent Validator metadata and state separation;
- sealed Evaluation export with reverse-channel restrictions;
- successor-only feedback lineage;
- multidimensional maturity/portfolio state;
- explainable priority decisions;
- scoped Negative Memory;
- bounded-writer orchestration and failure recovery;
- unchanged four authority flags.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, an irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, candidate, worker, lane or subsystem completed or failed.

----- CONTENT END -----
===== END DOCUMENT 013 =====

===== DOCUMENT 014 =====
BLOB: 87a8e2182122dfaa9b3b6070ce58ab8f2ab8b04d
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 2
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/87a8e2182122dfaa9b3b6070ce58ab8f2ab8b04d.txt
BYTES: 5537
ENCODING_STATUS: UTF8
SHA256_CONTENT: 72d2aee65c46ad5e7d26e5ca1547dd98bc35e725e5dfd3a750fc73d7b12f527d
----- CONTENT START -----
# Quant - Claude Code operating context

This file is intentionally short because Claude Code loads it every session. Put standing project rules here and task procedures in `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal project objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` is the highest authority.

Do not redefine Quant around the subsystem currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No real-capital authority is granted by this file. Current engineering work remains paper/shadow unless the project owner explicitly changes that boundary.

## Current authority / restart surface

Before substantial work:
1. Read `QUANT_NORTH_STAR.md`.
2. Read `handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md`.
3. Read `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`.
4. Read `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`.
5. Read the exact branch-specific mission/handoff named by current Blue governance.
6. Read only the architecture, code and tests relevant to that exact mission.

`STATE.md` and `CHIEF_BRIEF.md` are runtime/research snapshots, not current project-routing authority.
`CLAUDE_CURRENT_MISSION.md` is now a router and must not contain a frozen historical mission.
The repository default branch is currently historical and is not authority.

Do not import the whole of `AGENTS.md` into every session; use the current governance files above as the compact routing surface.

## Builder role

Claude Code is the Builder / Quant Engineer. Choose local implementation details autonomously, but do not redefine the product around the easiest component to finish.

Prefer coherent capability over local elegance. Avoid extra abstractions, files, agents and refactors unless they directly advance the current mission or repair a demonstrated invariant.

Ordinary coding failures, negative research results and blocked research lanes are not project stop conditions. Record them and continue with the highest-value executable work.

## Integrity invariants

Use one causal information timeline across research, paper/shadow decisions and the Book. Research evidence must describe the executable paper/shadow strategy rather than a more favorable backtest object.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate them separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

A state enum is not a capability. Do not claim decay management, historical strategy versioning, liveness or other behavior unless evidence actually drives it.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

## Ultracode / multi-agent discipline

Project settings enable Ultracode with a small workflow size guideline. Use parallel agents when workstreams are genuinely independent, need isolated context or benefit from adversarial review.

Do not spawn agents for trivial reads, one-file edits, sequential debugging or work that requires one shared evolving state.

For substantive changes, separate implementation from independent economic/research-integrity and runtime/restart review, then synthesize once in the lead agent.

Avoid duplicated exploration. Give each agent one distinct question and require a concise result.

## Token discipline

Use targeted search and file slices before full-file reads. Do not repeatedly restate architecture or facts already established in the repository.

Do not revisit a settled implementation choice unless new evidence contradicts it or a test fails.

Keep progress updates short. Put durable truth in code, tests, `STATE.md` and generated artifacts rather than long chat summaries.

Use `/compact` or a fresh session when the task changes materially. Use `/quant-orient` after branch/context changes instead of rereading everything manually.

## Verification

Normal V1 verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
```

Passing tests is necessary, not sufficient. Add adversarial tests for the specific failure mode being repaired. Use `/quant-proof` before declaring a major milestone complete.

## Git behavior

Follow the exact branch ownership and mutation permissions in the current Blue mission/handoff. Do not infer a current PR or branch from historical files.

Do not merge, force-push, delete branches, move frozen refs or perform irreversible external actions unless the current mission explicitly authorizes that operation.

Commit coherent checkpoints and keep durable mission state in GitHub rather than chat.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, experiment, worker, lane or subsystem completed or failed.

----- CONTENT END -----
===== END DOCUMENT 014 =====

===== DOCUMENT 015 =====
BLOB: 88a5c6b593a003e30c9a4707b562495f43771364
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 2
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/88a5c6b593a003e30c9a4707b562495f43771364.txt
BYTES: 5026
ENCODING_STATUS: UTF8
SHA256_CONTENT: 309409ed7c54bd717a0b9925c3845e97a448b3d28665d8409fb24437918d27de
----- CONTENT START -----
# Quant - Claude Code operating context

This file is intentionally short because Claude Code loads it every session. Put standing project rules here and task procedures in `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal project objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` is the highest authority.

Do not redefine Quant around the subsystem currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No real-capital authority is granted by this file. Current engineering work remains paper/shadow unless the project owner explicitly changes that boundary.

## Read economically, not ceremonially

Before substantial work:
1. Read `QUANT_NORTH_STAR.md`.
2. Read `STATE.md` and `CLAUDE_CURRENT_MISSION.md` when present.
3. Read only the architecture, code and tests relevant to the current change.
4. Read longer docs such as `SYSTEM_ARCHITECTURE.md`, `OPERATING_MODEL.md` and `AGENTS.md` only when the decision depends on them.

Do not import `AGENTS.md` here. Avoiding that startup context cost is intentional.

## Builder role

Claude Code is the Builder / Quant Engineer. Choose local implementation details autonomously, but do not redefine the product around the easiest component to finish.

Prefer coherent capability over local elegance. Avoid extra abstractions, files, agents and refactors unless they directly advance the current mission or repair a demonstrated invariant.

Ordinary coding failures, negative research results and blocked research lanes are not project stop conditions. Record them and continue with the highest-value executable work.

## Integrity invariants

Use one causal information timeline across research, paper/shadow decisions and the Book. Research evidence must describe the executable paper/shadow strategy rather than a more favorable backtest object.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate them separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

A state enum is not a capability. Do not claim decay management, historical strategy versioning, liveness or other behavior unless evidence actually drives it.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

## Ultracode / multi-agent discipline

Project settings enable Ultracode with a small workflow size guideline. Use parallel agents when workstreams are genuinely independent, need isolated context or benefit from adversarial review.

Do not spawn agents for trivial reads, one-file edits, sequential debugging or work that requires one shared evolving state.

For substantive changes, separate implementation from independent economic/research-integrity and runtime/restart review, then synthesize once in the lead agent.

Avoid duplicated exploration. Give each agent one distinct question and require a concise result.

## Token discipline

Use targeted search and file slices before full-file reads. Do not repeatedly restate architecture or facts already established in the repository.

Do not revisit a settled implementation choice unless new evidence contradicts it or a test fails.

Keep progress updates short. Put durable truth in code, tests, `STATE.md` and generated artifacts rather than long chat summaries.

Use `/compact` or a fresh session when the task changes materially. Use `/quant-orient` after branch/context changes instead of rereading everything manually.

## Verification

Normal V1 verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
```

Passing tests is necessary, not sufficient. Add adversarial tests for the specific failure mode being repaired. Use `/quant-proof` before declaring a major milestone complete.

## Git behavior

For the current corrective pass, update draft PR #12 rather than opening another PR. Do not merge, force-push, delete branches or perform irreversible external actions unless explicitly authorized.

Commit coherent checkpoints and remove temporary scratch files from the final diff.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, experiment, worker, lane or subsystem completed or failed.

----- CONTENT END -----
===== END DOCUMENT 015 =====

===== DOCUMENT 016 =====
BLOB: a9620341101ef781a62c4c3b51d3a9f3e7bde621
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 3
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/a9620341101ef781a62c4c3b51d3a9f3e7bde621.txt | audit/owner-recovery/20261026/pass-01/snapshots/edge_lab/CLAUDE.md
BYTES: 5537
ENCODING_STATUS: UTF8
SHA256_CONTENT: 798924cfd344d3e28efb3025d9f0d0d7d9fc61ae044e29e4786c1d6f686042cc
----- CONTENT START -----
# Quant - Claude Code operating context

This file is intentionally short because Claude Code loads it every session. Put standing project rules here and task procedures in `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal project objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` is the highest authority.

Do not redefine Quant around the subsystem currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No real-capital authority is granted by this file. Current engineering work remains paper/shadow unless the project owner explicitly changes that boundary.

## Current authority / restart surface

Before substantial work:
1. Read `QUANT_NORTH_STAR.md`.
2. Read `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`.
3. Read `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`.
4. Read `handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md`.
5. Read the exact branch-specific mission/handoff named by current Blue governance.
6. Read only the architecture, code and tests relevant to that exact mission.

`STATE.md` and `CHIEF_BRIEF.md` are runtime/research snapshots, not current project-routing authority.
`CLAUDE_CURRENT_MISSION.md` is now a router and must not contain a frozen historical mission.
The repository default branch is currently historical and is not authority.

Do not import the whole of `AGENTS.md` into every session; use the current governance files above as the compact routing surface.

## Builder role

Claude Code is the Builder / Quant Engineer. Choose local implementation details autonomously, but do not redefine the product around the easiest component to finish.

Prefer coherent capability over local elegance. Avoid extra abstractions, files, agents and refactors unless they directly advance the current mission or repair a demonstrated invariant.

Ordinary coding failures, negative research results and blocked research lanes are not project stop conditions. Record them and continue with the highest-value executable work.

## Integrity invariants

Use one causal information timeline across research, paper/shadow decisions and the Book. Research evidence must describe the executable paper/shadow strategy rather than a more favorable backtest object.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate them separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

A state enum is not a capability. Do not claim decay management, historical strategy versioning, liveness or other behavior unless evidence actually drives it.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

## Ultracode / multi-agent discipline

Project settings enable Ultracode with a small workflow size guideline. Use parallel agents when workstreams are genuinely independent, need isolated context or benefit from adversarial review.

Do not spawn agents for trivial reads, one-file edits, sequential debugging or work that requires one shared evolving state.

For substantive changes, separate implementation from independent economic/research-integrity and runtime/restart review, then synthesize once in the lead agent.

Avoid duplicated exploration. Give each agent one distinct question and require a concise result.

## Token discipline

Use targeted search and file slices before full-file reads. Do not repeatedly restate architecture or facts already established in the repository.

Do not revisit a settled implementation choice unless new evidence contradicts it or a test fails.

Keep progress updates short. Put durable truth in code, tests, `STATE.md` and generated artifacts rather than long chat summaries.

Use `/compact` or a fresh session when the task changes materially. Use `/quant-orient` after branch/context changes instead of rereading everything manually.

## Verification

Normal V1 verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
```

Passing tests is necessary, not sufficient. Add adversarial tests for the specific failure mode being repaired. Use `/quant-proof` before declaring a major milestone complete.

## Git behavior

Follow the exact branch ownership and mutation permissions in the current Blue mission/handoff. Do not infer a current PR or branch from historical files.

Do not merge, force-push, delete branches, move frozen refs or perform irreversible external actions unless the current mission explicitly authorizes that operation.

Commit coherent checkpoints and keep durable mission state in GitHub rather than chat.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, experiment, worker, lane or subsystem completed or failed.

----- CONTENT END -----
===== END DOCUMENT 016 =====

===== DOCUMENT 017 =====
BLOB: e1fb1130da04bd2f50690e3cc2967b496692b311
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 2
PATHS: CLAUDE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/e1fb1130da04bd2f50690e3cc2967b496692b311.txt
BYTES: 4253
ENCODING_STATUS: UTF8
SHA256_CONTENT: 492821d98fdf3cdae4ea6ce44b059619fb77f78fca6b1dbdcdf9fcb1748c2677
----- CONTENT START -----
# Quant - Claude Code operating context

This file is intentionally short because Claude Code loads it every session. Put standing project rules here and task procedures in `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal project objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` is the highest authority.

Do not redefine Quant around the subsystem currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No real-capital authority is granted by this file. Current engineering work remains paper/shadow unless the project owner explicitly changes that boundary.

## Read economically, not ceremonially

Before substantial work:
1. Read `QUANT_NORTH_STAR.md`.
2. Read `BUILDER_ROLE.md` and the current released mission when acting as Builder.
3. Read `STATE.md` and mission-relevant code/tests.
4. Read longer architecture docs when the decision depends on them.

Do not import `AGENTS.md` here. Avoiding that startup context cost is intentional.

## Builder role

Claude Code is one provider that may occupy the provider-independent Builder / Quant Engineer role. `BUILDER_ROLE.md` defines its authority, prohibitions, proof discipline and Red-Team handoff.

Choose local implementation details autonomously, but do not redefine the product around the easiest component to finish. Prefer coherent capability over local elegance. Avoid extra abstractions, files, agents and refactors unless they directly advance the released mission or repair a demonstrated invariant.

Ordinary coding failures, negative research results and blocked research lanes are not project stop conditions. Record them and continue with the highest-value executable work.

## Integrity invariants

Use one causal information timeline across research, paper/shadow decisions and the Book. Research evidence must describe the executable paper/shadow strategy rather than a more favorable backtest object.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate them separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

A state enum is not a capability. Do not claim decay management, historical strategy versioning, liveness or other behavior unless evidence actually drives it.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

## Token and workflow discipline

Use parallel agents only for genuinely independent workstreams or independent review. Do not duplicate exploration. Use targeted search and file slices before full-file reads. Put durable truth in code, tests and generated artifacts rather than chat summaries.

## Verification

Run the proof gate defined by the current released mission. Existing V1 verification remains a required baseline unless that mission explicitly supersedes it.

Passing tests is necessary, not sufficient. Add adversarial tests for the specific failure mode being repaired or data semantic being asserted.

## Git behavior

Never infer current authority from an old PR, branch name or this provider-specific file. Verify the exact released `BASE_SHA` and branch from the current mission. Do not merge, force-push, delete branches or perform irreversible external actions unless explicitly authorized.

Commit coherent checkpoints and remove temporary scratch files from the final diff.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an objective ambiguity that changes the scientific contract.

Do not stop merely because one test, experiment, worker, lane or subsystem completed or failed.

----- CONTENT END -----
===== END DOCUMENT 017 =====

===== DOCUMENT 018 =====
BLOB: eb5291cb0ada485e56961dc6c9495248110a5aa1
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 1
PATHS: CLAUDE.md
BYTES: 5428
ENCODING_STATUS: UTF8
SHA256_CONTENT: e06a27ae9acf035c925348949a3a49bb2927943075299cd9550aa4acc0f7cdff
----- CONTENT START -----
# Quant-Trade — contexte projet (lu automatiquement par toute session/agent)

Outil probabiliste sur indices NASDAQ. Trois étapes construites (A, B, C),
une quatrième en cours (D). Historique complet dans le repo, mais voici
l'essentiel pour ne pas repartir de zéro.

## Fichiers de données (`data/`)

- `nasdaq_composite_daily.txt` — **échantillon PRÉ-ENREGISTRÉ, NE JAMAIS MODIFIER.**
  NASDAQ Composite, 13/07/2021→10/07/2026, 1251 séances. Toutes les analyses
  "protocole figé" de référence tournent dessus par défaut.
- `nasdaq100_daily.txt` — NASDAQ-100 (NDX), 01/10/1985→13/07/2026, 10273
  séances (ère à volume réel ≥ 1985 uniquement ; fourni par l'utilisateur,
  nettoyé : 2 arrondis OHLC corrigés). Sert à ré-exécuter le même protocole
  sur un historique long (40 ans, plusieurs cycles).

Format (tabulé, fins de ligne CRLF, décimales `.`) :
```
date	ouv	haut	bas	clot	vol	devise	
13/07/2021 00:00	14715.133	14803.676	14660.19	14677.654	0	Pts	
```
Chargement : `src/data_loader.py::load_ohlc(path)` → DataFrame `[date,open,high,low,close]`.
`quality_report(df)` valide (lève si dates dupliquées ou OHLC incohérent).

## Code (`src/`)

- `data_loader.py` — `load_ohlc`, `quality_report`, `log_returns_pct` (rendements
  log %, close-to-close), `parkinson_var_pct` (variance range-based intra-séance).
- `diagnostics.py` (Étape A) — `summary_stats`, `lo_mackinlay_vr(r,q)` (ratio de
  variance, z homoscéd. et z\* robuste hétéro.), `ljung_box`, `acf`,
  `engle_arch_lm`, `fit_student_t`.
- `prediction.py` (Étape B) — `build_features(df)` (features CAUSALES : momentum,
  vol rolling, RSI/MACD/Bollinger/ATR/Stochastic, differenciation fractionnaire
  `frac_diff`), `triple_barrier_labels(df,horizon,vol_span,mult)` (labels
  ±1/0, barrières ∝ vol locale ewm), `walk_forward_signals` (purge/embargo),
  `backtest(pos,r_fwd,cost_bps,delay)`, `trading_metrics` (Sharpe/Sortino/
  Calmar/MDD/profit factor — **jamais le R²**), `dsr` (Deflated Sharpe Ratio,
  Bailey & López de Prado 2014).
- `volatility.py` (Étape C) — `ARCH_SPECS` (GARCH-n/t, GJR-t, GJR-skewt),
  `fit_arch`, `garch_path`/`garch_multistep` (récursions maison, validées vs
  `arch`), `ewma_path`, `fit_har`/`har_forecast` (HAR sur RV Parkinson),
  `qlike`/`mse`, `spa_test` (SPA de Hansen, bootstrap stationnaire), `dm_test`
  (Diebold-Mariano, HAC).

## Scripts (`scripts/`)

Chacun : `python3 scripts/run_etape_X.py [chemin_données] [chemin_sortie]`
(défaut = Composite pré-enregistré + `results/etape_X_....md`).
`run_etape_c.py` respecte la variable d'env `REFIT_EVERY` (défaut 5 ; utiliser
21 sur les historiques longs, sinon très lent — ~450 ré-estimations GARCH
sinon des milliers).

## Résultats déjà établis (ne PAS refaire, seulement RÉUTILISER)

**Étape A** — Composite (5 ans) : random walk NON rejeté (z\* robuste
non significative). NDX (40 ans) : random walk **REJETÉ** (VR(5)=0,89,
z\*=−2,68, p=0,007 → retour à la moyenne faible mais détecté). Effet ARCH
massif et queues épaisses (ν≈4,8 non conditionnel) dans les deux cas.

**Étape B** — univers figé N=4 (BuyHold, Momentum signe rdt-10j, Logit L2,
HistGB). Triple-barrier H=5j, ±1,5σ (ewm 20j). Walk-forward T0=750,
purge/embargo=5j, coûts 5 bps aller-retour.
- Composite : **aucun signal actif ne bat Buy & Hold** à DSR>0,95 (DSR
  BuyHold=0,567, le meilleur).
- NDX : LogitL2 **rentable net de coûts** (Sharpe +0,30, accuracy 53,7 %,
  break-even ≈17 bps ≫ 5 bps) mais **encore sous Buy & Hold** en DSR
  (BuyHold 0,842 vs LogitL2 0,372).
- **Conclusion actuelle : Buy & Hold reste la meilleure stratégie testée.**

**Étape C** — univers figé N=6 (EWMA, GARCH-n=bench, GARCH-t, GJR-t,
GJR-skewt, HAR-P). Perte QLIKE, test DM vs bench, test SPA famille entière.
- Composite (500 obs OOS) : GJR-t bat le bench (DM p=0,014 h=1, p=0,030 h=5)
  mais le SPA famille entière **échoue** (p≈0,11–0,15, non robuste — limite
  d'échantillon).
- NDX (9522 obs OOS) : GJR-t/GJR-skewt battent le bench ET **passent le SPA**
  (p=0,0000 h=1, p=0,0034 h=5) → **edge de volatilité statistiquement solide**.
- **Le modèle de volatilité C est le plus robuste des trois — utile pour le
  risk management (position sizing, VaR), pas pour prédire une direction.**

## Étape D (en cours / à construire)

Overlay défensif combinant B (direction, faible) + C (volatilité, robuste) :
piloter l'exposition (vol-targeting et/ou coupe en régime de vol extrême)
pour capter l'essentiel du rendement Buy & Hold tout en réduisant le max
drawdown (NDX a connu −83 % en 2000-2002 dans l'historique long). Objectif :
Sharpe/Calmar ≥ Buy & Hold avec MDD nettement inférieur.

## Discipline anti-data-snooping (NON NÉGOCIABLE)

Les univers de modèles/signaux et les protocoles OOS sont **figés avant
évaluation** dans chaque script. Toute extension doit être déclarée, comptée
(N essais) et re-testée au SPA/DSR. On n'itère jamais sur l'échantillon de
test jusqu'à un chiffre plaisant. R² interdit comme métrique de succès —
seules les métriques de trading nettes de coûts comptent.

## Git

Branche de travail : `claude/price-prediction-model-ykhog1`. Ne pas modifier
`data/nasdaq_composite_daily.txt` (échantillon pré-enregistré). Ne pas
pousser sans consigne explicite si vous êtes un sous-agent — laissez
l'orchestrateur intégrer et pousser.

----- CONTENT END -----
===== END DOCUMENT 018 =====

===== DOCUMENT 019 =====
BLOB: f3c2235b42f37e895771afe8b907f791b0d3f814
REPRESENTATIVE_PATH: CLAUDE.md
PATH_COUNT: 1
PATHS: CLAUDE.md
BYTES: 3604
ENCODING_STATUS: UTF8
SHA256_CONTENT: a355559a6c0bbad5bb76b4f2b1de004ed8c484fd0cf8cf4a4a7d7a28a10a3298
----- CONTENT START -----
# Quant-Trade — Claude operating context

Keep this file compact. It is a standing router, not a frozen mission.

## Mandatory orientation

Before substantial work, read in this order:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve the exact current branch and live HEAD
4. read the exact branch-specific audit/runtime/design evidence required for the assigned mission

Do **not** use September 2026 Blue handoffs, `STATE.md`, `CHIEF_BRIEF.md`, old issues, old PR text or the GitHub default branch alone to infer the current mission.

## Current project lines

- live Oracle V1: `builder/oracle-economic-loop-recovery-20261019`
- independent forensic / V2 baseline: `audit/forensic-checkpoint-20261019` -> `CHECKPOINT_010.md`
- V2 canonical trunk: `NOT_YET_DECLARED`
- default branch `blue/master-v2-2026-09-20`: routing/historical portal during cleanup, not latest-code authority

Oracle V1 may advance autonomously. Resolve its current HEAD rather than trusting a stale SHA in a chat or old document.

## Permanent authority boundary

Unless a later explicit Owner decision changes it:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Operational qualification, tests, validator PASS, frozen hypotheses, branch cleanup or model output grant none of these authorities.

## Builder role

Claude Code is primarily a Builder / Quant Engineer.

Do not redefine Quant around the subsystem currently being edited. Prefer the smallest coherent implementation that advances the current declared architecture and preserves evidence, restart safety and scientific boundaries.

Routine engineering decisions do not require Owner escalation. Escalate only genuine external boundaries, irreversible authority changes, unavailable resources/credentials, paid access, or strategic ambiguity not resolvable from current evidence.

## Scientific / runtime invariants

- never fabricate market data or evidence;
- preserve point-in-time timing, provenance and immutable historical results;
- UNKNOWN is not evidence of independence or PASS;
- structural similarity is not empirical correlation;
- preserve producer / validator-red-team / integration separation;
- persistent mutations must be restart-safe and idempotent;
- failed experiments remain scientific memory;
- one local PASS must not silently become a family-level or economic-edge claim.

## Repository hygiene

Current cleanup authority:

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`

Do not recreate branch sprawl. Reuse current branches where appropriate. If historical unique work is no longer active, archive its exact tip before deleting its working branch ref.

Do not mutate the live Oracle V1 branch as incidental cleanup.

## V2 discipline

V2 is being assembled from reconciled sources. Important current source branches are listed in `governance/CURRENT_PROJECT_STATE_2026-10-20.md`.

Do not:

- start a competing top-level architecture;
- silently promote an old branch to V2 authority;
- discard negative results because they are inconvenient;
- import historical work without recording provenance / supersession;
- treat cleanup as evidence that historical scientific conclusions disappeared.

## Completion standard

For substantive work, leave:

- coherent code or durable evidence;
- tests/adversarial checks appropriate to the failure mode;
- exact branch + HEAD provenance;
- updated current routing only when project state actually changed;
- a clear next legitimate action.

----- CONTENT END -----
===== END DOCUMENT 019 =====

===== DOCUMENT 020 =====
BLOB: 073eb656bd1678b7275118fe66ce54c64f0bb79c
REPRESENTATIVE_PATH: CLAUDE_CURRENT_MISSION.md
PATH_COUNT: 10
PATHS: CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/073eb656bd1678b7275118fe66ce54c64f0bb79c.txt | audit/owner-recovery/20261026/pass-01/snapshots/canonical_w2/CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_f/CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/snapshots/giga_q/CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_c1/CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/snapshots/horizontal_pre/CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/snapshots/intake_v3/CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/snapshots/runtime_v2/CLAUDE_CURRENT_MISSION.md | audit/owner-recovery/20261026/pass-01/snapshots/vertical/CLAUDE_CURRENT_MISSION.md
BYTES: 2684
ENCODING_STATUS: UTF8
SHA256_CONTENT: 92601eb26d913eab09d8030d5fc274de0dfc05c5bb83d80217353917df5929c3
----- CONTENT START -----
# Claude Current Mission Router

This file is a router, not a frozen task specification.

## Resolve current work

Always begin by resolving the current branch and exact HEAD.

### Oracle V2 Core branch

If the branch is:

`builder/oracle-v2-core-20261020`

read in this order:

1. `QUANT_NORTH_STAR.md`
2. `CLAUDE.md`
3. `research/research_os/architecture/ORACLE_V2_CORE_SPEC.md`
4. `research/research_os/runtime/ORACLE_V2_CORE_ROADMAP.md`
5. `research/research_os/runtime/V2_CORE_POLICY.json`
6. `research/research_os/runtime/V2_ACTIVE_EPOCH.json`
7. `research/research_os/runtime/CODEX_V2_HANDOFF_20261020.md`
8. the code/tests relevant to the current V2 work package
9. the V1 roadmap/checkpoints only when validating inherited V1 properties

The Codex handoff is a point-in-time continuation guide, not a substitute for fresh HEAD/CI reacquisition. If repository state advanced after the handoff commit, preserve and reconcile newer evidence.

Current mission: implement and qualify Oracle Research OS V2 Core as an autonomous **pre-outcome** research pipeline.

Owner implementation authorization is active.

Owner override: P0-D server-side branch protection is lifted and is not a V2 Definition-of-Done gate.

Permanent authority boundary during V2 Core:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Target system qualification:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`

Strongest candidate status:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY`

Neither is an economic-performance claim.

### Oracle V1 recovery branch

If the branch is:

`builder/oracle-economic-loop-recovery-20261019`

use `CLAUDE.md` and `research/research_os/runtime/ORACLE_LAB_V1_ROADMAP.md` as the current Oracle routing surfaces.

### Other branches

Use the branch-specific current governance/handoff. Historical September Blue files are relevant only when the current branch/governance explicitly routes to them.

## Never infer current mission from

- repository default branch;
- `STATE.md` alone;
- `CHIEF_BRIEF.md` alone;
- old PR/issue text;
- old chat summaries;
- this file's historical Git versions.

## Git / evidence discipline

Before any mutation reacquire fresh HEAD and relevant state. Preserve autonomous commits. Do not use force-push, reset, rewind or deletion of autonomous evidence as a conflict-recovery method.

P0-D being lifted removes the requirement for server-side branch protection; it does not authorize destructive Git operations.

Runtime evidence and repository evidence remain distinct. Model prose is never self-authenticating evidence.

----- CONTENT END -----
===== END DOCUMENT 020 =====
