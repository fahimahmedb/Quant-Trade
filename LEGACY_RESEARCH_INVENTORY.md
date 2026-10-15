# Quant-Trade — Canonical Legacy Economic Research Inventory

Reconciliation date: 2026-10-15  
Branch: `research/legacy-economic-reconciliation-20261015`  
Status: `PARTIAL_WITH_EXPLICIT_GAPS`

This inventory is the human-auditable entry point to the historical economic research memory. It preserves recovered results and limitations without running new economics.

## Governance invariants

- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- No new signal→future-return or PnL calculation was performed.
- No old sample was extended.
- No strategy was retuned.
- No prospective observation was authorized.
- Historical verdicts remain immutable.
- Missing primary evidence is `UNKNOWN`, never reconstructed from memory.

## Canonical artifacts in this reconciliation

- `LEGACY_RESEARCH_LEDGER.json` — machine-readable normalized core ledger.
- `LEGACY_HYPOTHESIS_ANCESTRY.md` — experiment genealogy and amendment/material-change distinctions.
- `LEGACY_NEGATIVE_KNOWLEDGE.md` — failures, falsification scope and transferable lessons.
- `LEGACY_DUPLICATION_MAP.md` — same-hypothesis / variant / related-mechanism relationships.
- `LEGACY_EVIDENCE_GAPS.md` — unrecovered provenance, trial and evidence gaps.
- `LEGACY_MIGRATION_RECOMMENDATION.md` — conceptual migration rules and final decision matrix.

## Recovered historical research map

### Equity / cross-sectional / factors

1. **TSR-NDX-001 — NASDAQ short-horizon reversal**: historical `REJECT_RESEARCH`; fixed expression should not be restarted merely because the framework is newer.
2. **B2 sector XRev**: 36 existing expressions; negative replication confirmed; `REJECT_RESEARCH` on spent data.
3. **Sector-relative shock reversal**: later variant; `KILL_EXPRESSION`, not mechanism-wide kill.
4. **Equity factor lab**: 65 configurations; most classic factor opportunities weakened post-2000; BAB with vol management was the principal historical survivor but recent decay remained material.
5. **Russell preliminary deletion basket**: predeclared/not armed; no outcome access; one event cluster and effective M unknown.
6. **Leveraged-ETF flow proxy / generic overnight / turn-of-month**: recovered in the September structural lab; simple proxy/calendar variants did not establish robust standalone edges.

### Trend / macro / calendar

7. **Broad futures trend + carry**: strong retrospective history (reported combined SR 1.06, t=6.9) with breadth effect, but survivorship/execution/cost and prospective gaps remain. It is not the same experiment as B4.
8. **B4 SPY/TLT/GLD TSMOM**: 40 dataset-level trials; `FAMILY_REJECTED` under the historical gate despite a positive selected net point estimate.
9. **FOMC pre-announcement overnight**: retrospective positive inside a broad exploratory campaign; requires prospective/authority gap completion rather than rediscovery.
10. **Month-end pension rebalance**: September retrospective screen was indicative; later formal Edge Lab generation `PARK_DATA` and computed no new economics.
11. **Broader policy-announcement repricing**: current state `PARK_UNTIL_AUTHORITY`; do not inherit the FOMC result as validation of the broader lane.

### Crypto / financing / forced flow

12. **Historical crypto carry**: BTC carry was historically strong but decayed toward/below the cash hurdle by the recovered 2026 regime; altcoin cross-sectional carry was weak after costs.
13. **Hyperliquid/CEX funding spread**: strong retrospective modeled result with weaker later-period economics and material ADL/one-leg/venue execution risk; promising but underproved.
14. **Binance extreme-funding reversal**: frozen one-shot run `PARK_DATA` after official endpoint HTTP 451; economics not computed.
15. **Simple liquidation-cascade rebound**: negative/unstable in the recovered hourly tests, especially later slices; do not rediscover the simple rule.
16. **Hyperliquid forced-flow paused lane**: `PARK_DATA_CONFIRMED`; exact primary qualification provenance remains incomplete in this reconciliation and the lane must not be conflated with the simple liquidation-rebound rule.
17. **Crypto book-pressure prospective attempt**: prospective timing but invalid capture; 21 responses lacked usable book fields, zero valid trades, `CAPTURE_INVALID/PARK_DATA`.

