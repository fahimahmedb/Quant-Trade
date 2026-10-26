# Discovery V4.2 — TYG optional-cash discounted issuance prospective L1 v1

STATUS = PREDECLARED_BEFORE_FIXING_OUTCOME
LABEL = EXPLORATORY_PROSPECTIVE_OOS_SINGLE_VEHICLE
PARENT = `../qualifications/us-cef-optional-cash-discount-l0-2026-10-15.json`
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
PAID_USD_AUTHORIZED = 0

## Prior exposure / contamination

TYG historical 2026 NAV/market/DRIP rows were visible during L0 route qualification. They are calibration contamination only and cannot support this result, choose thresholds, or be counted as prospective evidence. The future October 30 and November 30, 2026 rows were still `TBD` when this protocol was written; no future fixing NAV/market value for the target case has been intentionally read.

This protocol therefore tests one fixed future OOS implementation case, not a virgin-family discovery.

## Fixed target case

`ISSUER = Tortoise Energy Infrastructure Corp.`

`TICKER = TYG`

`TARGET_MONTHLY_INVESTMENT_DATE = 2026-10-30`

`OPTIONAL_CASH = 5000 USD`

The $5,000 amount is the ordinary monthly maximum stated by the Plan and is frozen before the target fixing. No waiver, larger cash amount, multiple accounts, household splitting, leverage or repeated same-month orders are permitted.

The hypothetical participant is already a single eligible Plan participant/common stockholder before the operational cutoff. This experiment does **not** establish that the Owner or any specific broker/account is eligible and does not authorize opening an account or sending money.

## Operational clock gate — before any target NAV/market payload

The Plan text says optional cash must reach the Plan Agent no later than two business days before the monthly investment date (the `payment date`) and will be applied on the next succeeding purchase date. It also states that directly issued optional-cash shares are priced using NAV and market price on the day preceding the relevant cash purchase investment date.

Before reading the target fixing NAV or market price, documentary evidence must uniquely establish for the October 2026 case:

1. the official monthly investment/payment date;
2. the next succeeding purchase date;
3. the exact day whose NAV and market price govern the optional-cash direct-issuance formula;
4. that the Plan terms remain operative without a superseding amendment/termination.

If these dates cannot be established from public issuer/Plan evidence without inference, verdict = `PARK_DATA` and **no target NAV/market payload may be read**. Do not substitute November, a dividend-reinvestment row, a nearby session or an inferred business-day convention.

## Frozen pricing branch

Primary Plan formula only.

Let:

- `V` = TYG per-share NAV on the exact official optional-cash fixing day;
- `P` = TYG market price per common share on that same official fixing day, using the issuer's Plan-defined market-price convention when publicly reconstructible;
- `DIRECT_ISSUANCE` = the Plan's premium branch for optional cash;
- `ISSUE_PRICE = max(V, 0.95 * P)` only if the direct-issuance branch applies.

If the Plan's discount/open-market branch applies, do not manufacture a 5% concession. Record `NO_DIRECT_ISSUANCE_CASE`; no alternate month or price is permitted.

If `DIRECT_ISSUANCE`:

`S = 5000 / ISSUE_PRICE`

`SAME_FIXING_MARK = S * P`

`GROSS_CONCESSION = SAME_FIXING_MARK - 5000`

This is an ideal same-fixing mark, not a realizable sale at that instant. It deliberately isolates the contractual issuance concession before delivery risk.

## Frozen costs / case verdict

The Plan discloses an Agent sale charge of `$15 + $0.05/share` if the participant directs the Plan Agent to sell shares. Use it as the central implementation deduction even though an actual immediate sale is not assumed possible.

`CENTRAL_COST = 15 + 0.05 * S`

`CENTRAL_CEILING = GROSS_CONCESSION - CENTRAL_COST`

Stress adds a single fixed 25 bp haircut to the same-fixing market value for delay/market slippage:

`STRESS_COST = CENTRAL_COST + 0.0025 * SAME_FIXING_MARK`

`STRESS_CEILING = GROSS_CONCESSION - STRESS_COST`

Case rules:

- `PARK_DATA` if the clock/fixing/branch or Plan continuity cannot be uniquely reconstructed before outcome access.
- `NO_DIRECT_ISSUANCE_CASE` if the open-market branch applies.
- `KILL_CASE` if direct issuance occurs but `CENTRAL_CEILING <= 0`.
- `PARK_ECONOMICS` if `CENTRAL_CEILING > 0` but `STRESS_CEILING <= 0`.
- `ADVANCE_IMPLEMENTATION_CHECK` only if both ceilings are positive.

No same-fixing result can be called executable PnL or a validated edge.

## Implementation check

Run only after `ADVANCE_IMPLEMENTATION_CHECK`.

Require public Plan/agent/issuer evidence sufficient to establish when the newly issued optional-cash shares were actually credited/available for disposition for this target purchase. If availability cannot be established without account-specific interaction, verdict = `PARK_DATA` after preserving the positive ceiling; do not infer instant credit from the pricing date.

If a public availability date/session is established, a separately fixed delivery-price calculation may be declared **before** reading that delivery-session price. This v1 does not pre-authorize a delivery PnL look.

## One-economic-look rule

No target fixing NAV/market read is allowed while another unresolved economic look is active. Claim the target case before the first numeric fixing payload and persist the claim. A newer remote claim wins.

## No-retuning rules

Do not change:

- $5,000 cash size;
- target October 30 monthly investment case;
- Plan branch formula;
- $15 + $0.05/share central cost;
- 25 bp stress haircut;
- issuer;
- fixing day;
- market/NAV source convention;
- or substitute another month

after any target numeric value is accessed.

## Alternative explanations / failure modes

- The discount can be much less than 5% because issue price is the greater of NAV and 95% of market.
- The fund may be in the open-market branch, producing no issuer concession.
- Fixed timing exposes the participant to price movement before shares are actually available.
- The Plan can be amended/terminated and orders can be rejected.
- Tax treatment and any account/broker constraints are not modeled.
- Historical same-issuer Plan results are already exposed and cannot be used as independent evidence.

## Inference ceiling

TEST_CAN_KILL = this exact October 2026 optional-cash case or show that its public implementation clock is not reconstructible.

TEST_CAN_SUPPORT = one future case has a positive predeclared discounted-issuance ceiling worth a separately declared delivery/eligibility study.

TEST_CANNOT_SAY = ALPHA, EDGE_VALIDATED, REPEATABILITY, BROKER_ELIGIBILITY, TAX_ADVANTAGE, EXECUTABLE_PNL, MULTI_ACCOUNT_CAPACITY, LIVE_READY or REAL_CAPITAL_READINESS.
