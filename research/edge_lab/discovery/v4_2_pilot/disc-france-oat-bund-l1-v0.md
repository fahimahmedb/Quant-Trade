# V4.2 pilot contract — France OAT / Bund relative repricing

`EXPERIMENT_ID = disc-france-oat-bund-l1-v0`

`STATUS = PREDECLARED_DESIGN_ONLY`

`LEVEL = L1`

`LIVE_CAPITAL = FORBIDDEN`

## 1. Decision targeted

Decide whether one coarse, event-linked France-vs-Germany sovereign-risk expression shows enough directional/economic signal to justify a future futures-level FOAT/FGBL reconstruction, or whether this exact expression should be killed/parked before CTD/DV01/roll/BBO work.

The family question already stored in the repo is narrower than a generic "France risk" story: unexpected first-public fiscal/financing information must create a delayed relative repricing beyond common euro-duration risk. This pilot preserves that scope.

## 2. Expression tested

This L1 tests **relative spread repricing**, not tradable P&L.

- event population: only a predeclared set of official French fiscal/financing publications or announcements whose public timestamp can be established without using remembered market outcomes;
- event set must be frozen in this file or an immutable linked artifact before reading the return series;
- proxy outcome: change in a public France 10Y sovereign-yield proxy minus change in a public Germany 10Y sovereign-yield proxy;
- horizon: close/official daily observation immediately before the event to the first full daily observation after the event; if event timing makes same-day causality ambiguous, use the next full day under one fixed rule;
- sign convention: adverse French fiscal/financing surprise is expected to widen France-minus-Germany relative yield/spread;
- no country, horizon, event-type, threshold or subperiod search inside this experiment.

If a clean ex-ante event population cannot be assembled cheaply without using outcome knowledge, verdict is `PARK_DATA`, not a rewritten event study.

## 3. Mechanism contract

`MECHANISM` — sufficiently surprising French fiscal/financing information may force benchmark, mandate, balance-sheet or risk-budget constrained participants to reprice French sovereign risk relative to common euro duration risk with some delay.

`WHO_PAYS` — investors/hedgers requiring immediate sovereign-risk capacity or constrained rebalancing after new information.

`WHY_PERSIST` — relative sovereign risk can be segmented by mandate, benchmark, collateral, balance-sheet and policy constraints; this is a hypothesis, not evidence of persistent inefficiency.

`PRIMARY_SIGNATURE` — events classified ex ante as adverse fiscal/financing surprises should produce a same-sign widening in the France-minus-Germany proxy, while benign/improving surprises should not systematically produce the same widening. The classification rule must be frozen before market-outcome access.

`ALTERNATIVE_EXPLANATION` — observed spread moves may be driven by common euro-rate shocks, Bund safe-haven flows, ECB communication, broad risk-off conditions, or post-event political news rather than the targeted fiscal information.

## 4. Inference rights

### TEST_CAN_KILL

A negative/null result can kill **this exact daily relative-spread expression around the frozen event set** only if:

1. the event timestamps are genuinely public-before-outcome and causally ordered;
2. the sign/classification rule is fixed ex ante;
3. the public France and Germany series are aligned consistently;
4. the event count is sufficient to detect an effect large enough to matter for a later tradable expression; and
5. no single episode dominates the result.

A null cannot kill all OAT/Bund relative-value mechanisms or all fiscal-risk repricing.

### TEST_CAN_SUPPORT

A positive result can support only:

- `PROMOTE_EXPRESSION` toward futures-level mapping if the direction is coherent and economically non-trivial;
- `PROMOTE_MECHANISM` only if the predeclared mechanism signature discriminates against the strongest common-rate/risk-off explanation;
- never a claim of executable FOAT/FGBL alpha.

### TEST_CANNOT_SAY

This L1 cannot establish:

- FOAT/FGBL executable P&L;
- correct CTD/DV01 hedge ratio;
- carry/roll/basis economics;
- repo/funding/margin effects;
- intraday reaction timing;
- first-news precedence beyond the authenticated event timestamp used;
- capacity;
- live readiness;
- that a sovereign default is likely or necessary for the mechanism.

## 5. Bias map

| Dimension | Expected L1 bias |
|---|---|
| Signal amplitude | UNKNOWN; daily yields may dilute intraday effect or mix later news |
| Timing | COARSE and potentially DOWNWARD for short-lived reactions; potentially UPWARD if later same-day news is mixed in |
| Costs | NOT MODELED as tradable PnL; cannot infer execution economics directly |
| Survivorship | LOW at sovereign-index level but historical vintage/publication integrity must be checked |
| Execution quality | UNSPOKEN; yield/index proxy is not a fillable futures pair |
| Capacity | UNSPOKEN / cannot infer |

## 6. Event-set adequacy before outcome interpretation

Before any result is considered, record:

- exact event IDs/dates/timestamps;
- source used for each event;
- ex-ante adverse/benign/neutral classification rule;
- whether classification depended on contemporaneous expectations or only document content;
- exclusions and why;
- number of events by class;
- known clustering (multiple events in same episode/week);
- any prior public exposure already present in the repo, including the preserved incidental TEC10 quote exposure.

If event classification cannot be made without hindsight or the event set is too small/clustered to discriminate a meaningful effect, use `PARK_DATA` or `INCONCLUSIVE`.

## 7. Unit-economics envelope before futures engineering

Because the L1 proxy is not tradable P&L, unit economics are expressed as a hurdle for whether futures reconstruction is worth buying:

- median absolute relative-spread response in basis points;
- event frequency per year;
- direction-consistency rate under the predeclared sign rule;
- rough FOAT/FGBL DV01 scale needed to convert a given spread move into candidate gross P&L;
- plausible small-account round-trip friction/margin order of magnitude only if available cheaply;
- sensitivity to one-day execution delay.

`BREAK_EVEN_FRICTION` is not computed from the yield proxy alone as if it were P&L. Instead, promotion requires that the observed spread move be large enough that a plausible duration-neutral futures translation could still have economic headroom after a defensible friction band.

If that hurdle is obviously not met, use `PARK_ECONOMICS` without building CTD/DV01 infrastructure.

## 8. Predeclared cheap red-team if L1 is positive

`RED_TEAM = common euro-rate / broad risk-off explanation`

Run exactly one cheap falsifier using an already-accessible public control that captures broad euro-duration or risk-off movement without requiring futures reconstruction. The purpose is to test whether the France-minus-Germany response is genuinely relative rather than just a generic rates move.

If no defensible cheap control is available, stop at `PROMOTE_EXPRESSION` and move the discrimination question into L2. Do not create a new macro data platform inside L1.

## 9. Verdict map

- `KILL_EXPRESSION` — frozen event-set daily relative-spread expression fails with adequate causal event/data quality.
- `KILL_MECHANISM` — forbidden from one coarse L1 unless the predeclared relative signature itself is contradicted under adequate data and a favorable test geometry; explicit justification required.
- `PARK_DATA` — event clock/classification or comparable series are not adequate.
- `PARK_ECONOMICS` — response exists but is too small/infrequent to justify futures-level reconstruction.
- `PROMOTE_EXPRESSION` — directionally coherent, economically non-trivial relative response justifies FOAT/FGBL mapping.
- `PROMOTE_MECHANISM` — response plus cheap control supports the specific delayed-relative-repricing story against the main alternative.
- `PROMOTE_HIGH` — only if event causality, effect size, direction consistency and economic headroom are unusually strong and the red-team survives.
- `INCONCLUSIVE` — only for predeclared adequacy failure.

## 10. Anti-requalification

Any post-result change to event set, surprise classification, sign convention, daily horizon, France/Germany proxy, exclusion rule, control, or economic hurdle creates a new linked experiment in the same mechanism cluster.