### Prediction markets / sports

18. **Generic favorite-longshot bias**: historical sign changed across samples and execution surfaces; no stable generic taker rule was established.
19. **F2 Kalshi favorite-longshot OOS**: cleaner modified protocol, but `BLOCKED_DATA_PERMISSION`; no outcome data acquired and no new economic evidence.
20. **BTC→prediction-market latency**: retrospective lead existed only around ≤1s and disappeared at 3s/5s; operationally a latency/infrastructure phenomenon, not a slow accessible edge.
21. **Prediction-market negRisk/combinatorial arbitrage**: tested implementation largely dead after fees; cross-venue rule mismatches created basis risk rather than clean arbitrage.
22. **Sports sharp-price / CLV research**: ~68,952 football matches; causal open/open and hindsight close/CLV diagnostics must remain separated. Some filtered retrospective variants were positive, but multiplicity and feed/execution gaps remain.
23. **Prediction-market market-making / category microstructure observations**: historical research suggests maker economics differ materially from taker biases; these are independent mechanism classes and must not be used to rescue FLB results.

### Volatility / rates / sovereign

24. **CFE VIX term premium**: v0/v1 `PARK_DATA`; v2 reader repair `PROMOTE_EXPRESSION` with unchanged economics and no independent observations. This is `PROMOTED_EXPRESSION_NOT_EDGE`, and current state is `NO_NEW_ECONOMIC_ACTION`.
25. **Treasury 5Y auction concession / ZF auction pressure**: same mechanism with different implementations; historical results `PARK_DATA`; later `L0_DAILY_SOURCE_GATE_PASS` is only a source qualification state.
26. **France OAT/Bund repricing**: v0 and public-daily-route generation `PARK_DATA`; later `L0_DAILY_SOURCE_GATE_PASS`; no family-wide rejection and no canonical positive result.
27. **CFTC ES leveraged-fund sentiment extremes**: `PARK_DATA`; economics never opened.
28. **Stock/bond joint-stress rebound**: `KILL_EXPRESSION`; scope does not extend to every cross-asset stress mechanism.

### SEC / corporate actions

29. **SEC Form 4 insider-purchase clusters**: historical real raw capture existed; 20 distinct accessions were previously acquired; 66 historical Actions runs recovered; 3 successful historical runs currently expose no retained artifacts; deterministic census publication did not land durably in Git. Later EOD lane is `PARK_DATA`, `economic_test_count=0`. This is recovery/completion, not new research. No rebuild is authorized.
30. **Corporate-action prospective protocols**: recovered declarations include CEF rights, CEF DRIP discounted issuance, ETF liquidation NAV convergence, odd-lot priority, reverse-split cash-in-lieu, reverse-split round-up and SPAC redemption floor. These are protocol/declaration states, not completed economic results.

### Weather

31. **Weather V1 → V2 → V3 → V4** is a research-design lineage, not a ladder of validated edges.
   - V2: blocked by a false-economic-exclusion defect in the structured-bound design; audit outcome-blind/synthetic.
   - V3: later summarized as `V3_NOT_JUSTIFIED`, no demonstrated prospective edge.
   - V4: material mechanism shift toward resolution source, information timing, repricing and microstructure; pre-op audit passed only for Owner consideration; `OWNER_PHASE_GATE = NOT_GRANTED`.
   - No recovered Weather generation has `PROSPECTIVE_VALIDATED = TRUE`.

### Unrecovered primary results

32. **MLB / soccer / weather replication bundle**: known historically, but primary durable artifact not recovered. `RESULT = UNKNOWN` in the canonical ledger; do not recreate solely to fill the gap.
33. **Box Office replay**: remembered as historical work, but primary result artifact not recovered. Canonical result remains `UNKNOWN` until provenance is found.

## Trial accounting

### Exact or explicit recovered denominators

- B2 sector XRev: **36** existing expressions.
- B4 macro TSMOM: **40** dataset-level trials.
- Equity factor lab: **65** configurations.

### Campaign-level partial bounds

- Deep research 2026-09-24: approximately **140 configurations** across multiple families.
- Structural edges 2026-09-25: approximately **60 variants** across multiple families.

