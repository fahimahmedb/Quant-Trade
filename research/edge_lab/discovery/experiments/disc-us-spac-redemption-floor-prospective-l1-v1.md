# Discovery V4.2 — US SPAC trust-redemption floor prospective L1 v1

STATUS = PREDECLARED_BEFORE_PROSPECTIVE_EVENT
LABEL = EXPLORATORY
PROSPECTIVE_T0 = 2026-10-12T21:00:00Z
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Purpose

Test prospectively whether a publicly documented SPAC redemption right can still provide a positive small-account contractual spread after a strictly post-filing market entry, realistic timing constraints, and frozen frictions. Historical SPAC examples seen during L0 are documentary calibration only and do not count as fresh evidence.

## Prospective universe — frozen

Only a meeting/proxy event whose first SEC filing containing the operative redemption right and deadline has EDGAR `accepted` STRICTLY AFTER PROSPECTIVE_T0 is eligible. Select the FIRST chronologically qualifying event; same accepted timestamp => smaller issuer CIK. Never skip an unattractive event.

A qualifying event must satisfy ALL before any market-price payload is read:

1. Nasdaq/NYSE/NYSE American listed SPAC public common share (not unit, warrant, right, founder share or post-combination operating-company share).
2. Primary SEC proxy/charter materials explicitly give public shareholders a cash redemption right tied to the relevant meeting/business-combination/extension proposal.
3. Filing gives either a stated estimated redemption value per public share or an objectively reconstructible trust-account formula.
4. Filing explicitly permits redemption by a public shareholder regardless of record-date ownership OR otherwise clearly establishes that a post-announcement buyer can validly redeem. If this is not explicit, PARK_DATA before price access.
5. A post-announcement buy-settle-tender window exists: at least one regular market open strictly after EVENT_TIME, then sufficient time for T+1 settlement, then at least one full US business day before the issuer/transfer-agent legal redemption cutoff. If not, event is INELIGIBLE before prices.
6. Redemption is still open and no result/completion filing has been intentionally read at claim time.
7. One public daily OHLC route is documented before any price payload. If the selected symbol is unavailable there, PARK_DATA; do not substitute a later event.
8. The relevant public share is separable/redeemable under the filing terms; units requiring separation are excluded unless the common share itself is already separately listed and purchasable.

All issuers/examples exposed during the 2026-10-12 L0 search are excluded from this prospective sample.

## Event clock, entry, and redemption value

EVENT_TIME = EDGAR `accepted` timestamp of the first qualifying proxy/meeting filing that makes redemption right + deadline + holder eligibility explicit.
ENTRY_SESSION = first regular exchange session whose official open is strictly after EVENT_TIME and still satisfies the buy-settle-tender window.
ENTRY_PRICE = raw regular-session OPEN on ENTRY_SESSION from the prequalified public route.
Q = 10 public shares. No quantity search and no leverage.

REDEMPTION_VALUE = the per-share cash amount stated in the qualifying filing if fixed/estimated from a dated trust balance; if the filing instead specifies only a trust formula, use the latest public trust value available at EVENT_TIME and label it ESTIMATED. Do not use a later final redemption amount for Stage A.

## Frozen costs and time buffer

CENTRAL_ENTRY_FRICTION = 0.0010 * Q * ENTRY_PRICE.
CENTRAL_OPERATIONAL_FEE = 0 USD as an optimistic ceiling only, not a broker-fee claim.
CENTRAL_CEILING = Q * (REDEMPTION_VALUE - ENTRY_PRICE) - CENTRAL_ENTRY_FRICTION.

STRESS_ENTRY_FRICTION = 0.0025 * Q * ENTRY_PRICE.
STRESS_OPERATIONAL_FEE = 50 USD flat.
STRESS_CEILING = Q * (REDEMPTION_VALUE - ENTRY_PRICE) - STRESS_ENTRY_FRICTION - STRESS_OPERATIONAL_FEE.

BROKER_BUFFER = one full US business day earlier than the legal/transfer-agent redemption cutoff. The modeled holder must be settled and operationally able to instruct redemption by BROKER_BUFFER. If not, KILL_IMPLEMENTATION before any economic promotion.

Carry/opportunity cost, taxes, trust-value drift, creditor claims, bid/ask spread beyond the frozen friction, delayed consummation and failed proposals are not modeled in Stage A; this makes the ceiling optimistic.

## Stage A — contractual spread screen

- KILL_CASE if CENTRAL_CEILING <= 0.
- PARK_ECONOMICS if CENTRAL_CEILING > 0 but STRESS_CEILING <= 0.
- ADVANCE_TO_OUTCOME_CHECK only if CENTRAL_CEILING > 0 AND STRESS_CEILING > 0 AND the BROKER_BUFFER timing test passes.

No Stage-A result can promote the family or validate alpha.

## Stage B — public completion/redemption check

Run only after ADVANCE_TO_OUTCOME_CHECK and only when a later public SEC filing establishes the meeting/business-combination outcome and actual redemption treatment.

- KILL_CASE if the relevant proposal/business combination fails in a way that voids the modeled redemption path, or if the filing shows the selected public-share redemption right was not payable under the frozen conditions.
- PARK_DATA if actual treatment cannot be determined from primary public filings.
- SURVIVES_PROSPECTIVE_CASE only if the public filing confirms the redemption path remained payable and the Stage-A STRESS_CEILING was positive.

Do not substitute the final actual redemption amount back into Stage A. Record any difference between estimated and actual redemption value as implementation error, not a retuned entry signal.

## Family evidence threshold

Collect cases prospectively without changing Q, timing buffer, entry session or costs. Consider family-level escalation only after >=5 qualifying prospective cases in a separately predeclared review. At least 4/5 must survive Stage B and the median frozen STRESS_CEILING must be positive before any stronger claim is even considered.

## Single adverse check

The only frozen economic adverse check is STRESS_CEILING: 25 bps entry friction + 50 USD flat operational fee, plus the one-business-day broker buffer. No nearby fee, Q, deadline or entry-window search.

## Inference rights

TEST_CAN_KILL = one prospective SPAC redemption implementation case.
TEST_CAN_SUPPORT = one case has positive frozen stress spread and later public confirmation that the redemption path remained payable.
TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, LIVE_READY, EXECUTABLE_PNL, GENERAL_BROKER_SUPPORT, GUARANTEED_TRUST_VALUE, TAX TREATMENT, OR SCALABLE_CAPACITY.

REAL_CAPITAL_AUTHORIZED and LIVE_TRADING_AUTHORIZED remain FALSE regardless of result.
