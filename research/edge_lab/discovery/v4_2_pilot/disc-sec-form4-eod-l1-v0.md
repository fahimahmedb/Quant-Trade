# V4.2 pilot contract — SEC / Form 4 EOD

`EXPERIMENT_ID = disc-sec-form4-eod-l1-v0`

`STATUS = PREDECLARED_DESIGN_ONLY`

`LEVEL = L1`

`LIVE_CAPITAL = FORBIDDEN`

## 1. Decision targeted

Decide whether one simple, publication-timestamp-aware Form 4 purchase expression deserves the expensive PIT security-mapping / delist / corporate-action reconstruction, or should be killed/parked at the EOD-proxy stage.

## 2. Expression tested

- event: issuer-day with at least one Form 4 open-market purchase transaction (`transactionCode = P`) available in the existing SEC census;
- information clock: use filing/publication timestamp, never transaction date as tradable availability;
- activation rule: first full U.S. trading day after public filing availability;
- entry proxy: close of that first full trading day;
- exit proxy: close 20 U.S. trading days later;
- outcome: equal-weight issuer-event return minus a fixed broad U.S. equity benchmark return over the same interval;
- duplicate handling: multiple same-issuer filings on the same activation day collapse to one issuer-event; no size threshold tuning;
- no post-result sector, insider-title, market-cap, purchase-size, horizon, or threshold slicing inside this experiment.

If a required issuer cannot be mapped to a contemporaneous public EOD series under the cheap proxy, record the mapping failure. Do not silently drop it without reporting coverage.

## 3. Mechanism contract

`MECHANISM` — some public insider purchases may reveal information or confidence that is incorporated into market prices with delay.

`WHO_PAYS` — counterparties / market participants slower to incorporate informative insider activity.

`WHY_PERSIST` — signal may be low-capacity, heterogeneous, operationally messy, and partially offset by noise; this is a hypothesis, not a conclusion.

`PRIMARY_SIGNATURE` — before outcomes, the mechanism predicts a positive benchmark-adjusted drift after public filing availability for purchase events. A stronger mechanistic version may later predict larger effect for economically larger purchases, but purchase-size monotonicity is **not** part of this L1 unless the scaling denominator is already PIT-clean.

`ALTERNATIVE_EXPLANATION` — any positive drift may reflect small-cap/value/illiquidity exposure, issuer selection, survivorship, or delayed corporate news unrelated to insider informational content.

## 4. Inference rights

### TEST_CAN_KILL

A negative/null result can kill **this exact EOD purchase expression** only if:

1. public filing timestamps are available and used causally;
2. mapping coverage is high enough to avoid a result driven by systematic exclusions;
3. the sample is not dominated by a few issuers/events;
4. benchmark-adjusted returns are computable consistently; and
5. there is enough event count for the test to have a reasonable chance of detecting an effect of economically relevant size.

Failure on any of these adequacy conditions implies `PARK_DATA` or `INCONCLUSIVE`, not a mechanism kill.

A negative result does not by itself kill all insider-information mechanisms.

### TEST_CAN_SUPPORT

A positive result can support only:

- `PROMOTE_EXPRESSION` toward PIT CIK/security mapping, delists, corporate actions and cleaner execution timing;
- `PROMOTE_MECHANISM` only if the predeclared red-team below weakens the strongest obvious confound without erasing the effect;
- never capturability or causal private-information proof.

### TEST_CANNOT_SAY

This L1 cannot establish:

- that insiders possess/acted on private information;
- same-day or intraday tradability;
- survivorship-safe PnL;
- executable spreads/slippage;
- capacity;
- live readiness;
- robustness across insider roles, purchase sizes, sectors or market regimes not predeclared here.

## 5. Bias map

| Dimension | Expected L1 bias |
|---|---|
| Signal amplitude | UNKNOWN; survivorship/mapping omissions may bias up, conservative activation delay may bias down |
| Timing | CONSERVATIVE relative to faster reaction because entry waits for a full trading day after filing |
| Costs | UPWARD until explicit EOD transaction-cost band is subtracted |
| Survivorship | POTENTIALLY UPWARD if delisted/dead securities are under-mapped |
| Execution quality | UPWARD; closes are proxies, not guaranteed fills |
| Capacity | UNSPOKEN / cannot infer |

## 6. Data adequacy required for a negative to be informative

Record before verdict:

- total eligible Form 4 purchase issuer-events;
- fraction with valid filing timestamps;
- fraction mapped to a contemporaneous EOD security series;
- fraction excluded and exclusion reasons;
- concentration by issuer;
- number of events with complete 20-trading-day follow-up;
- obvious delist/dead-security omissions under the proxy.

No ex-post minimum sample cutoff may be invented. If coverage is obviously too weak to distinguish a plausible effect, use `PARK_DATA`/`INCONCLUSIVE`.

## 7. Unit-economics envelope before reconstruction

Estimate only:

- event frequency per month/year;
- median number of simultaneous positions;
- gross benchmark-adjusted effect size under this expression;
- small-account trade-size plausibility;
- rough round-trip friction interval for ordinary U.S. equities;
- sensitivity to one full-day execution delay;
- whether a plausible edge remains after excluding obviously tiny/illiquid names **only in a future new experiment**, not by tuning this one.

`BREAK_EVEN_FRICTION` is the gross per-trade friction that would consume the observed effect. Promotion requires meaningful headroom versus a defensible small-account friction interval.

## 8. Predeclared cheap red-team if L1 is positive

`RED_TEAM = naive market/size-liquidity confound`

Use one predeclared coarse confound check that does not require a full factor platform: compare the purchase-event drift against a simple matched or stratified benchmark available from already-accessible public EOD metadata (for example coarse market-cap/liquidity bucket if available without heavy engineering).

If a defensible cheap match is unavailable, do **not** invent one after seeing returns. Stop at `PROMOTE_EXPRESSION` and make the confound test an L2 requirement.

## 9. Verdict map

- `KILL_EXPRESSION` — exact filing-aware EOD purchase expression fails with adequate coverage/power.
- `KILL_MECHANISM` — forbidden from this single L1 unless the predeclared primary signature and a favorable bound both fail with strong data adequacy; explicit justification required.
- `PARK_DATA` — timestamp/mapping/survivorship coverage prevents interpretation.
- `PARK_ECONOMICS` — effect may exist but frequency/headroom/capacity is too weak for the project objective.
- `PROMOTE_EXPRESSION` — positive, economically meaningful drift justifies PIT reconstruction.
- `PROMOTE_MECHANISM` — positive drift plus cheap confound check supports the specific informational-delay story.
- `PROMOTE_HIGH` — only if effect size, headroom, coverage and red-team survival are unusually strong.
- `INCONCLUSIVE` — only for predeclared adequacy failure.

## 10. Anti-requalification

Any post-result change to filing clock, activation day, event code, benchmark, horizon, universe, duplicate rule, size filter, insider role filter, cost assumption or mapping rule is a new linked experiment in the same mechanism cluster.