These numbers must **not** be summed mechanically. Families overlap, variants are correlated, and no complete global researcher-degree-of-freedom registry exists.

`GLOBAL_EFFECTIVE_TRIALS = UNKNOWN`

## Evidence timing summary

- Retrospective positive/negative evidence exists across many families.
- Genuine OOS exists in some historical protocols (for example B2/B4 internal historical validation structure), but it remains retrospective from today's vantage point and cannot be relabelled prospective.
- Prospective registrations exist.
- One prospective crypto capture was attempted but invalid.
- **No recovered canonical family has completed valid prospective economic validation.**

`PROSPECTIVE_VALIDATED = 0`

## Negative knowledge that materially changes future work

The strongest anti-restart lessons are:

- sector ETF reversal has already consumed a substantial expression family and a later shock variant;
- small-universe ETF trend B4 is spent/rejected and must not be rescued by post-hoc thresholds;
- broad futures trend/carry remains distinct from B4 and should not be rediscovered from zero;
- generic FLB signs are sample-dependent;
- easy prediction-market arbitrage is generally eaten by fees/settlement basis;
- simple hourly liquidation rebound is not robust;
- Weather V2/V3 failures are design/program knowledge, not alpha negatives;
- technical/data failures must remain `PARK_DATA`, not be rewritten as negative returns;
- Form 4 workflow existence is not a durable census and must be recovered before any economic continuation;
- reader/parser repairs share the parent economic lineage and do not reset trials.

## Research-status map

### TESTED_AND_KILLED / NO repeat as-is
- TSR-NDX fixed expression.
- B2 36-expression family as expressed.
- B4 small-universe family on spent validation data.
- sector-shock expression.
- stock/bond stress expression.
- generic tested negRisk/combinatorial implementation.
- simple hourly liquidation-rebound implementation.

### TESTED_BUT_UNCERTAIN / PROMISING_BUT_UNDERPROVED
- broad futures trend+carry;
- HL/CEX funding spread;
- FOMC overnight;
- month-end pension;
- sports sharp-price/CLV variants.

### BLOCKED_BY_DATA / COST / PERMISSION / AUTHORITY
- Treasury/ZF: data/source lineage completion.
- France OAT/Bund: data-route completion.
- CFTC ES: data.
- SEC Form 4: durable census/price-route evidence.
- F2: permission.
- Hyperliquid forced-flow: qualified data blocker.
- Policy announcement: authority.
- Binance funding reversal: source access in historical run.
- crypto book pressure: invalid capture requires a new authorized prospective generation.

### PROMOTED_EXPRESSION_NOT_EDGE
- CFE VIX reader-repaired expression.

### REQUIRES_PROSPECTIVE_VALIDATION
Every retrospectively positive family that could ever be reconsidered economically.

### GENUINELY_UNEXPLORED
`UNKNOWN`. Repository archaeology cannot prove that the complement of recovered work was never privately/unmerged/deleted/researched.

## Economic identity map — recoverable examples

| Family | Payer / mechanism | Main exposure | Main cost/risk driver |
|---|---|---|---|
| Broad trend+carry | hedgers / trend underreaction + carry | diversified directional trend + term/carry | turnover, spreads, rolls, breadth/capital |
| B4 | market trend | directional ETF trend | turnover, borrow/cost assumptions, concentration |
| Sector reversal | shocked sector investors / liquidity | mean reversion, relative-value | turnover, beta/style leakage |
| Month-end pension | institutional rebalancers | calendar flow / equity-bond imbalance | timing and proxy validity |
| FOMC overnight | policy-event risk transfer | equity overnight beta/event premium | event crowding, execution |
| Crypto carry | perp longs paying funding | low-direction financing premium + venue tail risk | fees, basis, liquidation/ADL, cash hurdle |
| HL/CEX spread | segmented venue participants | relative funding/basis | double-leg execution, ADL, venue risk |
| CFE VIX | volatility hedgers/risk premium | short-vol/term-premium exposure likely | tail risk, settlement/execution |
| Treasury/ZF | auction participants / supply | rates duration/event repricing | event timing, source integrity, slippage |
| OAT/Bund | French sovereign risk repricing | relative duration/credit-political spread | event timing, basis, data route |
| Form 4 | informed insiders versus market | small-cap/idiosyncratic event exposure | survivorship/delist, liquidity, costs |
| Russell deletion | benchmark-constrained sellers | small-cap liquidity/forced-flow | event clustering, issuer risk, costs |

