# US ETF liquidation NAV convergence — bounded L0 qualification

DECISION = L1_NOW
LEVEL = L0
FAMILY = us-etf-liquidation-nav-convergence
MECHANISM_CLUSTER = fund-liquidation-forced-cash
ECONOMIC_OUTCOME_ACCESSED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD = 0

## Mechanism

MECHANISM = When a US exchange-listed ETF is formally scheduled for closure, the fund stops or restricts creations/redemptions, ceases exchange trading on a stated date, liquidates its portfolio and ultimately pays remaining shareholders a pro-rata cash distribution tied to residual NAV after liabilities and liquidation costs. Near the final tradable session, authorized-participant arbitrage and ordinary secondary-market liquidity may weaken while the terminal payoff becomes increasingly cash-like.

WHO_PAYS = Sellers requiring immediate liquidity before delisting and, if a discount exists, the fund's terminal liquidation process closes the gap by distributing residual NAV to holders who remain through liquidation.

WHY_EDGE_CAN_EXIST = Capacity can be tiny because closing ETFs are often small and illiquid; holding through delisting creates settlement/tax/operational nuisance; the final distribution is delayed and not perfectly known; liquidation costs and residual asset moves create basis risk. These frictions can make small discounts irrelevant to institutional capital while still measurable for a very small actor.

WHY_NOT_ARBITRAGED = No profitability claim. AP activity may keep the market price close to NAV until the last session, liquidation costs may absorb the discount, the final NAV can fall after the last trade, and broker restrictions/taxes can dominate. L1 must be able to kill the case cheaply.

This is causally distinct from issuer odd-lot tenders, reverse-split fractional treatment, SPAC redemption, daily ETF reversal and rights offerings. The payoff source is a terminating fund's pro-rata residual NAV, not proration priority or a fixed issuer purchase price.

## Public primary evidence observed

SEC Rule 497 liquidation supplements in 2026 repeatedly specify the same mechanical structure:

- Theme ETF Trust filings state that the funds cease trading on a fixed closing date, liquidate portfolios over a stated period, and distribute cash pro rata to remaining shareholders; the final NAV reflects closing costs.
- CrossingBridge Ultra-Short Duration ETF filing states Nasdaq trading ceases on the closing date and the fund liquidates as a series of the trust on the stated liquidation date.
- Schwab Ariel Opportunities ETF filing states a board-approved liquidation date and a prior NYSE Arca last trading date.
- Several other 2026 Rule 497 supplements state that shareholders remaining after the last trading date receive cash equal to their proportionate interest / NAV, subject to expenses, taxes and withholdings.

These documents establish the mechanism and event clock. They are not economic outcomes and no historical market price, NAV discount, liquidating distribution or realized return was read or computed.

## CHEAP_DATA_NOW

- Event discovery / filing timestamp: SEC EDGAR Rule 497 / 497K filings and primary fund supplements.
- Last trading date / liquidation date: primary Rule 497 supplement.
- Exchange close: public daily OHLC route must be documented for the selected symbol before any payload access.
- Fund NAV: issuer/fund sponsor's public daily NAV page or SEC N-PORT/NAV disclosure only if available under a frozen route; no substitution after event selection.
- Final liquidating distribution: later primary fund filing / sponsor notice if Stage B is reached.

No paid source is required for a prospective first-case test, but the selected case must prove both market-close and NAV routes before any economic calculation.

## Historical exposure receipt

The L0 search exposed several 2026 liquidation filings and fund names, including Theme ETF Trust funds, CrossingBridge Ultra-Short Duration ETF, Schwab Ariel Opportunities ETF, Deepwater Beachfront Small Cap ETF, Defiance Daily Target 2X Long ZETA ETF, several Direxion funds, and Innovator Uncapped Bitcoin 20 Floor ETF. These are CALIBRATION_ONLY and must never be used as fresh prospective evidence under v1.

No market-price/NAV payload or final distribution was read for these examples.

## Minimum discriminating test target

Use the FIRST chronologically qualifying fresh US ETF liquidation filing accepted after a future predeclared T0, excluding all exposed names above.

Before reading any price or NAV payload, freeze:
- exact selected fund and SEC accepted timestamp;
- last regular exchange trading session;
- liquidation date;
- entry = official regular-session close on the final tradable day;
- quantity = 1 share for normalized economics plus a separate fixed 100-share dollar example only if the share price makes that feasible; no quantity optimization;
- NAV reference = issuer-published NAV for the same final tradable date, published no earlier than the market close and with a documented timestamp/route;
- central round-trip/exit-equivalent friction = 20 bps of entry notional;
- stress friction = 50 bps + $10 flat operational cost;
- holding horizon = last trading close to liquidating distribution;
- one adverse check = final cash distribution after all fund expenses must still exceed entry plus stress friction.

Stage A should kill the case if the observed close is not at a positive discount to same-date published NAV after central friction. A positive Stage A only allows waiting for the actual distribution; it cannot promote the family.

## L0 verdict

L1_NOW. The mechanism is contractual, causal, small-capacity and prospectively observable from primary public documents. Historical examples are contaminated by this qualification and are excluded. The next action is a clean prospective predeclaration before any future event selection or price/NAV read.
