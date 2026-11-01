# Discovery V4.2 — US closed-end-fund rights small-holder step-up prospective L1 v1

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-15T11:15:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_TOTAL = 0

## Why this exists

The documentary L0 qualified a distinct, tiny-capacity allocation mechanism: some US listed closed-end-fund rights offerings grant a `step-up` privilege to a record-date shareholder who receives fewer rights than the normal ratio requires for one new share, allowing that holder to subscribe for one whole share without supplying the otherwise-missing rights.

All 2026 examples exposed during L0 are calibration/documentary contamination only. They MUST NOT count as fresh evidence, a pristine case, or support for profitability. This protocol therefore starts prospectively and selects the first eligible event strictly after `PROSPECTIVE_T0`.

## Mechanism

MECHANISM = A contractual small-holder step-up can waive the missing-right requirement for one subscription share when the record-date holder receives fewer rights than the normal subscription ratio. The incremental allocation is mechanically unavailable at scale to a single beneficial owner.

WHO_PAYS = Economically, the fund/issuer and nonparticipating or diluted shareholders bear the incremental allocation at the stated subscription price. Any apparent benefit is reduced by the cost and risk of holding the qualifying common shares, rights opportunity value, fees, taxes, price moves, dilution, delivery delay and cancellation/modification risk.

WHY_PERSIST = Capacity is intrinsically tiny, eligibility language varies, subscription-agent deadlines are operationally awkward, and a one-share privilege can be irrelevant to institutional capital. No multi-account multiplication is permitted.

MECHANISM_CLUSTER = subscription-rights-allocation

## Prospective universe — frozen before event access

Only a rights offering whose first qualifying definitive SEC filing has an EDGAR `accepted` timestamp STRICTLY AFTER `PROSPECTIVE_T0` may enter the sample.

Select the FIRST chronologically qualifying event. If two events have the same accepted timestamp, select the smaller issuer CIK. Do not skip an event because its subscription price, market price, ratio, expected discount or fund looks unattractive.

A qualifying event must satisfy ALL of the following using primary filings available at the public timestamp, before any selected market-price payload is read:

1. US exchange-listed closed-end management investment company common shares; exclude ETFs, operating companies, BDCs, preferred-only offers and private/non-listed funds.
2. A definitive public rights-offering filing/prospectus or subscription-agent exhibit states the rights ratio, record/entitlement mechanics, expiration deadline and subscription-price rule.
3. The same primary terms explicitly grant a small-holder `step-up` (or semantically equivalent) allowing a holder issued fewer rights than the normal whole-share ratio to subscribe for exactly one whole new common share without acquiring the missing rights.
4. One beneficial-owner position only. No multiple-account, nominee-fragmentation or household-splitting interpretation.
5. The public event occurs early enough that at least one regular exchange session remains in which the hypothetical qualifying common-share position could be acquired before the filing's operative entitlement cutoff, taking any explicit due-bill/ex-rights rule into account. If the record/entitlement opportunity is already closed when the terms become public, the case is ineligible.
6. The offer is still open and not already cancelled, completed or fully allocated at claim time.
7. A public daily OHLC route for the common shares can be documented before reading the selected event's prices. If not, PARK_DATA for the selected case; do not substitute a later event after seeing prices.

All issuers/funds and cases exposed in the 2026 L0 search — including BlackRock Capital Allocation Term Trust, Cohen & Steers Quality Income Realty Fund, UWM Holdings, Greenfire Resources and the other exposed rights-offering examples — are ineligible for fresh evidence under this protocol.

## Frozen hypothetical position

The test models one beneficial owner starting with zero shares before the event.

If the primary filing states that any holder receiving fewer than `R` rights may use the step-up privilege to purchase one new share, and one common share generates at least one right, then:

- `Q_ENTRY = 1` common share.
- `STEPUP_NEW_SHARES = 1`.
- The position must respect the exact beneficial-owner/record-holder aggregation language in the filing.

If one share does not qualify under the actual filing mechanics, set `Q_ENTRY` to the smallest whole-share count mechanically required by the filing BEFORE reading any selected market price. No alternative share-count search is allowed after price access.

## Event clock and acquisition convention

`EVENT_TIME` = EDGAR accepted timestamp of the earliest definitive primary filing that first publicly establishes every eligibility item above.

`ENTRY_SESSION` = first regular listing-exchange session whose official open occurs strictly after `EVENT_TIME` and still qualifies for the entitlement under the filing's record/due-bill/ex-rights mechanics.

`ENTRY_PRICE` = raw regular-session OPEN of the common shares on `ENTRY_SESSION` from the prequalified public daily route.

The qualifying shares are hypothetically held through the entitlement cutoff and through the subscription decision. No intraday optimization, alternate entry day, close substitution or event skipping is allowed.

## Subscription price

`SUBSCRIPTION_PRICE` is determined exactly by the primary filing's frozen formula. If the formula depends on future market/NAV values, record the formula at admission but do not read those values early.

If the final subscription price cannot be reconstructed from primary/public data exactly as specified, PARK_DATA. Do not replace it with an estimated or nearby formula.

## Stage A — mechanical incremental ceiling

Stage A asks only whether the one-share step-up has any economically interesting upper-bound value at the subscription deadline. It is not executable P&L and does not ignore the required qualifying-share position.

