# Experiment protocol

## P0-E1 — Does a causal volatility forecast improve terminal wealth?

**Status before final result:** preregistered; the OOS result must not be read
until the implementation is frozen.

- **Bottleneck:** the repository scores volatility forecasts but has no
  demonstrated mapping from information at time *t* to net wealth.
- **Hypothesis:** volatility persistence can make a long-only, unlevered
  exposure rule compound to more wealth than constant exposure by avoiding
  sufficiently damaging high-volatility periods.
- **Mechanism:** RiskMetrics EWMA (`lambda=0.94`) forecasts next-day variance;
  exposure is `min(1, 20% / forecast annual volatility)`.
- **Information/timing:** exposure earning close-to-close return *t* uses only
  closes through *t-1*. This deliberately avoids same-close execution.
- **Data:** existing NASDAQ Composite OHLC file. First 750 returns are training;
  the final 500 are the already-consumed evaluation period. The index is not a
  tradable instrument, so even success cannot justify `PROMOTE`.
- **Benchmark:** constant 1.0 exposure to the same return series.
- **Economics:** arithmetic portfolio returns, initial wealth 1.0, zero cash
  yield/financing, and 2 bp per unit of one-way exposure turnover. Cost stresses
  are 0, 5, and 10 bp.
- **Primary criterion:** strategy terminal wealth after 2 bp must exceed the
  benchmark. Otherwise `KILL` this economic use of the forecast.
- **Secondary diagnostics (cannot rescue failure):** CAGR, annual volatility,
  maximum drawdown, turnover, and concentration.
- **Falsification fixed ex ante:** split-half results; remove the five best and
  five worst strategy days; perturb `lambda` to 0.90 and 0.97 and target
  volatility to 12% and 18%. These are robustness checks, not candidates from
  which to select a winner.
- **Multiplicity:** this is one material experiment with six disclosed stress
  variants. No untouched holdout remains after execution.
- **Decision mapping:** failure of the primary criterion is `KILL`; success is
  at most `VALIDATE_MORE`, because the data source has no provenance, lacks
  dividends and a tradable instrument, and covers only five years.