Fields not established by evidence remain `UNKNOWN`; this table is not expanded by inference.

## Final decision matrix

The authoritative full matrix is in `LEGACY_MIGRATION_RECOMMENDATION.md`. Its default is **NO repeat** whenever prior work already answered the same question. `YES_WITH_NEW_GENERATION` is reserved for materially different future evidence regimes, not cosmetic variants.

## Final verdict

```text
LEGACY_RECONCILIATION_STATUS = PARTIAL_WITH_EXPLICIT_GAPS
HISTORICAL_RESEARCH_ITEMS_FOUND = 33_INVENTORY_ENTRIES_INCLUDING_2_PRIMARY_PROVENANCE_GAPS_AND_1_BUNDLED_7_PROTOCOL_GROUP
DISTINCT_MECHANISM_FAMILIES = AT_LEAST_24_RECOVERABLE; EXACT_GLOBAL_COUNT_UNKNOWN_DUE_BUNDLING_AND_UNRECOVERED_ARTIFACTS
KNOWN_DUPLICATE_OR_VARIANT_ITEMS = 17_CLASSIFIED_RELATIONSHIPS_IN_DUPLICATION_MAP
KILLED_FAMILIES = 3_FAMILY_OR_CLOSED-FAMILY_LEVEL_CASES_RECOVERED; ADDITIONAL_EXPRESSION_LEVEL_KILLS_PRESERVED_SEPARATELY
PARKED_FAMILIES = AT_LEAST_13_FAMILY_OR_GENERATION_STATES_CURRENTLY_BLOCKED_OR_PARKED
PROMOTED_BUT_NOT_VALIDATED = 1_CFE_VIX_EXPRESSION
PROSPECTIVE_VALIDATED = 0
EFFECTIVE_TRIALS_KNOWN = 3_EXACT_DENOMINATORS_RECOVERED: 36, 40, 65; GLOBAL_EFFECTIVE_TRIALS_UNKNOWN
EFFECTIVE_TRIALS_UNKNOWN = MOST_OTHER_FAMILIES_AND_GLOBAL_DENOMINATOR
RESEARCH_THAT_MUST_NOT_BE_REPEATED = B2_36_EXPRESSIONS; B4_SPENT_FAMILY/WINDOW; EXACT_SECTOR_SHOCK; EXACT_STOCKBOND_STRESS; TESTED_NEGRISK; SIMPLE_HOURLY_LIQUIDATION_REBOUND; LEGACY_TSR_NDX; WEATHER_V1-V3_AS_IF_NEW; FORM4_CENSUS_REBUILD_BEFORE_RECOVERY
RESEARCH_REQUIRING_ONLY_GAP_COMPLETION = TREASURY/ZF; FRANCE_OAT/BUND; SEC_FORM4_RECOVERY; CFTC_ES; FORMAL_MONTHEND_PENSION; F2_PERMISSION; HYPERLIQUID_DATA; CFE_DISTINCT_EVIDENCE_PACKAGE; SELECTED_PROSPECTIVE_PROTOCOLS_IF_SEPARATELY_AUTHORIZED
GENUINELY_UNEXPLORED_SPACES = UNKNOWN
OWNER_DECISIONS_REQUIRED = POLICY_ANNOUNCEMENT_AUTHORITY; ANY_WEATHER_PHASE_REOPENING; ANY_NEW_PROSPECTIVE_OBSERVATION; ANY_BUILDER/NEW_ECONOMIC_TEST/CAPITAL/LIVE_AUTHORIZATION; F2_OR_OTHER_RIGHTS-DEPENDENT_RESEARCH_ONLY_AFTER_DOCUMENTED_PERMISSION
```

The reconciliation is deliberately `PARTIAL_WITH_EXPLICIT_GAPS`, not `COMPLETE`, because two named historical result families still lack their primary durable artifacts and the global effective-trial denominator cannot be reconstructed honestly. The knowledge base is nevertheless sufficient to prevent major known research families from being restarted blindly.
