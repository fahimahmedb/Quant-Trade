# Discovery V4.2 — US reverse-split fractional round-up prospective L1 v1

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-12T20:00:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Purpose

Test whether a publicly announced reverse split that explicitly rounds a fractional post-split entitlement UP to one whole share can create a positive small-account economic ceiling after a strictly post-announcement entry, and whether that issuer-level entitlement plausibly survives nominee/broker mechanics.

Historical issuers exposed before T0 are calibration only and permanently excluded from the prospective sample.

## Prospective universe — frozen

Only events whose first public SEC filing containing the operative split and fractional-treatment terms has EDGAR `accepted` STRICTLY AFTER PROSPECTIVE_T0 are eligible. Select the FIRST chronologically qualifying event. Same timestamp => smaller issuer CIK. Never skip an unattractive event.

A qualifying event must satisfy ALL:

1. Nasdaq, NYSE, or NYSE American listed operating-company common stock.
2. Fixed reverse split ratio 1-for-R, R integer > 1, stated in primary documents.
3. Primary filing explicitly says a holder otherwise entitled to a fractional post-split share will be rounded UP to one whole post-split share. Cash-in-lieu, round-down and discretionary treatments are excluded from this expression.
4. Effective time and entitlement basis are explicit enough to determine whether a market purchase after EVENT_TIME can still participate.
5. At least one regular exchange-session open exists strictly after EVENT_TIME and strictly before the documented last entitlement time. Otherwise INELIGIBLE before any price access.
6. No minimum-holding, aggregation-across-all-beneficial-holdings, registered-holder-only, transfer-agent registration or other disclosed condition makes the modeled post-announcement beneficial-owner position facially ineligible. If ambiguous, PARK_DATA before price access.
7. One public daily OHLC route is documented before any price payload. If the selected symbol is unavailable on that route, PARK_DATA; do not switch events.
8. No post-effective result, broker allocation result, or later price payload has been intentionally read when the event is claimed.

## Event clock and fixed position

EVENT_TIME = EDGAR `accepted` timestamp of the first public filing/exhibit that makes ratio + effective time + round-up treatment reconstructible.
ENTRY_SESSION = first regular exchange session whose official open is strictly after EVENT_TIME and still before the entitlement cutoff.
ENTRY_PRICE = raw regular-session OPEN from the prequalified public route.

Q = 1 pre-split share. No quantity search.
STRICT_PRO_RATA_POST_SPLIT = 1 / R share.
MODELED_ISSUER_ENTITLEMENT = 1 whole post-split share under the explicit round-up language.

The hypothetical investor starts from zero beneficial holdings, uses one account only, no margin, no shorting, and never places a real order.

## Stage A — issuer-level optimistic ceiling

POST_SPLIT_REFERENCE_PRICE = first regular-session OPEN of the post-split security on/after the split-adjusted effective trading date, from the same prequalified public route.

THEORETICAL_ROUNDUP_VALUE = 1 * POST_SPLIT_REFERENCE_PRICE.
ENTRY_COST = 1 * ENTRY_PRICE.
CENTRAL_ENTRY_FRICTION = 0.0010 * ENTRY_COST.
CENTRAL_EXIT_FRICTION = 0.0010 * THEORETICAL_ROUNDUP_VALUE.
CENTRAL_NET_CEILING = THEORETICAL_ROUNDUP_VALUE - ENTRY_COST - CENTRAL_ENTRY_FRICTION - CENTRAL_EXIT_FRICTION.

STRESS_ENTRY_FRICTION = 0.0025 * ENTRY_COST.
STRESS_EXIT_FRICTION = 0.0025 * THEORETICAL_ROUNDUP_VALUE.
STRESS_REORG_FEE = 50 USD flat.
STRESS_NET_CEILING = THEORETICAL_ROUNDUP_VALUE - ENTRY_COST - STRESS_ENTRY_FRICTION - STRESS_EXIT_FRICTION - STRESS_REORG_FEE.

This is deliberately optimistic: it assumes the holder actually receives a whole post-split share and can value it at the first post-split regular-session open. It does not model tax, settlement delay, halt risk, price impact, account restrictions or allocation failure.

### Stage-A decision

- KILL_CASE if CENTRAL_NET_CEILING <= 0.
- PARK_ECONOMICS if CENTRAL_NET_CEILING > 0 but STRESS_NET_CEILING <= 0.
- ADVANCE_IMPLEMENTATION_CHECK only if CENTRAL_NET_CEILING > 0 AND STRESS_NET_CEILING > 0.

No Stage-A result can PROMOTE the family.

## Stage B — nominee/broker implementation gate

Run only after ADVANCE_IMPLEMENTATION_CHECK.

Require public issuer, transfer-agent, DTC, exchange, or official broker documentation sufficient to answer whether a normal beneficial owner holding Q=1 through a nominee broker receives the issuer's rounded whole-share treatment rather than broker-level aggregation/pro-rata allocation.

- KILL_CASE if documented nominee mechanics eliminate the modeled whole-share round-up or a mandatory known fee makes STRESS_NET_CEILING <= 0.
- PARK_DATA if beneficial-owner treatment cannot be established from public documentation without account-specific/live interaction.
- SURVIVES_PROSPECTIVE_CASE only if both the frozen stress ceiling is positive and documented nominee mechanics remain compatible with the modeled one-share round-up.

## Family threshold

This is a sibling expression of `us-reverse-split-cash-in-lieu`, not an independent mechanism count. Do not tune Q, ratio bounds, entry session, cost assumptions or implementation criteria after outcomes. Family-level escalation requires a separately predeclared review after at least 5 prospective round-up cases or a decisive implementation-level falsification, whichever occurs first.

## Single adverse check

Only the frozen STRESS_NET_CEILING is permitted: 25 bps entry friction + 25 bps exit friction + 50 USD flat reorganization fee. No nearby search.

## Inference rights

TEST_CAN_KILL = one prospective issuer-level/implementation case.
TEST_CAN_SUPPORT = one case exhibits a positive predeclared stress ceiling and public nominee mechanics compatible with a one-share round-up.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, GENERAL_BROKER_ELIGIBILITY, TAX_TREATMENT, OR SCALABLE_CAPACITY.

REAL_CAPITAL_AUTHORIZED and LIVE_TRADING_AUTHORIZED remain FALSE regardless of result.
