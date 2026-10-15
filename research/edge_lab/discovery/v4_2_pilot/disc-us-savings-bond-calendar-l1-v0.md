# Savings-bond calendar feature — linked L1 preparation v0

STATUS = DESIGN_NOT_EXECUTABLE
LEVEL = L1_EXPLORATORY_ACCOUNTING_PROXY
ECONOMIC_LOOK_OPENED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

Parent evidence: `../qualifications/us-savings-bond-calendar-legal-followup-2026-10-14.json` and `../qualifications/us-savings-bond-calendar-l0-2026-10-14.json`.

This is one completed non-outcome preparation. It does not amend any frozen A–E/VX protocol, reserve a look or authorize data access. A linked executable declaration, exact bounded retrieval manifest and CAS claim must precede any selected rate/redemption-value access. No account or actual purchase is required or permitted.

## Mechanism and discriminating question

Treasury's book-entry Series I contract assigns the first day of the posting month as issue date. If two purchases really post in the same month, delaying the cash outlay may preserve the same bond accrual while reducing cash tied up. Treasury pays the contractual interest; capacity limits, non-transferability, eligibility, posting uncertainty, lockup and forfeited interest can remove any useful rent. This is a cash-management feature, not exchange-traded alpha.

Does the late-posting expression beat a same-currency liquid cash proxy after the full holding period, redemption penalty and a stated operational friction, rather than merely earning more interest per day held? A positive calendar increment alone is insufficient.

## Fixed historical accounting case, not a fresh prospective sample

- Issue cohort: October 2024. One fixed case chosen for completed holding period and weekday endpoints, without viewing its rates/redemption values. No year/month search or substitution.
- Initial cash: USD10,000, before tax; individual annual I-bond capacity reference only. Owner eligibility remains UNKNOWN. No claim of access or unused historical allowance.
- Early expression E: principal posts October 1, 2024.
- Late expression L (primary): principal posts October 31, 2024, the same calendar month. Successful posting is an optimistic assumption, not an observed fill.
- Both redeem November 3, 2025. This is 398 days after early posting and 368 after late posting; both exceed one year from actual posting, avoiding a shortcut based only on issue-month age.
- Benchmark anchor: the official U.S. Treasury one-year daily par yield dated September 30, 2024, known before either hypothetical outlay. Set `b = percentage_quote / 100`. No date fallback, nearby tenor or alternate provider.
- `b` is held constant in a simple ACT/365 cash proxy. It is an indicative curve observation, not an executable deposit or a realized rolling-bill strategy; reinvestment, term/liquidity and instrument differences remain material.
- `R_OCT` is Treasury's official redemption value per USD100 initial Series I principal, October2024 issue cohort, November2025 redemption month. Use only if the official value definition authenticates monthly applicability and whether the three-month penalty is already incorporated. Never subtract it twice. No estimated inflation path or fitted compounding convention.
- Exposed document windows do not become virgin by changing supplier or naming a new declaration. This is exploratory accounting, not confirmatory OOS.

## Fixed cashflow calculations, no values acquired yet

Let `Q = 10000` and `D = 398`, with 30 days of retained cash before L posts.

- E terminal value: `Q * R_OCT / 100`.
- L terminal value: `Q * R_OCT / 100 + Q * b * 30 / 365`.
- Benchmark terminal value: `Q * (1 + b * 398 / 365)`.
- Central excess: L terminal minus benchmark terminal.
- Calendar increment: L terminal minus E terminal.
- Central operational cost: USD0 (optimistic).
- Stress operational cost: USD10 once per expression, explicitly assumed, not a broker or Treasury tariff.
- Stress excess: central excess minus USD10. Stress calendar increment: calendar increment minus USD10, treating the extra scheduling burden as an incremental hurdle.

