# US reverse-split cash-in-lieu — bounded L0 qualification

DECISION = L1_NOW
LEVEL = L0
FAMILY = us-reverse-split-cash-in-lieu
ECONOMIC_OUTCOME_ACCESSED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Mechanism

MECHANISM = Some reverse stock splits do not issue fractional post-split shares. Instead, holders who would otherwise receive a fraction are paid cash under a formula fixed in the corporate-action documents. A holder with a deliberately small pre-split position can therefore face a payout rule that is discrete at the account/record-holder level rather than proportional to scalable institutional size.
WHO_PAYS = The issuer/corporate-action settlement process.
WHY_EDGE_CAN_EXIST = Capacity is tiny, terms are issuer-specific, record-vs-beneficial-holder treatment varies, brokers may aggregate positions or charge reorganization fees, and the event is operationally annoying. Those frictions can make the opportunity irrelevant to large capital while still economically material for a very small account.
WHY_NOT_ARBITRAGED = No claim yet. The mechanism may be fully neutralized by market pricing, broker aggregation, fees, tax, rounding, or record-date mechanics. L1 must be able to kill it cheaply.
MECHANISM_CLUSTER = corporate-action-fractional-settlement

This is causally distinct from issuer-tender odd-lot priority: the allocation rule comes from fractional-share treatment in a reverse split, not proration priority in a tender offer.

## Public primary evidence

1. SEC filing for a June 2026 Nasdaq reverse split (CIK 1527541) states that no fractional shares would be issued; holders otherwise entitled to a fraction would receive cash equal to that fraction times the Nasdaq closing price on June 17, 2026, adjusted for the split. Trading was to begin split-adjusted on June 18, 2026.
2. SEC filing for Power REIT (CIK 1532619) states a 1-for-10 reverse split effective June 2, 2026; fractional interests would receive cash equal to the applicable fraction times the June 2 NYSE American closing price, adjusted for the split.
3. A separate August 2026 SEC filing (CIK 1948864) explicitly used a different policy: fractional interests were rounded UP to a whole share and no cash was paid. This negative control confirms that the treatment must be read from each issuer's actual filing and cannot be inferred from the words “reverse split.”

No historical entry price, payout return, P&L, Sharpe, hit rate or optimization was computed in this L0.

## Cheap-data-now

- Event/terms: SEC 8-K, proxy and charter-amendment filings, with EDGAR accepted timestamps.
- Listing/trading session: issuer filing + exchange symbol.
- Daily open/close if later authorized by a frozen L1: public historical-price surface documented before payload access.

No paid data is required for the first discriminating test.

## Main leakage / implementation risks

- “Stockholder of record” may not map cleanly to a retail beneficial owner at a broker.
- Brokers may aggregate fractional entitlements across customers, round internally, or charge mandatory reorganization fees.
- Effective-time and entitlement rules may require holding before a cutoff that is earlier than the public trade window.
- Cash may be based on an already-known market price or an issuer/agent sale process, leaving no exploitable premium.
- Taxes, settlement timing and trading suspension/delisting risk can dominate a tiny position.
- Reverse-split names are often distressed/high-volatility securities; directional exposure before settlement can overwhelm the fractional payout.

## Minimum discriminating test — design target, NOT YET EXECUTED

Use the FIRST prospective event after a future predeclared T0 that satisfies all of:
- Nasdaq/NYSE/NYSE American listed common stock;
- public filing explicitly says cash-in-lieu of fractions rather than round-up/down without cash;
- exact split ratio, effective time, entitlement basis and cash formula are fixed in primary documents;
- broker/beneficial-owner treatment is documentable enough to know whether a normal retail holder can actually receive the issuer cash treatment;
- one public historical-price route is documented before payload access.

Before any price payload, freeze one small position implied by the split ratio, event clock, entry rule, central/stress fee assumptions, failure horizon and a single adverse broker-fee check. The first L1 should be an optimistic-ceiling test: if even the best document-supported cash formula cannot exceed entry cost plus frozen frictions, KILL the case immediately. A positive ceiling can only justify deeper broker/settlement validation, never promote the family by itself.

## L0 verdict

L1_NOW because the mechanism is causal, small-capacity, publicly documented and cheaply falsifiable. The next action should be a prospective predeclaration, not a historical return search. Do not choose a historical winner from the examples above.
