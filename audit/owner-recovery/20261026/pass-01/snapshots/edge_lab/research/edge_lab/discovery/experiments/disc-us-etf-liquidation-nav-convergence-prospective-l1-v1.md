# Discovery V4.2 — US ETF liquidation NAV convergence prospective L1 v1

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-12T21:00:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Mechanism

MECHANISM = A terminating ETF that has announced a last trading date and a later cash liquidation date may temporarily trade below its terminal residual NAV because ordinary secondary-market liquidity and AP arbitrage weaken as the fund winds down, while holders willing to tolerate delisting/settlement nuisance receive the final pro-rata liquidation distribution.
WHO_PAYS = Sellers demanding immediate liquidity before delisting if they accept a discount to terminal fund value.
WHY_PERSIST = Tiny fund size, uncertain liquidation expenses, tax/settlement nuisance, trading restrictions and short-lived event windows limit capacity and institutional attractiveness.
MECHANISM_CLUSTER = fund-liquidation-forced-cash

## Prospective universe — frozen

Eligible event = FIRST SEC EDGAR Rule 497 / 497K filing with accepted timestamp strictly after PROSPECTIVE_T0 that newly announces liquidation of a US exchange-listed ETF and provides both a final regular exchange trading date and a later liquidation/distribution date.

Tie at same accepted timestamp => smaller registrant CIK, then lexicographically smaller ticker.

Exclude:
- mutual funds / non-exchange-listed funds;
- CEFs;
- mergers/reorganizations into another fund;
- cases without a fixed last trading date;
- cases where the liquidation distribution has already occurred at claim time;
- all funds/registrants exposed during the 2026-10-12 L0 search, including Theme ETF Trust examples, CrossingBridge Ultra-Short Duration ETF, Schwab Ariel Opportunities ETF, Deepwater Beachfront Small Cap ETF, Defiance Daily Target 2X Long ZETA ETF, the exposed Direxion liquidation set, and Innovator Uncapped Bitcoin 20 Floor ETF.

Do not skip the first qualifying event because the fund is illiquid, unattractive or the apparent spread is small.

## Claim ordering

Before reading any market price, NAV value or liquidating-distribution amount for the selected fund:
1. persist the exact SEC accession, registrant CIK, ticker, accepted timestamp, last trading date, liquidation date and source URL;
2. prove the event is the first observed chronologically qualifying event under the bounded SEC feed used;
3. document one public daily exchange-close route and one issuer/fund NAV route without reading their selected-event numeric payloads;
4. if either route cannot be documented, PARK_DATA the selected event; do not substitute another event.

## Stage A — final-trading-day NAV discount

ENTRY_SESSION = announced final regular exchange trading session.
ENTRY_PRICE = official/raw regular-session CLOSE from the prequalified public daily-price route.
NAV_REFERENCE = issuer-published per-share NAV for the same date, using a value published at/after that session close under the prequalified route.
Q_NORM = 1 share.
Q_EXAMPLE = 100 shares only as a fixed dollar illustration; never used to choose or promote a case.

GROSS_DISCOUNT_PER_SHARE = NAV_REFERENCE - ENTRY_PRICE.
CENTRAL_FRICTION = 0.0020 * ENTRY_PRICE.
STRESS_FRICTION = 0.0050 * ENTRY_PRICE + (10 / 100) for the fixed 100-share illustration, i.e. $0.10/share flat equivalent.
CENTRAL_STAGE_A = GROSS_DISCOUNT_PER_SHARE - CENTRAL_FRICTION.
STRESS_STAGE_A = GROSS_DISCOUNT_PER_SHARE - STRESS_FRICTION.

Decision:
- KILL_CASE if CENTRAL_STAGE_A <= 0.
- PARK_ECONOMICS if CENTRAL_STAGE_A > 0 but STRESS_STAGE_A <= 0.
- ADVANCE_TO_LIQUIDATION_CHECK only if both are > 0.

No alternate close, intraday low, VWAP, next-day OTC quote, NAV timestamp, quantity, fee or issuer substitution is allowed.

## Stage B — realized liquidation check

Run only after ADVANCE_TO_LIQUIDATION_CHECK and after a primary public source states the actual per-share cash liquidation distribution.

FINAL_CASH_PER_SHARE = documented terminal cash distribution attributable to one share, excluding unrelated later tax corrections unless explicitly part of the liquidation payment.
CENTRAL_REALIZED = FINAL_CASH_PER_SHARE - ENTRY_PRICE - CENTRAL_FRICTION.
STRESS_REALIZED = FINAL_CASH_PER_SHARE - ENTRY_PRICE - STRESS_FRICTION.

- KILL_CASE if CENTRAL_REALIZED <= 0.
- PARK_ECONOMICS if CENTRAL_REALIZED > 0 but STRESS_REALIZED <= 0.
- SURVIVES_PROSPECTIVE_CASE only if STRESS_REALIZED > 0.

A single survivor cannot promote or validate the family.

## Family threshold

Collect without modifying v1. Family-level escalation may be considered only after at least 5 qualifying prospective cases, with a separately predeclared review. No threshold tuning, fund-type filtering, sponsor filtering, date-window changes or post-outcome exclusion.

## Adequacy / blockers

PARK_DATA before economic access if any is unresolved: exact SEC accepted timestamp, ticker/listing, final trading date, later liquidation date, close-price route, same-date issuer NAV route, or later primary distribution route.

## Inference rights

TEST_CAN_KILL = one prospective liquidation-convergence case.
TEST_CAN_SUPPORT = one case surviving both same-date NAV discount and actual terminal cash under fixed stress friction.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, TAX_TREATMENT, BROKER_ELIGIBILITY, REPEATABILITY, CAPACITY OR FAMILY PROFITABILITY.

No real capital or live trading is authorized regardless of result.