The retained cash interest is kept as idle cash after October31; no interest on interest or double use of principal. Match initial capital and terminal horizon. Report absolute dollars and basis points of initial capital, plus the break-even benchmark rate. Do not annualize alpha or report Sharpe. Federal tax is excluded on both sides; no claim about Owner net tax, FX or eligibility. Principal lockup and lack of transferability are disclosed even if the numeric hurdle passes.

## One conditional adversarial case, counted now

Only if the primary hurdles pass: assume the same late cash outlay fails to post until November1, 2024, changing the issue cohort to November2024. Redemption remains November3, 2025, more than one year after posting. Read exactly one additional official redemption value `R_NOV`, with the same penalty-definition gate. Retained cash interest remains exactly 30 days, with no credit for money in transit. Recompute late excess and subtract USD10. No other delay, month, holding horizon, cost or benchmark variant.

Expressions planned: E comparator, L primary, and one conditional posting-slip adversary; one cash benchmark. All are dependent, not independent trials. The adversarial access must be inside the future published reservation envelope; otherwise stop without fetching it.

## Adequacy and source gates before execution

All must be resolved without first inspecting selected economic values:

1. Verify applicable contractual issue/accrual/redemption rules for the historical2024–2025 case. A current/2025 legal description alone is not proof of historical applicability.
2. Establish a free official Treasury route for the specified historical redemption values, monthly applicability, units and penalty treatment; no account, calculator parameter search or unsupported reconstructed formula. A parameterized official calculator is permissible only under a subsequently frozen request and claim.
3. Establish a free, permitted official route for the single dated1Y quote. The future retrieval manifest must declare the entire exposed response scope if the endpoint necessarily returns surrounding observations; do not silently call a full annual payload one observation.
4. Authenticate source versions/rights, bound requests/bytes/time, freeze software/manual arithmetic and receipt capture in the existing Discovery runtime. No parallel framework.

A source/version/definition gap => PARK_DATA before calculation; do not pick another cohort or provider. No launch while another economic look is unresolved. No repeat of completed legal pages without a new specific version question.

## Decision contract to carry unchanged into any executable declaration

- Adequate source data and central excess <=0: KILL_EXPRESSION for this exact cohort/benchmark expression only.
- Central excess >0 but stress excess <=0 or stress calendar increment <=0: PARK_ECONOMICS.
- Both primary stress hurdles >0, and the unique posting-slip adversary also has stress excess >0: at most PROMOTE_EXPRESSION for later posting/benchmark qualification.
- Primary positive but posting-slip stress excess <=0: PARK_ECONOMICS, recording posting sensitivity rather than selecting E as replacement.
- Missing any required source/penalty/clock fact: PARK_DATA, not a numeric kill or promote.

TEST_CAN_KILL = this exact fully funded late-posting accounting expression against its explicitly assumed cash proxy.
TEST_CAN_SUPPORT = bounded validation of posting reliability and a genuinely accessible matched cash alternative.
TEST_CANNOT_SAY = scalable alpha, realized executable arbitrage, full-family profitability, prospective confirmation, Owner eligibility, tax-adjusted edge or capital/live readiness.

One historical case has no population confidence interval or statistical power for a family claim. Positive accounting may reflect the proxy or liquidity/rate-risk compensation. Report that limitation, not a fabricated significance measure.

## Prior exposures and next decision

All previous N/M and private-history UNKNOWNs, rejected families and public selections remain consumed. The unreserved TreasuryDirect buying-page exposure `unplanned-treasurydirect-current-rate-panel-20261014` includes May–October2026 EE2.40%, I composite4.26%, I fixed0.90%; it is not used to choose numerical outcomes here and cannot be erased. Source acquisition/hash details remain in the parent proof. October2024/November2025 values and the September30,2024 benchmark have not been requested in this preparation; no assertion that private history is pristine.

NEXT = after higher-priority prospective admission and only without reopening an economic look, resolve the exact official historical value-route/penalty and version questions in one bounded metadata-only step. If no route can be qualified within that step, PARK_DATA this design. No selected values until a separately published executable declaration plus original-runtime CAS reservation.
