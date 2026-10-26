# Discovery V4.2 — US issuer odd-lot priority prospective L1 v1

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-12T20:00:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Why this exists

This declaration converts the already-qualified issuer-tender odd-lot mechanism into a clean prospective test. The historical Anebulo example is calibration only because public completion/result snippets became exposed during documentary source resolution on 2026-10-12. It MUST NOT be counted as fresh economic evidence, an untouched sample, or confirmation of profitability.

## Mechanism

MECHANISM = In a partial issuer self-tender, an explicit odd-lot preference can give a beneficial owner of fewer than 100 shares priority ahead of the proration applied to larger holders. A small actor may therefore receive materially better allocation than scalable capital.
WHO_PAYS = The issuer repurchase budget and, economically, larger tendering holders who are prorated while qualifying odd lots are prioritized.
WHY_PERSIST = Capacity is intrinsically tiny per beneficial owner; aggregation rules, broker deadlines/fees, taxes, cancellation conditions and event irregularity make the trade operationally annoying and hard to scale.
MECHANISM_CLUSTER = issuer-corporate-action-allocation

This is not insider information, direction forecasting, daily ETF reversal, Form-4 alpha, or an account-multiplication scheme. Aggregate beneficial ownership across accounts is respected.

## Prospective universe — frozen before event access

Only events whose EDGAR `accepted` timestamp is STRICTLY AFTER `PROSPECTIVE_T0` are eligible. Select the FIRST chronologically qualifying event. If two have the same accepted timestamp, select the smaller issuer CIK. Do not skip an event because its spread looks unattractive.

A qualifying event must satisfy ALL of the following using the commencement filing and exhibits available at the public timestamp:

1. Form SC TO-I / issuer tender under Rule 13e-4; not a third-party Rule 14d tender.
2. Exchange-listed operating-company common stock on Nasdaq or NYSE at commencement; exclude closed-end funds, ETFs, preferreds, warrants and exchange offers.
3. Fixed cash purchase price stated at commencement. Exclude Dutch auctions/ranges for v1.
4. Explicit odd-lot priority BEFORE general proration for a holder beneficially owning in aggregate fewer than 100 shares and tendering all qualifying shares.
5. Offer is still open after the public commencement timestamp and no result/completion filing has occurred when the event is claimed.
6. A public daily OHLC route is documentably available before any price payload is read. Nasdaq's public Historical Data surface is an acceptable route if the selected symbol is actually retrievable; otherwise PARK_DATA rather than substitute a different event after seeing prices.

The historical Anebulo case and all issuer names exposed during the 2026-10-12 L0 search are ineligible for this prospective sample even if later documents are found.

## Event clock and entry — frozen

EVENT_TIME = SEC EDGAR `accepted` timestamp of the qualifying commencement SC TO-I.
ENTRY_SESSION = first regular Nasdaq/NYSE trading session whose official open occurs strictly after EVENT_TIME.
ENTRY_PRICE = raw regular-session OPEN for the selected common stock on ENTRY_SESSION from the prequalified public daily route.
Q = 99 shares, representing a hypothetical investor starting from zero beneficial holdings and remaining below 100 shares in aggregate. No multi-account multiplication.
OFFER_PRICE = fixed cash price stated in the commencement offer.

No intraday optimization, limit-price reconstruction, alternate entry window, close-price substitution or event skipping is allowed after the event is claimed.

## Stage A — immediate economic ceiling

This is deliberately an upper-bound feasibility screen, not executable P&L.

GROSS_DOLLAR_CEILING = Q * (OFFER_PRICE - ENTRY_PRICE)
CENTRAL_ENTRY_FRICTION = 0.0010 * Q * ENTRY_PRICE
CENTRAL_TENDER_FEE = 0 USD (optimistic ceiling only; NOT a broker-fee claim)
CENTRAL_CEILING = GROSS_DOLLAR_CEILING - CENTRAL_ENTRY_FRICTION

STRESS_ENTRY_FRICTION = 0.0025 * Q * ENTRY_PRICE
STRESS_TENDER_FEE = 50 USD flat heuristic stress charge
STRESS_CEILING = GROSS_DOLLAR_CEILING - STRESS_ENTRY_FRICTION - STRESS_TENDER_FEE

Taxes, borrow, financing, cancellation loss, opportunity cost, settlement delay and rejection risk are NOT modeled in these ceilings. Their omission makes the screen optimistic.

### Stage-A decision

- `KILL_CASE` if CENTRAL_CEILING <= 0.
- `PARK_ECONOMICS` if CENTRAL_CEILING > 0 but STRESS_CEILING <= 0.
- `ADVANCE_TO_COMPLETION_CHECK` only if both CENTRAL_CEILING > 0 and STRESS_CEILING > 0.

No Stage-A result can PROMOTE the family or validate alpha.

## Stage B — completion/acceptance check

Run only for a case that reaches `ADVANCE_TO_COMPLETION_CHECK`, and only after a public result/final amendment exists.

Use the issuer's SEC result filing / final SC TO-I/A as the primary source. Record whether qualifying odd lots were accepted in full, partially, or not determinable. Do not infer acceptance from general proration language.

- `KILL_CASE` if the filing shows qualifying odd lots were not accepted in full or the offer was terminated/cancelled.
- `PARK_DATA` if odd-lot acceptance cannot be determined from primary public documents.
- `SURVIVES_PROSPECTIVE_CASE` only if the primary filing shows qualifying odd lots accepted in full AND Stage-A STRESS_CEILING > 0.

A surviving single case is still not a family-level edge claim.

## Family evidence threshold

Collect prospective cases without changing this protocol. Do not tune entry, quantity, costs, issuer type or spread hurdle after a result.

Family-level escalation may be considered only after at least 5 qualifying prospective cases. At that point a new, separately predeclared review may ask whether at least 4/5 cases survived Stage B and whether median STRESS_CEILING was positive. Until then: no alpha, Sharpe, live-readiness or capital-authority claim.

## Adequacy / blockers

PARK_DATA before reading price payload if any of the following is unresolved: commencement identity, accepted timestamp, fixed offer price, explicit odd-lot priority, listing status, first post-event regular session, or documented historical-price route. Do not replace the selected event with a more attractive one after a blocker is discovered.

## Single adverse check

The only fixed economic adverse check in v1 is the STRESS_CEILING above (25 bps entry friction + 50 USD flat fee). No nearby fee, quantity, price-window or share-count search is allowed.

## Inference rights

TEST_CAN_KILL = one prospective implementation case.
TEST_CAN_SUPPORT = one case survives a predeclared optimistic+stress screen and later documented odd-lot acceptance.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, REPEATABILITY, CAPACITY_BEYOND_99_SHARES, BROKER_ELIGIBILITY, TAX_TREATMENT, OR MULTI_ACCOUNT_SCALING.

REAL_CAPITAL_AUTHORIZED and LIVE_TRADING_AUTHORIZED remain FALSE regardless of result.
