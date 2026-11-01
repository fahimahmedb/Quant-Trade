# Discovery V4.2 — Russell preliminary deletions, one calendar basket

ID = disc-russell-deletion-calendar-basket-l1-v1
STATUS = PREDECLARED_NO_OUTCOME_ACCESS; execution is NOT armed.
LEVEL = L1; LABEL = EXPLORATORY_RETROSPECTIVE.
REAL_CAPITAL_AUTHORIZED = FALSE; LIVE_TRADING_AUTHORIZED = FALSE.

## Decision and provenance

Decision for this preparation pass: PREPARE_L1, not a measured KILL or promotion. Complete the existing Russell L1_PREDECLARE question. The declaration becomes frozen only when published on the authorized remote branch. This is not a prospective clock declaration and admits no SEC event.

Reuse `../qualifications/russell-deletion-forced-flow-l0-2026-10-12.json`, SHA256 `54b46f9c195c6a75a5c7dcc93f052cb2751798aaf57216c1a03ada2822c68e7e`. That receipt records the first eight company rows, selected before quotes, from the official preliminary list:

- https://www.lseg.com/content/dam/ftse-russell/en_us/documents/other/ru3000-deletions-20260522.pdf ; cached HTTP 200, 182787 bytes, SHA256 `c6f176c2727ac1ddc35e394a0cbdd24ab3d095d54fba8d5424a983f6c364ac9e`.
- https://www.lseg.com/en/media-centre/press-releases/ftse-russell/2026/russell-reconstitution-2026-schedule ; schedule source already read in L0. Preliminary-list date May 22, effective rebalance June 26 after close. No new web access or claim that today's PDF proves its original publication contents/minute.

The fixed dates, row-prefix basket and fractional USD100 per name were selected in L0. Costs, benchmark, adequacy and verdict below are fixed now, before this worker accesses any selected quote. The primary L0 receipt is evidence, not permission to acquire from a provider whose automated extraction is prohibited.

## Mechanism and competing explanation

MECHANISM = Temporary inventory pressure from benchmark-constrained sellers around index removals may leave a subsequent rebound for buyers willing to warehouse small-company risk.
WHO_PAYS = Funds implementing benchmark membership changes near the scheduled close, paying immediacy/low tracking error; buyers bear equity, liquidity and company-specific risk.
WHY_PERSIST = Concentrated mandated timing and limited small-stock depth can exceed available inventory capacity; anticipatory arbitrage may instead eliminate the effect.
QUESTION = Does this one price-blind calendar basket have a large enough costed rebound, beyond a fixed broad small-cap benchmark, to justify further data work?
PRIMARY_SIGNATURE = Positive basket return after the rebalance close, net of deliberately material assumed friction, with broad participation and positive benchmark excess.
ALTERNATIVE_EXPLANATION = Ordinary small-cap/healthcare exposure, issuer news, risk compensation or alphabetic selection; no observed fund-flow variable establishes forced selling.
NEGATIVE_CONTROL = IWM over exactly the same two closes, descriptive market benchmark only. It is not a matched counterfactual or an independently traded candidate. There is no second control window or placebo search.

## Fixed population, timing and units

Exactly these eight names in original source-row order: AARD (Aardvark Therapeutics), ARAY (Accuray), ACTU (Actuate Therapeutics), AISP (Airship AI Holdings), ALDX (Aldeyra Therapeutics), ALIT (Alight A), AOUT (American Outdoor Brands), AVD (American Vanguard).

Do not read the final deletion list to drop names. Do not replace a missing/delisted/ticker-mapped name with a survivor or ninth row. Preliminary membership need not equal final membership; that limitation is part of this expression.

ENTRY = 2026-06-26 regular-session CLOSE, America/New_York (scheduled 16:00 EDT).
EXIT = 2026-07-06 regular-session CLOSE, America/New_York (scheduled 16:00 EDT).
No nearest-day replacement, intraday timing, window search, short leg or leverage. Dates are the L0 selection, not selected on observed returns. Hold through the whole interval, including the July 3 market holiday.

