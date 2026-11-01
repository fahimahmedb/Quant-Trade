# US SPAC trust-redemption floor — bounded L0 qualification

DECISION = L1_NOW
LEVEL = L0
FAMILY = us-spac-redemption-floor
ECONOMIC_OUTCOME_ACCESSED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Mechanism

MECHANISM = Public SPAC shares can carry a contractual right, under the charter/proxy terms for a qualifying meeting, to be redeemed for a pro-rata share of the trust account if the holder satisfies the stated tender/DWAC deadline. When a redeemable share trades below the documented trust redemption amount and there is enough operational time to buy and validly tender it, the trust account creates a contractual cash floor distinct from directional equity forecasting.
WHO_PAYS = The SPAC trust account / sponsor-funded trust mechanics, economically transferred to redeeming public shareholders under the charter and meeting terms.
WHY_EDGE_CAN_EXIST = Residual SPACs can become very small and illiquid after prior redemptions; redemption procedures are operationally annoying, broker deadlines can be earlier than the legal deadline, settlement timing matters, and capital can be tied up for a modest absolute spread. These frictions can matter more to scalable capital than to a small account.
WHY_NOT_ARBITRAGED = This is a well-known mechanism and may usually be efficiently priced. The practical edge can disappear through bid/ask spread, inability to settle before the redemption cutoff, broker fees, redemption withdrawal/consummation conditions, trust-tax leakage, creditor risk, or a market price already above trust value. L1 must kill it cheaply when the net spread is not there.
MECHANISM_CLUSTER = contractual-redemption-arbitrage

This is causally distinct from issuer odd-lot tenders and reverse-split fractional settlement: the payoff comes from a contractual trust-account redemption right, not proration priority or fractional-share treatment.

## Current primary-source evidence — documentary only

Public SEC proxy statements in 2026 explicitly state that public shareholders may redeem for a pro-rata share of the trust account, commonly require delivery/tender of shares to the transfer agent roughly two business days before the meeting, and in some filings state that a shareholder may redeem regardless of whether it was the record-date holder. Other filings show that redemption can depend on the relevant proposal/business combination being approved or consummated and that trust value can change with taxes/claims.

Examples observed during this L0 search include 2026 proxy filings with stated illustrative trust values around $10.48, $10.60, $10.716, $10.82, $12.91 and $13.19 per public share. These examples are DOCUMENTARY EXPOSURE ONLY. No corresponding market entry price, spread, P&L, return, hit rate or selected winning case was read or computed. These exposed issuers are not an untouched confirmation sample.

## Cheap data now

- Contract/right/deadline/trust amount: SEC DEFM14A/DEF 14A/10-K/8-K and charter/trust-agreement disclosures with EDGAR accepted timestamps.
- Meeting and redemption cutoff: primary proxy materials.
- Listing/symbol and daily OHLC: public market-data route documented before payload access in any L1.
- Completion/result: later SEC filing, only after a case passes the predeclared entry-spread screen.

No paid data is required for a first discriminating test.

## Main implementation risks

- Broker internal redemption cutoff may be earlier than the issuer/transfer-agent deadline.
- Shares bought after the record date can sometimes redeem, but this must be explicitly documented for the selected case; never assume it generally.
- T+1 settlement and DWAC processing can make a seemingly open window operationally impossible.
- Some redemptions are conditional on proposal approval or business-combination consummation; a failed transaction can delay or change the payoff path.
- Trust amount may decline through taxes or permitted withdrawals; creditor claims can also matter.
- Units/warrants generally do not inherit the same redemption right as separated public shares.
- Very low float can produce large bid/ask spread and poor fills even when a headline redemption spread looks positive.

## Minimum discriminating test — design target, NOT YET EXECUTED

Use the FIRST prospective post-T0 SPAC meeting filing that satisfies all of the following before any market-price payload is read:

1. Nasdaq/NYSE/NYSE American listed public common share with an explicit redemption right for the relevant meeting.
2. Proxy/charter terms state a determinable redemption amount or a formula tied to the trust account.
3. Filing explicitly permits redemption by a purchaser who was not necessarily the meeting record-date holder OR otherwise gives a post-announcement buyer a documented path to redemption.
4. A valid buy-settle-tender window exists after the SEC public timestamp, allowing at least one regular market session plus settlement before the stated legal/transfer-agent redemption deadline.
5. Redemption is not already closed and no completion/result filing is exposed at claim time.
6. One public daily OHLC route is documented before price payload access.

Before reading ENTRY_PRICE, freeze the exact event, entry session, trust-value source, legal redemption deadline, one conservative broker-buffer deadline, central/stress frictions, and the condition under which redemption cash is payable.

First-stage economics should be a simple contractual ceiling:
`NET_REDEMPTION_SPREAD = REDEMPTION_VALUE - ENTRY_PRICE - entry friction - fixed operational fee - carry/time cost proxy`.

A nonpositive central ceiling KILLs the case. A positive central but nonpositive stress ceiling PARKs economics. Only a positive stress ceiling may advance to a later completion/operational check. No single case can validate alpha or the family.

## L0 verdict

L1_NOW because the mechanism is causal, contract-based, public-document driven, cheaply falsifiable, and economically different from current families. The mechanism is known, so the research question is not whether redemption rights exist; it is whether a strictly prospective small-account implementation can still produce a positive net contractual spread after real timing and broker frictions. Do not historical-scan for a winner.
