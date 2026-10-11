# disc-cfe-vix-term-premium-l1-v0

Label: EXPLORATORY; pre-declared 2026-10-11T22:16:30.575864+00:00; parent 9348a94c9f3541a92e8a8334e1cf07c2ed7e029f.

- ID: disc-cfe-vix-term-premium-l1-v0
- mechanism: volatility insurance demand may compensate sellers for bearing jump and mark-to-market risk.
- who_pays: investors buying volatility protection; compensation may be entirely risk premium, not alpha.
- why_persist: crash exposure, funding/margin and mandate constraints deter arbitrage; not a guaranteed premium.
- level: L1.
- question: does one fixed quarterly short-VX settlement proxy show a broad economically material premium net of simple costs over 2013–2025?
- proxy: 52 quarterly H/M/U/Z expiry contracts, 2013–2025 inclusive; official CFE historical daily settlement files. Calendar/URL manifest accompanies this declaration. One constant contract per nonoverlapping trade, never resize after returns.
- known_biases: settlement is not a fill; official files may be revised; stale/zero settlement values, off-market marks, survivorship of file availability, holiday calendar approximation, fixed quarterly sampling, small effective N and jump concentration. No daily margin or risk-adjusted alpha established. Personal noncommercial analysis only; no redistribution of raw Cboe data.
- fixed_rule: for each manifest contract, short at the first strictly positive daily Settle on/after expiry minus45 calendar days, cover at the first strictly positive daily Settle on/after expiry minus15 days. Each chosen row must be within4 calendar days of its target; no substitute contract/window. Require all52 trades; missing/ambiguous files => PARK, no partial positive selection. PnL index points = entry minus exit. Multiplier1000 USD/point. Report all52 outcomes, calendar-year totals, pooled mean/median, worst trade, endpoint-only cumulative drawdown and 2013–2018/2019–2025 block means. Entry/exit are fixed calendar targets; no fit, filter or parameter search. No back-adjusted series.
- cost_assumption: 0.10VX points round-trip central (100USD/contract),0.25 stress (250USD). These assume commissions+spread+slippage; not authenticated historical broker costs. Capital denominator deliberately absent: no Sharpe/CAGR/leveraged return. Financing, intratrade margin/default and crash execution unresolved.
- max_time_minutes: 60 agent minutes; each request <=15s and262144 body bytes; each process <=120s and2MiB metadata/payload; at most52 files total, no retries or secondary provider substitution in this experiment. Stop acquisition on first unavailable/invalid file and preserve it. No paid service/account.
- kill_if: with complete sample, gross pooled mean<=0, or stress-net mean<=0. This kills only this quarterly settlement expression, not all volatility insurance.
- promote_if: complete sample, central-net mean>=0.25VX points/trade, stress-net mean>0 and both fixed chronological blocks central-net positive. Otherwise PARK mixed/insufficient. PROMOTE_HIGH not allowed with this proxy. Promotion only justifies risk/margin/execution validation.
- uncertainty: descriptive year-cluster bootstrap of pooled mean (13 year blocks,2000 draws,seed41011,95percent interval); no confirmatory p-value. Wide interval reported, no extra test chosen afterward.
- prior_exposures: PRIVATE_UNKNOWN; known literature about short-volatility risk premium and famous volatility crashes, no claim of untouched data. Cached catalogue/HEAD only for CFE; earlier F1/B2/B4/SMARD and other closed families untouched. One rule/two fixed cost scenarios, M_effective UNKNOWN;52 trades are not52 independent discoveries.
- RESULT: 36/52 files acquired; request37 (H2022) returned403. No payoff/statistical calculation. Full receipts in the adjacent result JSON.
- DECISION: PARK (PARK_DATA).
- NEXT: next Discovery family. Preserve private raw files; no automatic retry or shortened-window result.

V4.2 pilot folder is design-only; this separately published quarterly45→15calendar-day contract is the executed access attempt, not the pilot20-trading-day expression. No silent equivalence is claimed.
