# V2-A Mission - SEC Form-4 Deterministic Census and Data-Semantics Gate

Authority: Blue Team / Mission Control. Builder base is frozen at `37f298423ca4a100c1c633da2c3c6c2641d8dd8e`. This mission is a Data Plane / Research-Factory preregistration gate only. It grants no return-analysis, capital, merge or Phase-2 economic authority.

Read `QUANT_NORTH_STAR.md` and `BUILDER_ROLE.md` first.

## Frozen scientific contract

- Source period: 2020-01-01 through 2026-06-30 inclusive; 2026 is H1.
- Primary census source: official SEC EDGAR ownership structured data and raw filing/index artifacts.
- Original Form 4 only. Form 4/A cannot create a certified event and is counted diagnostically.
- Qualifying transaction: non-derivative code `P` and acquired/disposed code `A`. SEC code P includes open-market **or private** purchase.
- Qualified reporting owner: director and/or officer. Ten-percent ownership alone is insufficient.
- Issuer identity: issuer CIK. Ticker is only a temporal attribute.
- Insider identity: reporting-owner CIK. No fuzzy name matching.
- Joint filings: never infer transaction-row ownership. When a filing has multiple reporting owners and primary structure does not prove attribution, classify `JOINT_OWNER_AMBIGUOUS` and exclude it from the certified event count while reporting it.
- Calendar: pinned canonical U.S. regular-session calendar. Two transaction dates qualify when regular sessions separating them are `<= 10`.
- Formation: for each issuer, process qualifying observations in transaction-date order. Create exactly one formation when the trailing 10-session window crosses from `<2` to `>=2` distinct qualified insider CIKs. Additional insiders do not create another formation while the window remains active. A later event is allowed only after the rolling window first falls below two and re-arms.
- Public observability: retain transaction dates separately from EDGAR acceptance timestamps. `event_time` is the earliest time at which two distinct qualifying insiders in the economic crossing window are publicly observable.
- Security/ticker/price-path coverage is downstream diagnostic metadata only. It cannot add, remove or redefine a census event.

## Hard boundary

No forward returns, P&L, Sharpe, alpha, hit rate, return t-statistic, strategy optimization, parameter rescue or outcome-based exclusion may be queried, computed, ranked, plotted or persisted in this mission. The 2-insider / 10-session rule is immutable.

## Required handoff state

Builder finishes only at `SUBMITTED_FOR_RED_TEAM`, never `MERGEABLE`, with exact branch/SHA, source hashes, waterfall, exact census, annual/concentration statistics, unresolved and mapping-loss ledger, design-level N sensitivity, clean proof evidence and known limitations. Red Team should attack identity, event uniqueness, causal timing, calendar window, amendments/joint filings, survivorship/ticker mapping, loss reconciliation, determinism and artifact freshness.
