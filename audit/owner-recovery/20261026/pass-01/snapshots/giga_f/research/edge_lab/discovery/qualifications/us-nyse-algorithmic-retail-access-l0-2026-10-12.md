# NYSE retail price improvement — autonomous-origin access falsifier

Date: 2026-10-12. Level: L0, documents only.
Decision: **KILL_EXPRESSION**, limited to an algorithm originating its own order
instructions and claiming NYSE Retail Taker/Attested eligibility merely because
the account belongs to a retail individual. No return test was conducted.

## Admission check before this research action

Fresh initial branch HEAD: `5e8c61b8a01bc7f2ea3c5872487613e00da72a03`.
CONTROL was unpaused, with capital/live false. The five Owner-authorized
protocols were checked: odd-lot A uses T0 20:00Z; cash-in-lieu B v2, round-up C
v2, SPAC D and ETF-liquidation E use T0 21:00Z, all on October 12.
B/C v1 clocks remain INVALID. Only their immutable bodies incorporated by v2
were read, at `ca23532498b77d5eb3310f9c080909a2a239a221` and
`7f5f6a1199658bce0983ca5d71faebf06ab184c9`, respectively; no v1 admission.

Reused `prospective-feed-check-2026-10-12T2106Z.json`: six bounded primary feeds
had no post-T0 candidates, and its [official SEC calendar](https://www.sec.gov/submit-filings/filer-support-resources/edgar-calendar)
receipt establishes that EDGAR does not accept filings on October 12's holiday.
Calendar response hash: `031cad3dadc356e0fc0d6d8e8872f4e8e4ce39b0c92bf403f7761f887ffcaa8c`.
No redundant holiday poll, issuer exhibit, price, NAV or distribution payload
was requested. No event was selected or claimed. Next admission check is after
EDGAR reopens October 13 (existing state gate 10:00Z), retaining each protocol's
own T0 and all historical exclusions. Across A–E, earliest eligible EDGAR
accepted time wins, then smaller CIK; E's own ticker tie rule remains intact.
Bounded-feed completeness and `updated` versus exact `accepted` remain distinct.

Discovery had no RUNNING queue item. The five saved claim-file identities each
had a durable result: three PARK_DATA and two KILL_EXPRESSION; only disposition
metadata was inspected. Their calculations were not reopened. A newly appearing
unresolved claim must still block any second economic look.

## Causal question and decisive evidence

The candidate is segmented liquidity: suppliers may offer better prices to
less adversely selected retail flow. They pay the price concession; eligibility
and broker-controlled routing could keep it unavailable to scalable informed
flow. This is an execution-cost hypothesis, not a directional return forecast.

1. [NYSE current equities overview](https://www.nyse.com/trade/equities),
   sections “NYSE Retail Liquidity Program” and “Retail Taker Order,” observed
   during 21:23–21:28Z on October 12: the order must originate from a natural
   person and reach the exchange through an RMO. The page states:
   “The order cannot originate from a trading algorithm or any other computer methodology.”
   It gives the same origin restriction for Retail Attested Orders, which
   cannot interact with RPI orders. The published RPI indicator identifies
   interest side, not size. An indicator alone cannot establish a fill or
   incremental realized savings. No current-page revision identifier is given.
2. [NYSE membership documentation](https://www.nyse.com/trade/membership?quicktabs_293=3),
   same observation window: exchange membership is for qualifying registered
   broker-dealers, not individual investors. Retail participation uses RMO
   agreements. This corroborates that a public webpage is not a retail routing
   entitlement. No application, broker inquiry, account or order was made.

This falsifies the specified autonomous-origin access assumption before paying
for market data or a backtest. It does **not** say computerized transmission of
a genuinely human-originated order is universally prohibited, that every venue
has identical rules, or that qualifying human-originated retail flow receives
no benefit. No workaround, false retail marking or exception is proposed.

## Relation to the concurrent EDGX result

During this pass another branch advance saved
`us-retail-liquidity-priority-l0-2026-10-12.json`: EDGX displayed queue priority
is PARK_DATA because attributed executions/access were not qualified. Preserve
that decision unchanged. The present evidence concerns NYSE price-improving
taker access, a different implementation, and adds an explicit origin-condition
falsifier. It does not reclassify the EDGX mechanism or reopen its data gate.
The family-wide retail-benefit claim remains untested.

## Exposure and cost

Two primary-targeted searches and three document opens in two browser calls.
NYSE program/membership pages are decisive. Nasdaq BX FAQ search excerpts were
visible, but the PDF text extraction was unusable and its current applicability
was not established; it is not used to assert a 2026 Nasdaq rule. Historical
regulatory/program-success snippets and NYSE marketing/fee material were also
exposed. No fill, quote, NAV, payoff series or selected trade result was read.
This is documentary/selection exposure, not pristine confirmation. No retries,
economic execution, new census or WTI/CME/DataMine probe. Paid spend 0;
tokens, global bill and browser origin bytes NOT MEASURED.

## Nine-field decision

- RESULT: KILL_EXPRESSION for autonomous-origin NYSE Retail Taker/Attested
  eligibility claimed solely from a retail account; documentary falsification.
- EFFECT_SIZE: Return effect not estimated; necessary access premise fails.
- UNCERTAINTY: Human-originated broker routing and its incremental savings are
  unqualified; no generalization to other venues.
- POWER_LIMITATION: No statistical sample, executions, or control orders.
- ECONOMIC_SIGNIFICANCE: Prevents a backtest from assigning unavailable retail
  treatment to the proposed algorithm; no dollar profit or loss estimated.
- FAILED_CRITERIA: Required non-algorithmic order origin and qualified RMO path.
- LESSON: A retail-owned account does not by itself make an algorithm's order
  eligible for every retail-only exchange program.
- FAMILY_STATUS: Only the specified NYSE access expression is closed. Existing
  EDGX PARK_DATA and all other family histories remain unchanged; no L1 opened.
- NEXT_DECISION: Keep the newest already-selected Discovery question rather
  than overwrite concurrent research. Original A–E prospective admission comes
  first after the saved SEC opening gate; absent a qualifying event, perform
  that next documentary question. No additional research action in this pass.

Reopening this exact access premise requires genuinely changed primary
eligibility evidence; a new name or account label is insufficient.

Publication parent: `4ca424b0fc62a6ba194ebbb3b3eeb899e464916c`; fresh CONTROL remains unpaused, capital/live false.
The concurrent next question is preserved verbatim in STATE: Can a fixed price-blind small basket from the official preliminary deletion list support one cheap rebalance sell-pressure/rebound test?
