# V4.2 pilot contract — CFE / VIX term premium

`EXPERIMENT_ID = disc-cfe-vix-term-premium-l1-v0`

`STATUS = PREDECLARED_DESIGN_ONLY`

`LEVEL = L1`

`LIVE_CAPITAL = FORBIDDEN`

## 1. Decision targeted

Decide whether one narrowly specified VX-futures expression deserves a cleaner L2/L3 reconstruction, or whether this expression should be killed/parked before any BBO/TAS/margin engineering.

This test is **not** designed to prove that volatility risk premium exists in general.

## 2. Expression tested

Contract-level, no continuous-series optimization:

- instrument: listed CFE VX futures contracts;
- entry proxy: official settlement exactly 20 trading days before final settlement, when available under a predeclared calendar rule;
- position: short one contract notionally normalized only for return comparison, not for live sizing;
- exit proxy: final pre-settlement/final settlement value under one fixed rule declared before outcome calculation;
- one observation per contract;
- no horizon search;
- no maturity search;
- no alternate roll rules inside this experiment.

If the required public settlement observations cannot be assembled consistently without changing the rule, verdict is `PARK_DATA`, not a rewritten test.

## 3. Mechanism contract

`MECHANISM` — buyers of convexity / volatility protection may accept a persistent premium that is transferred to sellers of VX futures risk.

`WHO_PAYS` — participants demanding volatility protection / immediacy / convexity exposure.

`WHY_PERSIST` — bearing crash-sensitive volatility risk may require compensation; institutional mandate/risk constraints can keep demand non-price-neutral. This is a hypothesis, not a conclusion.

`PRIMARY_SIGNATURE` — before looking at returns, the mechanism predicts that the short-contract payoff should be more favorable when the futures contract begins at a larger positive premium to contemporaneous spot VIX, under one fixed monotonicity check. The exact basis measure and binning rule must be frozen before calculation.

`ALTERNATIVE_EXPLANATION` — any apparent short-VX profit may be a mechanical convergence/basis exposure, sample/regime artifact, or compensation for general equity/volatility crash risk rather than a distinct exploitable signal.

## 4. Inference rights

### TEST_CAN_KILL

A negative result can kill **this exact 20-trading-day short-contract expression** if:

1. required settlements are available for a sufficiently broad contract history under the fixed rule;
2. no material sample construction failure is observed;
3. the gross result is non-positive or economically negligible even before a realistic friction allowance; and
4. the primary signature is absent or opposite under the predeclared monotonicity check.

A negative L1 result does **not** automatically kill the general volatility-risk-premium mechanism.

### TEST_CAN_SUPPORT

A positive result can support only:

- `PROMOTE_EXPRESSION` if the exact expression is materially positive and the mechanism signature points in the expected direction;
- `PROMOTE_MECHANISM` only if the signature also discriminates meaningfully against the stated alternative explanation;
- never direct strict-validation success.

### TEST_CANNOT_SAY

This L1 test cannot establish:

- executable BBO/fill PnL;
- margin/capital efficiency;
- intraday slippage;
- capacity;
- crash-tail acceptability;
- live readiness;
- that spot VIX behavior equals VX-futures tradability;
- that the mechanism is independent of known broad volatility/equity risk premia.

## 5. Bias map

| Dimension | Expected L1 bias |
|---|---|
| Signal amplitude | UNKNOWN; settlement-to-settlement may overstate or understate implementable payoff |
| Timing | COARSE; no intraday entry/execution timing |
| Costs | UPWARD until explicit cost band is subtracted |
| Survivorship | LOW concern at contract level if complete contract history is used; verify missing-contract handling |
| Execution quality | UPWARD; official settlements are not guaranteed fills |
| Capacity | UNSPOKEN / cannot infer |

## 6. Data adequacy required for a negative to be informative

Before interpreting a null/negative as `KILL_EXPRESSION`, record:

- number of eligible contracts;
- missing-contract rate;
- calendar consistency;
- whether final-settlement observations are comparable across history;
- whether one or a few crisis contracts dominate aggregate economics.

If these conditions fail materially, use `PARK_DATA` or `INCONCLUSIVE`. Do not change the horizon after seeing the result.

## 7. Unit-economics envelope before data engineering

Before any deeper reconstruction, estimate only the following coarse envelope:

- observations per year under this exact contract rule;
- plausible gross return per contract exposure;
- rough round-trip exchange/broker/spread friction band for a small account;
- capital/margin order of magnitude only if publicly accessible cheaply;
- crash/tail concentration risk;
- likely sensitivity to entry delay.

`BREAK_EVEN_FRICTION` must be computed from the observed gross effect before promotion. Promotion requires non-trivial distance between break-even friction and a defensible small-account friction interval.

No universal x2/x3 cost multiplier is used.

## 8. Predeclared cheap red-team if L1 is positive

Run exactly one adversarial check before strict validation:

`RED_TEAM = naive risk/basis explanation`

Test whether the result remains economically meaningful after conditioning on / benchmarking against the predeclared initial futures-to-spot basis information that forms the primary signature. The goal is to determine whether the expression contains anything beyond a trivial basis/convergence relation.

If implementing this red-team requires new heavy data infrastructure, stop at `PROMOTE_EXPRESSION` and move the discrimination question into L2; do not build infrastructure inside L1.

## 9. Verdict map

- `KILL_EXPRESSION` — exact 20-day expression fails under adequate data.
- `KILL_MECHANISM` — forbidden from a single L1 unless both favorable economics and the primary mechanism signature are contradicted with adequate data; requires explicit justification.
- `PARK_DATA` — data consistency prevents interpretation.
- `PARK_ECONOMICS` — effect may exist but break-even friction/tail economics are implausible for the project objective.
- `PROMOTE_EXPRESSION` — positive expression with enough economic headroom to justify cleaner execution testing.
- `PROMOTE_MECHANISM` — expression positive and predeclared signature supports the causal story against the main alternative.
- `PROMOTE_HIGH` — only if effect, signature, and economic headroom are unusually strong and the cheap red-team survives.
- `INCONCLUSIVE` — only for predeclared adequacy failure, never as a rescue after an ordinary negative.

## 10. Post-result mutation rule

Any change to 20-day horizon, contract selection, basis definition, sample exclusion, settlement rule, cost band, or red-team definition after outcome exposure creates a new linked experiment and counts as another expression in the same mechanism cluster.
