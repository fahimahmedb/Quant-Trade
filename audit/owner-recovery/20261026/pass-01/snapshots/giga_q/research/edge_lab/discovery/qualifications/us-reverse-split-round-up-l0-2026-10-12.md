# US reverse-split fractional round-up — bounded L0 qualification

DECISION = L1_NOW
LEVEL = L0
FAMILY = us-reverse-split-fractional-settlement
RELATION_TO_CASH_IN_LIEU = SAME_FAMILY_NEW_EXPRESSION
ECONOMIC_OUTCOME_ACCESSED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Mechanism

MECHANISM = Some reverse splits explicitly round a fractional post-split entitlement UP to one whole post-split share instead of paying cash-in-lieu. For a sufficiently small pre-split position, that creates a discrete corporate-action transfer: the holder can receive one post-split whole share even though the strict pro-rata entitlement is less than one share.
WHO_PAYS = issuer / corporate-action settlement process through the anti-fractional rounding rule.
WHY_EDGE_CAN_EXIST = the benefit, if actually passed through to a retail beneficial owner, is capped to roughly one post-split share per eligible holder/record position and is operationally awkward. That is tiny capacity and may be ignored by scalable capital.
WHY_NOT_ARBITRAGED = broker/DTC aggregation may completely eliminate the holder-level round-up; issuers may require aggregation across accounts or define the rule only for registered holders; fees, distressed-stock volatility, halts or post-split price collapse can dominate. No profitability claim is made.
MECHANISM_CLUSTER = corporate-action-fractional-settlement.

This is economically different from the cash-in-lieu expression because the hypothesized value comes from a discontinuous round-up, not from the level of a cash fixing price. It remains the same broad corporate-action family and must not be counted as an independent mechanism discovery.

## Existing public exposure

The prior cash-in-lieu L0 already exposed one August 2026 SEC filing (CIK 1948864) whose terms stated that fractional interests would be rounded UP to a whole share and no cash would be paid. That issuer/example is calibration-only and is permanently excluded from any fresh sample. No price or return for that issuer is used here.

## Cheap-data-now

- Primary event/terms: SEC 8-K, proxy, charter amendment and incorporated reverse-split exhibits with EDGAR accepted timestamps.
- Listing/effective time: issuer filing plus exchange/listing identifier.
- Price route for a later frozen L1: one public daily OHLC source documented before payload access.
- Implementation check: issuer/transfer-agent/broker public documentation when available.

No paid data is required for the first discriminating test.

## Main blockers

- Nominee brokers may aggregate customer positions at DTC/record-holder level and allocate post-split shares pro rata, destroying the apparent round-up.
- Terms may require aggregation of all beneficial holdings, registered ownership, or a specific cutoff that prevents a post-announcement purchase from qualifying.
- Reverse-split issuers are often distressed and highly volatile; exposure can overwhelm the discrete share benefit.
- Reorganization fees can dominate a one-share benefit.
- Round-up language sometimes exists to simplify issuer books rather than to promise a retail beneficial-owner windfall.

## Minimum discriminating test

Use the FIRST prospective post-T0 event whose public primary filing explicitly says fractional post-split interests are rounded UP to one whole share and whose entitlement timing still permits a strictly post-announcement market entry. Before reading any price payload, freeze:

- first qualifying event by EDGAR accepted timestamp;
- exact split ratio;
- first eligible post-announcement regular-session open;
- deterministic small pre-split quantity;
- central/stress entry friction;
- one flat reorganization-fee stress;
- issuer-level theoretical round-up benefit;
- a separate broker/nominee implementation gate.

The first economic test is an optimistic ceiling. If even issuer-level economics are nonpositive, KILL immediately. A positive issuer-level ceiling does not survive unless public implementation evidence is compatible with a normal beneficial owner receiving the rounded share.

## L0 verdict

L1_NOW. Expected information gain is high because one prospective event can decisively distinguish a real discrete transfer from a record-holder-only accounting rule. Do not historical-scan for winners; freeze T0 first and accept the first qualifying future case.
