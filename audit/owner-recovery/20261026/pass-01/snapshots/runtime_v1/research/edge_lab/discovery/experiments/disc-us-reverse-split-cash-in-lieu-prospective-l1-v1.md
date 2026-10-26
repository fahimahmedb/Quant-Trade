# Discovery V4.2 — US reverse-split cash-in-lieu prospective L1 v1

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-12T20:00:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Purpose

Test whether a publicly announced reverse split with an explicit cash-in-lieu formula can create a positive small-account economic ceiling after a strictly post-announcement entry. Historical examples used in L0 are calibration/exposure only and are permanently excluded from this prospective sample.

## Mechanism

MECHANISM = a reverse split converts a pre-split position into a fractional post-split entitlement, and the issuer/agent settles the fraction using a document-defined cash formula instead of issuing the fraction.
WHO_PAYS = issuer/corporate-action settlement process.
WHY_PERSIST = if any positive mismatch exists it is intrinsically tiny-capacity, event-specific, operationally annoying, and exposed to broker aggregation/reorganization fees.
MECHANISM_CLUSTER = corporate-action-fractional-settlement.

This protocol does not assume that cash-in-lieu itself creates value. The intended first test is deliberately able to kill the mechanism if the formula merely reproduces ordinary market value.

## Prospective universe — frozen

Only an event whose first public SEC filing containing the operative reverse-split terms has EDGAR `accepted` STRICTLY AFTER PROSPECTIVE_T0 is eligible. Select the FIRST chronologically qualifying event. Same accepted timestamp => smaller issuer CIK. Do not skip an unattractive case.

All of the following must be true before any price payload is read:

1. Nasdaq, NYSE, or NYSE American listed operating-company common stock.
2. Reverse split ratio is fixed and stated in a primary SEC filing or incorporated exhibit.
3. Filing explicitly states that fractional post-split shares will NOT be issued and specifies cash-in-lieu treatment. Round-up-to-whole-share events are excluded from v1.
4. Cash formula is objectively reconstructible from primary documents: e.g. a stated exchange closing price, volume-weighted/average sale proceeds, or another fixed agent formula. If the formula remains discretionary/ambiguous, PARK_DATA.
5. Effective time / entitlement basis is explicit enough to determine whether shares bought after EVENT_TIME can still participate.
6. At least one regular exchange session open exists strictly after EVENT_TIME and strictly before the documented last time at which a purchase can obtain the split entitlement. Otherwise the event is INELIGIBLE before prices.
7. One public daily OHLC route is documented before payload access. If the selected symbol cannot be retrieved from that already-documented route, PARK_DATA; do not substitute another event after seeing prices.
8. No final cash-in-lieu amount, post-event payout result, or completion outcome has been intentionally read when the event is claimed.

The June/August 2026 issuers and CIKs already exposed during L0 are excluded forever from this prospective sample.

## Event clock and position — frozen

EVENT_TIME = EDGAR `accepted` timestamp of the first public filing/exhibit that makes ratio + effective time + cash treatment reconstructible.
ENTRY_SESSION = first regular trading session whose official open is strictly after EVENT_TIME and still qualifies under rule 6 above.
ENTRY_PRICE = raw regular-session OPEN on ENTRY_SESSION from the prequalified public route.

Let reverse split ratio be 1-for-R, R an integer > 1.
Q = R - 1 pre-split shares, capped at 99 shares. If R - 1 > 99, Q = 99. No quantity search after event selection.
POST_SPLIT_FRACTION = Q / R, provided Q < R; if Q >= R because of the 99-share cap/ratio relation, PARK_DATA for v1 rather than redesign quantity.

The hypothetical account starts with zero beneficial holdings. No account multiplication, cross-broker splitting, margin, shorting, or live order.

## Payout reconstruction

CASH_BASIS = the exact per-whole-post-split-share cash basis defined by primary documents, reconstructed only when the required fixing becomes public.
GROSS_CASH_PAYOUT = POST_SPLIT_FRACTION * CASH_BASIS.
ENTRY_COST = Q * ENTRY_PRICE.

If the issuer formula is expressed on a pre-split basis, normalize it algebraically to the same economic units before comparison and preserve the original formula in the result receipt.

## Frozen frictions

CENTRAL_ENTRY_FRICTION = 0.0010 * ENTRY_COST.
CENTRAL_REORG_FEE = 0 USD only as an optimistic ceiling, not a broker-fee claim.
CENTRAL_NET_CEILING = GROSS_CASH_PAYOUT - ENTRY_COST - CENTRAL_ENTRY_FRICTION.

STRESS_ENTRY_FRICTION = 0.0025 * ENTRY_COST.
STRESS_REORG_FEE = 50 USD flat.
STRESS_NET_CEILING = GROSS_CASH_PAYOUT - ENTRY_COST - STRESS_ENTRY_FRICTION - STRESS_REORG_FEE.

Taxes, settlement delay, opportunity cost, corporate-action rejection, broker aggregation and directional mark-to-market before the fixing are not modeled. Their omission makes the ceiling optimistic.

## Decision rule

Stage A waits until the document-defined CASH_BASIS is publicly observable; it does not use a later realized brokerage credit.

- KILL_CASE if CENTRAL_NET_CEILING <= 0.
- PARK_ECONOMICS if CENTRAL_NET_CEILING > 0 but STRESS_NET_CEILING <= 0.
- ADVANCE_IMPLEMENTATION_CHECK only if CENTRAL_NET_CEILING > 0 AND STRESS_NET_CEILING > 0.

No Stage-A outcome can PROMOTE the family.

## Implementation check

Run only after ADVANCE_IMPLEMENTATION_CHECK. Require public primary/official broker or transfer-agent documentation sufficient to determine whether a normal beneficial owner at a nominee broker receives this cash-in-lieu treatment rather than broker-level aggregation/rounding.

- KILL_CASE if the documented nominee/broker mechanics eliminate the modeled fractional entitlement for a normal beneficial owner or impose a mandatory known fee that makes the stress ceiling nonpositive.
- PARK_DATA if retail beneficial-owner treatment cannot be established without account-specific/live interaction.
- SURVIVES_PROSPECTIVE_CASE only if the issuer-level stress ceiling is positive and documented nominee mechanics remain compatible with the modeled entitlement.

A surviving case is not validated alpha or executable PnL.

## Family evidence threshold

Do not tune ratio bounds, quantity, entry session, fee assumptions, or formula class after outcomes. Consider family-level escalation only after >= 5 prospective qualifying cases under this exact protocol, in a separately predeclared review. Historical L0 examples do not count.

## Single adverse check

The only economic adverse check is the frozen STRESS_NET_CEILING (25 bps entry friction + 50 USD reorganization fee). No nearby fee/quantity/window search.

## Inference rights

TEST_CAN_KILL = one prospective reverse-split implementation case.
TEST_CAN_SUPPORT = one case has a positive predeclared stress ceiling and compatible documented beneficial-owner mechanics.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, BROKER_ELIGIBILITY_IN_GENERAL, TAX_TREATMENT, OR SCALABLE_CAPACITY.

REAL_CAPITAL_AUTHORIZED and LIVE_TRADING_AUTHORIZED remain FALSE regardless of result.