For each name i, illustrative entry capital = USD100, fractional quantity q_i = 100 / P_i,entry. Total funded capital = USD800. No rebalancing or compounding. Fractions are arithmetic normalization, not proof of brokerage availability. Maximum invested capital is USD800; mark-to-market loss within the holding interval remains unknown, and terminal returns are not a drawdown estimate. No margin/borrow/financing expense assumed for this fully cash-funded proxy; opportunity cost and taxes excluded explicitly.

g_i = P_i,exit / P_i,entry - 1.
G = mean(g_i) over all eight; B = IWM_exit / IWM_entry - 1.
CENTRAL_NET = G - 0.0100 (100 bps of entry capital, total USD8).
STRESS_NET = G - 0.0200 (200 bps, total USD16).
CENTRAL_EXCESS = G - B - 0.0100.
STRESS_EXCESS = G - B - 0.0200.
Name-level central net = g_i - 0.0100. USD net = 800 * basket net.

Costs are fixed total roundtrip hypotheses covering commission/spread/slippage, not authenticated historical costs or a guarantee conservative for illiquid names. Do not charge IWM trading costs because it is only a comparator. Break-even total friction is G for absolute return and G-B for benchmark excess, reported in bps; it is not an optimized fee choice. Report no annualized return, Sharpe or capital scaling promise.

## Fixed data route and adequacy

Proposed sole daily-price route: the existing Yahoo chart schema, `https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}` for the eight names and IWM. Reuse the repository's prior schema evidence; no new calibration ticker. Route access/rights must be resolved by existing evidence or a bounded documentary check before a price request. If explicitly prohibited, unavailable or unresolved, PARK_DATA for this declared route; do not bypass or silently substitute a vendor.

If route and software gates pass in a later run, publish the original declaration hash and one CAS claim BEFORE any selected price payload. Fixed request parameters: interval=1d, period1=2026-06-25T00:00:00Z, period2=2026-07-07T00:00:00Z (exclusive), events=div,splits, includeAdjustedClose=false. Order: AARD, ARAY, ACTU, AISP, ALDX, ALIT, AOUT, AVD, IWM. Extract only the two exact-session `indicators.quote[0].close` fields using provider timestamps and exchange timezone. Never use adjusted-close, OPEN, high/low or a different session. Provider quote.close is a secondary proxy; historical restatements and split normalization outside the window are not fully authenticated.

All-or-nothing adequacy: exactly eight identifiable USD listed common shares matching these named issuers plus the fixed IWM benchmark; unique correctly dated regular-session endpoints; finite strictly positive closes at both dates for all nine; no split, distribution, dividend, merger/conversion or symbol-identity ambiguity affecting the holding interval `(entry close, exit close]` as indicated by the returned metadata/actions. No return-magnitude filter. Missing corporate-action fields do not prove absence: an unresolvable action/schema ambiguity fails adequacy. A flagged action means PARK_DATA for the whole basket, never exclusion, adjustment or survivor replacement after return access. Data completeness cannot authenticate historical company survival or establish PIT membership.

On a request/parse/adequacy failure, preserve acquired private bytes/receipts and stop further requests; outcome exposure, if any, remains consumed. No retry, mirrors, alternate provider, re-download or silent repair. Fixed acquisition ceiling: nine requests, zero retries, <=2 MiB per operation, <=120 seconds per acquisition operation, <=60 minutes cumulative L1 agent work. Paid spend zero. CPU/tokens/global bill have no supplied global meter; never report invented measurements. Raw prices stay private; publish derived returns, hashes, failure details and original claim linkage only.

## Frozen decision and single positive contradiction