`REFERENCE_PRICE_A` = regular-session CLOSE on the official expiration date, or if the expiration occurs on a non-trading day, the immediately preceding regular-session CLOSE. This convention is frozen now.

`STEPUP_GROSS_A = REFERENCE_PRICE_A - SUBSCRIPTION_PRICE`.

`ENTRY_MARK_A = Q_ENTRY * (REFERENCE_PRICE_A - ENTRY_PRICE)`.

`CENTRAL_COST_A = 0.0010 * (Q_ENTRY * ENTRY_PRICE + SUBSCRIPTION_PRICE)`.

`CENTRAL_CASE_A = STEPUP_GROSS_A + ENTRY_MARK_A - CENTRAL_COST_A`.

Stress uses only one predeclared adverse case:

`STRESS_COST_A = 0.0025 * (Q_ENTRY * ENTRY_PRICE + SUBSCRIPTION_PRICE) + 25 USD`.

`STRESS_CASE_A = STEPUP_GROSS_A + ENTRY_MARK_A - STRESS_COST_A`.

These are screening marks only. They omit delivery-delay price risk, taxes, financing, subscription-agent rejection, broker handling, distribution changes, dilution between expiration and delivery, and the opportunity value of transferable rights. Their omission is favorable to the hypothesis.

### Stage-A decision

- `KILL_CASE` if `CENTRAL_CASE_A <= 0`.
- `PARK_ECONOMICS` if `CENTRAL_CASE_A > 0` but `STRESS_CASE_A <= 0`.
- `ADVANCE_TO_DELIVERY_CHECK` only if both are positive.

No Stage-A outcome can promote the family or establish executable alpha.

## Stage B — actual allocation and delivery check

Run only if Stage A reaches `ADVANCE_TO_DELIVERY_CHECK`, and only after primary/public completion documents identify the actual step-up allocation and delivery date or a sufficiently precise delivery window.

Requirements:

1. Primary terms/result evidence shows the qualifying small-holder step-up was actually honored for the selected offering, not cancelled or removed by amendment.
2. `DELIVERY_SESSION` = first regular session on or after the earliest date the new share is documented as available to holders; if exact availability cannot be established, PARK_DATA.
3. `DELIVERY_OPEN` = regular-session OPEN on `DELIVERY_SESSION`.
4. Compute the bounded two-share hypothetical mark:

`GROSS_B = Q_ENTRY * (DELIVERY_OPEN - ENTRY_PRICE) + 1 * (DELIVERY_OPEN - SUBSCRIPTION_PRICE)`.

`CENTRAL_B = GROSS_B - 0.0010 * (Q_ENTRY * ENTRY_PRICE + SUBSCRIPTION_PRICE + (Q_ENTRY + 1) * DELIVERY_OPEN)`.

`STRESS_B = GROSS_B - 0.0025 * (Q_ENTRY * ENTRY_PRICE + SUBSCRIPTION_PRICE + (Q_ENTRY + 1) * DELIVERY_OPEN) - 25 USD`.

Taxes, financing, distributions and broker-specific handling remain unmodeled and must be disclosed as favorable omissions.

### Stage-B decision

- `KILL_CASE` if the step-up was removed/not honored, the offer was cancelled, or `CENTRAL_B <= 0`.
- `PARK_ECONOMICS` if `CENTRAL_B > 0` but `STRESS_B <= 0`.
- `PARK_DATA` if allocation/delivery cannot be established without inference.
- `SURVIVES_PROSPECTIVE_CASE` only if the step-up was honored and both `CENTRAL_B` and `STRESS_B` are positive.

One surviving case is still not a family-level edge claim.

## Adequacy / blockers

PARK_DATA before reading a selected price payload if any of these are unresolved: exact first-public accepted timestamp, fund/listing status, rights ratio, explicit step-up language, beneficial-owner mechanics, entitlement cutoff, subscription-price formula, or documented public daily-price route.

After the selected event is claimed, a blocker does NOT authorize substitution of a later or more attractive event.

## Multiplicity and contamination

This is one causal family and one fixed economic expression. Historical 2026 examples already exposed are not trials. No parameter search over `Q_ENTRY`, cost levels, valuation dates, alternative exit dates, discount thresholds, rights ratios, fund types or offering structures is allowed after an outcome.

## Family evidence threshold

Collect prospective cases under this unchanged protocol. Family-level escalation may be considered only after at least 5 qualifying prospective cases. A later separately predeclared review may then ask whether at least 4/5 survived Stage B and whether median `STRESS_B` was positive.

Until then: no alpha, Sharpe, live-readiness, scalable-capacity or capital-authority claim.

## Inference rights

TEST_CAN_KILL = one prospective implementation case or the practicality of this exact small-holder expression.

TEST_CAN_SUPPORT = one case survives the frozen mechanical, cost and delivery checks and justifies collecting more prospective cases.

TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, REPEATABILITY, TAX_ADVANTAGE, BROKER_ELIGIBILITY, CAPACITY_BEYOND_ONE_BENEFICIAL_OWNER, OR MULTI_ACCOUNT_SCALING.

REAL_CAPITAL_AUTHORIZED and LIVE_TRADING_AUTHORIZED remain FALSE regardless of result.
