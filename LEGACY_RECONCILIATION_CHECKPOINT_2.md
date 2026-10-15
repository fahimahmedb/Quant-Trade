# Legacy Economic Reconciliation — Checkpoint 2

Date: 2026-10-15
Branch: `research/legacy-economic-reconciliation-20261015`
Mission scope: historical research reconciliation only.

## Governance preserved

- REAL_CAPITAL_AUTHORIZED = FALSE
- LIVE_TRADING_AUTHORIZED = FALSE
- No new backtest, sample extension, payoff computation, strategy tuning or prospective authorization was performed.
- Missing results remain UNKNOWN; no legacy result is recreated.

## Historical layers now recovered

### Layer A — legacy memory / early autonomous research
- `research/memory.jsonl`
- `research/opportunity_map.json`
- Includes NASDAQ short-horizon reversal (`TSR-NDX-001`) with historical `REJECT_RESEARCH` status.

### Layer B — deep research lab, 2026-09-24
Branch: `claude/deep-research-project-6vr22g`
Artifacts include `research/deep_research_2026-09-24/REPORT.md` and runnable experiment outputs.
The report states approximately 140 configurations were tested.
Recovered families include:
- multi-asset futures trend + carry;
- prediction-market favorite/longshot and latency diagnostics;
- crypto carry/momentum/reversal screens;
- equity factor lab;
- volatility management / risk-layer tests.

Important immutability notes:
- trend+carry historical result is retrospective lab evidence, not prospective validation;
- prediction-market close-price comparisons marked hindsight/CLV remain hindsight diagnostics;
- crypto carry findings do not create live authority.

### Layer C — structural edges lab, 2026-09-25
Branch: `claude/deep-research-project-6vr22g`
Artifact: `research/structural_edges_2026-09-25/REPORT.md` plus raw script outputs.
The report states approximately 60 variants were tested.
Recovered families include:
- Hyperliquid/CEX funding spread;
- pre-FOMC overnight effect;
- month-end pension rebalance;
- sports sharp-price / CLV diagnostics;
- prediction-market market-making / negative-risk / basis tests;
- liquidation rebound tests;
- turn-of-month / overnight / leveraged ETF proxy tests;
- SPAC / merger-arb / listing-fade research notes.

### Layer D — Weather lineage / governance / independent re-audits
Recovered from weather branches, Astra and Owner/Blue artifacts.
Rule preserved: repairs and audits are not silently upgraded into new economic evidence.

### Layer E — B2/B4 re-executions, 2026-10-08
Branch: `research/f2-primary-terms-decision-2026-10-09`
- Sector XRev B2: 36 EXISTING expressions, negative replication confirmed, `REJECT_RESEARCH`; no new discovery claim.
- Time-series macro B4: `DATASET_LEVEL_TRIAL_COUNT = 40`; `FAMILY_REJECTED` under the historical gate; positive selected net return did not rescue failed t-stat / half-sample / concentration criteria.

### Layer F — current Edge Lab / V4.2 discovery
Branch: `research/edge-lab-continuous`
Recovered examples:
- CFE VIX term premium: v0 PARK_DATA, v1 PARK_DATA, v2 reader repair PROMOTE_EXPRESSION; reader repair is not a fresh economic generation.
- Treasury 5Y / ZF: PARK_DATA due source adequacy / population issues; outcome exposure is retained in pristine/trial accounting.
- France OAT/Bund: PARK_DATA; no family-wide rejection.
- CFTC ES sentiment: PARK_DATA; economics never opened.
- Month-end pension V4.2 expression: PARK_DATA; economics never opened in that generation.
- Sector-relative shock reversal: KILL_EXPRESSION only.
- Stock/bond joint-stress rebound: KILL_EXPRESSION only.
- Crypto book-pressure prospective attempt: capture invalid / PARK_DATA; no valid trade sample.
- Russell deletion basket: PREDECLARED_NOT_ARMED / no economic result.
- SEC Form 4 EOD: recovery / data-decision lane, not a new research authorization.
- Corporate-action prospective protocols: registrations/preparations are not results.

### Layer G — F2 access decision
`research/kalshi_flb_f2/TERMS_DECISION_2026-10-09.md`
- `BLOCKED_DATA_PERMISSION`
- No Kalshi outcome data acquired under current rights.
- This is not an empirical rejection of favorite-longshot bias.

## Trial-accounting evidence recovered so far

Known or directly stated historical denominators:
- Deep research lab 2026-09-24: ~140 configurations (campaign-level count; per-family effective denominator not fully recoverable).
- Structural edges lab 2026-09-25: ~60 variants (campaign-level count; per-family effective denominator not fully recoverable).
- Sector XRev B2: 36 existing expressions.
- Time-series macro B4: DATASET_LEVEL_TRIAL_COUNT = 40.
- CFE VIX v0: planned 52 contracts; 36 usable HTTP-200 files before source failure. This is data coverage, not an effective-trial denominator.
- Russell deletion basket: one declared expression, one event cluster, eight dependent constituents; effective M explicitly UNKNOWN.

Do not sum these mechanically into a global effective-trial count. Overlap and researcher degrees of freedom remain material.

## Provenance gaps retained explicitly

The following mission-known historical assertions have not yet been bound to a durable primary artifact through the recovered repository surfaces and therefore must not be upgraded from UNKNOWN merely from recollection:
- MLB / soccer / weather replication result cited elsewhere as +0.1003% net;
- Box Office negative replay;
- some branch-only negatives cited later by the October board (for example listing-fade concentration) until primary artifacts are recovered;
- any exact effective-trial denominator not present in a registry/artifact.

If these primary artifacts remain unrecovered, the final ledger will preserve `RESULT = UNKNOWN` or `PROVENANCE = INCOMPLETE` as appropriate rather than recreate them.

## Duplication / ancestry rules fixed by this checkpoint

1. Reader/parser/source-format repair with unchanged economics = amendment / same economic generation unless source proves otherwise.
2. Horizon, universe, mechanism, execution timing or target-outcome material change = new generation.
3. Same broad market label does not imply same hypothesis.
4. Same economic mechanism under different names is marked SAME_HYPOTHESIS / VARIANT / SAME_MECHANISM_DIFFERENT_IMPLEMENTATION as evidence permits.
5. Retrospective development evidence never becomes prospective merely because later governance is stricter.
6. A KILL_EXPRESSION never becomes KILL_MECHANISM unless the original source explicitly supports family-level falsification.

## Next autonomous steps

- Finish ancestry across Weather, SEC Form 4, CFE, Treasury/ZF, France OAT/Bund, B2/B4 and September lab families.
- Bind negative knowledge and transferable lessons.
- Build duplication map.
- Normalize machine-readable ledger.
- Produce evidence-gap and migration recommendation artifacts.
- End only with COMPLETE or PARTIAL_WITH_EXPLICIT_GAPS.
