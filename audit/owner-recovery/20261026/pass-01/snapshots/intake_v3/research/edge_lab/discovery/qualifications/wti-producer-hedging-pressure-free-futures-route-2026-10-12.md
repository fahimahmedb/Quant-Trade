# WTI producer hedging pressure — zero-cost futures route follow-up

DECISION = PARK_DATA
LEVEL = L0_DATA_QUALIFICATION
FAMILY = wti-producer-hedging-pressure
ECONOMIC_OUTCOME_ACCESSED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD = 0

## Question

Can a distinct, complete-enough, zero-paid-cost WTI futures settlement/calendar route support a fixed futures holding/roll return instead of the invalid spot-only proxy?

## What was established

1. CME Group's Daily Settlements documentation states that official daily settlements are the values used to mark futures positions to market and that the Daily Settlement report covers eligible contracts.
2. CME's WTI contract specification identifies CL, 1,000 barrels, and the expiration rule: trading in the current delivery month ceases on the third business day before the 25th calendar day of the month preceding delivery, with the stated holiday adjustment.
3. CME's WTI daily-settlement procedure documents how the first six contract months are settled, including the 14:28–14:30 ET settlement window for the front months and spread-implied procedures farther out.
4. CME's 2023/2024 market-data notices state that after the FTP retirement, Daily Bulletin files remain available on the Daily Bulletin web page and daily Settlement Files are available through CME DataMine at midnight CT free of charge. The notice explicitly distinguishes the midnight Settlement File as non-fee-liable from earlier End-of-Day files that are fee-liable.
5. The Daily Bulletin page links Historical Daily Bulletin to the CME DataMine catalog. The public catalog route is visible, but this runtime did not establish an unauthenticated historical file download path or a machine-stable no-account API for a multi-year CL series.

## Decision

The economic mechanism is NOT rejected. The official futures route is economically appropriate and the settlement files are described by CME as free of charge, but `CHEAP_DATA_NOW` is not yet satisfied for this runtime because historical retrieval itself is unproven and may require DataMine account/session handling.

Therefore the family remains `PARK_DATA`. Do not substitute EIA spot, ETF oil proxies, or a stitched third-party continuous series after this decision. Do not spend more discovery time on CME access unless a genuinely new zero-cost retrieval fact appears.

## Why this closes the bounded follow-up

The prior handoff allowed <=15 minutes / <=3 primary metadata requests, no retries and no price payloads. The metadata question is now answered sufficiently for routing: the correct official data product exists and is non-fee-liable at midnight, but current-environment retrieval is not proven. A further account/authentication integration effort would be infrastructure work rather than cheap economic learning.

## Primary references observed

- CME Group — Daily Settlements.
- CME Group — About Settlements.
- CME Group — Light Sweet Crude Oil (WTI) Futures contract specifications / fact card.
- CME Group — NYMEX WTI Crude Oil daily settlement procedure.
- CME Globex Notice 2023-11-13 and 2024-02-26 — Settlement File / Daily Bulletin migration; midnight Settlement Files marked non-fee-liable.
- CME Group — Daily Bulletin / Historical Daily Bulletin link.

No settlement value, curve shape, return, COT row, P&L, hit rate or threshold outcome was read or computed in this follow-up.

## Next

Move research capacity to a causally distinct mechanism with `CHEAP_DATA_NOW` rather than re-probing WTI. WTI may be revisited only if historical CL settlement retrieval becomes directly usable at zero paid cost without source substitution.