1. Access or all-or-nothing adequacy failure => PARK_DATA. Do not call it economic rejection; no INCONCLUSIVE escape for a disappointing adequate result.
2. Adequate CENTRAL_NET <= 0 => KILL_EXPRESSION only, even if benchmark-relative performance is positive.
3. Primary positive gate requires ALL: STRESS_NET > 0; CENTRAL_EXCESS >= 0.0050 (50 bps); STRESS_EXCESS > 0; at least five of eight names have name-level central net > 0. Strict/weak inequalities as written. Failure with CENTRAL_NET > 0 => PARK_ECONOMICS.
4. Only after the primary gate passes, perform exactly one adversary on the already acquired data: remove the single name with highest g_i; ASCII symbol order breaks ties. Recompute equal-weight net/excess for the remaining seven using the SAME 100/200 bps costs and SAME IWM B. PASS only if remaining STRESS_NET > 0 AND remaining CENTRAL_EXCESS > 0. No alternate exclusion, subset, sector hedge or threshold.
5. Primary gate + adversary PASS => PROMOTE_EXPRESSION, meaning further research is worth considering. Adversary failure => PARK_ECONOMICS. Neither PROMOTE_MECHANISM nor PROMOTE_HIGH is available from this single correlated event.

TEST_CAN_KILL = this exact eight-name preliminary-list calendar expression (KILL_EXPRESSION).
TEST_CAN_SUPPORT = this exact expression as a candidate for cleaner replication (PROMOTE_EXPRESSION).
TEST_CANNOT_SAY = KILL_MECHANISM, PROMOTE_MECHANISM, PROMOTE_HIGH, alpha, forced-flow causality, executable fills, capacity, live readiness, confirmation or that all index-removal effects are absent.

BIAS_DIRECTION: preliminary-list misclassification can dilute the hypothesized signal but need not do so; alphabetic prefix/sector concentration and current-document/survivor availability can bias either way; ignoring actual execution costs/failed exits can overstate capture; raw-close omissions of corporate actions can bias either way (adequacy gate handles detected cases); IWM controls only coarse market direction, not sector/style risk. Requiring large fixed friction does not establish robustness to all of these biases.

## Exposures, accounting and next

One expression, one rebalance-date cluster, eight dependent constituents, one fixed benchmark, two cost reports and at most one conditional concentration adversary. None is an independent holdout. No bootstrap confidence interval from eight names or pseudo-independent daily observations. Describe range/median/breadth and benchmark excess; uncertainty/power remains weak at one event cluster. Effective M, earlier private history and overlap with older equity exposures remain UNKNOWN. B2/B4 and all other closed families/results stay closed: this event-list mechanism is not a renamed signal/grid and confers no fresh-data claim for IWM.

Prior public exposure: general reconstitution-pressure literature; the eight issuer identities and June/July dates in the cached L0; past Yahoo schema calibration elsewhere; historical/private market exposure UNKNOWN. An initial status-read in this pass also displayed the already published VX result embedded in Discovery STATE; it created no VX acquisition/recalculation and is not independent evidence. No selected Russell/IWM return, quote, NAV, payout, final-list filter or new SEC issuer body was accessed in this pass.

RESULT = L1_PREPARATION_COMPLETED_NO_ECONOMIC_RESULT.
EFFECT_SIZE = NOT_COMPUTED.
UNCERTAINTY = First-public list authenticity, actual removal/flow, price/corporate-action availability, rights and execution remain unestablished.
POWER_LIMITATION = One event cluster; no population or causal claim.
ECONOMIC_SIGNIFICANCE = A large broad costed rebound could justify cleaner evidence; no expected profit estimated.
FAILED_CRITERIA = No outcome attempted; runnable adapter and route-rights preflight not yet qualified.
LESSON = An initial deletion list can define a price-blind test, provided missing names/actions fail the basket instead of causing selection after results.
FAMILY_STATUS = PREDECLARED_NOT_ARMED; original L0 question COMPLETED.
NEXT_DECISION = On fresh HEAD/CONTROL, give A-E first-event admission priority after October 13 10:00Z. If no eligible event/unfinished economic look, reuse this declaration for a single bounded source-permission/software preflight (<=15 minutes, <=3 primary documentary requests, no prices); then claim once through the existing Discovery runtime only if admissible, or PARK_DATA with precise cause. No generic framework, no new calibration outcome, no forced bypass of unsupported runner. This pass ends after publishing preparation.
