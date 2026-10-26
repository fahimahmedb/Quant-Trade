# V4.2 executable declaration — France/Germany content-signed debt-release repricing

`EXPERIMENT_ID = disc-france-oat-bund-debt-release-l1-v1`

`PARENT = disc-france-oat-bund-l1-v0`

`STATUS = PREDECLARED_BEFORE_YIELD_OUTCOME_ACCESS`

`LEVEL = L1`

`LIVE_CAPITAL = FORBIDDEN`

## 1. Research decision

Decide whether a mechanically enumerable, official French public-debt release has enough **content-signed daily relative repricing** versus Germany to justify futures-level FOAT/FGBL reconstruction.

This is intentionally narrower than the parent "unexpected fiscal surprise" mechanism. It tests a public-document content sign, **not market surprise versus expectations**. Therefore a null may kill only this exact content-signed expression, not the broader fiscal-surprise mechanism.

## 2. Official event population — frozen before yield access

Population rule: every INSEE quarterly `Dette trimestrielle de Maastricht des administrations publiques` release from 2023-Q1 through 2026-Q2 inclusive. No release is selected because of remembered market reaction.

Classification rule, using only the numbers stated in that release at publication:
- `ADVERSE` if published debt/GDP ratio is higher than the immediately preceding-quarter ratio stated in the same release;
- `BENIGN` if lower;
- `NEUTRAL` if unchanged.

Subsequent statistical revisions do not retroactively change the classification. This is deliberate point-in-publication-time semantics.

| Quarter | Publication date | INSEE publication | Published ratio | Prior ratio as stated | Class |
|---|---|---|---:|---:|---|
| 2023-Q1 | 2023-06-30 | https://www.insee.fr/fr/statistiques/7638614 | 112.5 | prior quarter lower by 0.7pp | ADVERSE |
| 2023-Q2 | 2023-09-29 | https://www.insee.fr/fr/statistiques/7675970 | 111.8 | 112.5 | BENIGN |
| 2023-Q3 | 2023-12-22 | https://www.insee.fr/fr/statistiques/7739721 | 111.7 | 111.7 as stated / unchanged | NEUTRAL |
| 2023-Q4 | 2024-03-26 | https://www.insee.fr/fr/statistiques/8062883 | 110.6 | 111.7 | BENIGN |
| 2024-Q1 | 2024-06-28 | https://www.insee.fr/fr/statistiques/8210074 | 110.7 | 109.9 | ADVERSE |
| 2024-Q2 | 2024-09-27 | https://www.insee.fr/fr/statistiques/8260877 | 112.0 | 110.5 | ADVERSE |
| 2024-Q3 | 2024-12-20 | https://www.insee.fr/fr/statistiques/8316840 | 113.7 | 112.2 | ADVERSE |
| 2024-Q4 | 2025-03-27 | https://www.insee.fr/fr/statistiques/8540321 | 113.0 | 113.6 | BENIGN |
| 2025-Q1 | 2025-06-26 | https://www.insee.fr/fr/statistiques/8597434 | 113.9 | 113.2 | ADVERSE |
| 2025-Q2 | 2025-09-25 | https://www.insee.fr/fr/statistiques/8644919 | 115.6 | 113.9 | ADVERSE |
| 2025-Q3 | 2025-12-19 | https://www.insee.fr/fr/statistiques/8686951 | 117.4 | 115.7 | ADVERSE |
| 2025-Q4 | 2026-03-27 | https://www.insee.fr/fr/statistiques/8955019 | 115.6 | 117.2 | BENIGN |
| 2026-Q1 | 2026-06-25 | https://www.insee.fr/fr/statistiques/9010340 | 117.5 | 115.7 | ADVERSE |
| 2026-Q2 | 2026-09-29 | https://www.insee.fr/fr/statistiques/9053525 | 119.0 | 117.5 | ADVERSE |

Counts frozen: 14 events = 9 ADVERSE, 4 BENIGN, 1 NEUTRAL.

Important semantic limitation: the class measures document content direction in debt/GDP, not deviation from consensus expectations. It cannot by itself establish an information surprise.

## 3. Yield proxies — frozen

France: Banque de France daily `TEC10`, a constant-maturity 10-year fictitious Treasury yield obtained by interpolation among French Treasury securities.

Germany: Deutsche Bundesbank daily 10-year Svensson term-structure spot yield on listed Federal securities, series:
`BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A`.

The proxy-construction mismatch is accepted only for coarse directional Discovery. It is not an executable futures pair.

## 4. Exact outcome rule — frozen before data access

For each event:

- `PRE_DATE` = last date with both France and Germany daily observations strictly **before** the INSEE publication calendar date.
- `POST_DATE` = first date with both France and Germany daily observations strictly **after** the publication calendar date.
- Same-day observations are deliberately excluded because historical intraday release times are not assumed.
- `SPREAD_t = FR_TEC10_t - DE_10Y_t`, in percentage points.
- `DELTA_BP = (SPREAD_POST - SPREAD_PRE) * 100`.
- `SIGNED_BP = DELTA_BP` for ADVERSE events; `SIGNED_BP = -DELTA_BP` for BENIGN events; NEUTRAL events are descriptive only and excluded from signed-class promotion statistics.

No alternate horizon, same-day version, lag search, event exclusion, country substitution or subperiod search is allowed after outcomes are read. A changed rule is a new linked experiment.

## 5. Mechanism and alternative

`MECHANISM` — worsening published French fiscal/debt content may cause constrained holders/hedgers to reprice French sovereign risk relative to Germany, while improving content may move the relative spread the other way.

`WHO_PAYS` — participants needing immediate benchmark/mandate/risk-budget adjustment after public fiscal information.

`WHY_PERSIST` — sovereign benchmark, collateral, mandate and balance-sheet constraints can make relative adjustment imperfect; this remains a hypothesis.

`PRIMARY_SIGNATURE` — median `SIGNED_BP` across non-neutral events is positive and direction consistency exceeds chance enough to justify a more faithful expression.

`ALTERNATIVE_EXPLANATION` — relative widening may be produced by Bund safe-haven demand / broad risk-off rather than France-specific debt information; the content classification may also be anticipated by markets.

## 6. Adequacy gate — fixed

The economic result is interpretable only if:

1. both official series provide PRE and POST observations for at least 12/14 events;
2. at least 8 non-neutral events remain after purely mechanical missing-data handling;
3. no event is excluded based on the realized yield move;
4. publication date and class come from the frozen INSEE table above;
5. no single event contributes more than 50% of the absolute sum of non-neutral `SIGNED_BP`.

Failure of 1–4 => `INCONCLUSIVE`/`PARK_DATA` as appropriate. Failure of 5 prevents mechanism-level inference but does not erase the raw expression result.

## 7. Decision thresholds — fixed before outcomes

This L1 is worth futures reconstruction only if all are true on non-neutral events:

- median `SIGNED_BP >= +1.5 bp`;
- direction consistency (`SIGNED_BP > 0`) `>= 60%`;
- mean `SIGNED_BP > 0`;
- adequacy gate passes.

These are a Discovery hurdle, not a significance test and not evidence of alpha.

If median signed response is `<= 0` with adequacy passed => `KILL_EXPRESSION`.

If response is positive but median `< 1.5 bp` or consistency `< 60%` => `PARK_ECONOMICS` unless a predeclared adequacy failure dominates.

Passing the hurdle => at most `PROMOTE_EXPRESSION` before red-team.

## 8. Inference rights

### TEST_CAN_KILL
Only the exact expression: quarterly INSEE debt/GDP content sign -> next-full-day France-minus-Germany daily yield repricing using the frozen proxies and 2023-Q1..2026-Q2 event population.

### TEST_CAN_SUPPORT
A positive/hurdle-passing result can support spending effort on a futures-level mapping or, after the red-team below, limited support for France-specific relative repricing.

### TEST_CANNOT_SAY
This test cannot establish:
- true expectation surprise;
- executable FOAT/FGBL alpha;
- intraday reaction timing;
- CTD/DV01/carry/roll/basis/repo/margin economics;
- capacity or live readiness;
- persistent anomaly versus compensated sovereign/crash risk;
- causality from debt publication alone.

## 9. Bias direction

- Timing: conservative/coarse; skipping publication-day observation may dilute a fast effect.
- Signal amplitude: unknown; next-day daily proxies can mix later news.
- Event surprise: upward or downward unknown because no consensus forecast is modeled.
- Construction mismatch FR vs DE: unknown noise bias.
- Costs/execution: not modeled; no P&L claim.
- Survivorship: low at sovereign-series level; publication revisions handled by using release-page content for classification.

## 10. Unit-economics hurdle

No futures engineering is authorized before the L1 hurdle passes. `1.5 bp` median signed relative move is used only as a coarse headroom threshold: a duration-neutral €100k-class sovereign-futures expression would need enough gross bps to dominate ordinary small-account friction before CTD/DV01/margin work is worth doing. Exact futures economics remain unproven.

Event frequency is approximately four releases/year, so even a real effect must have meaningful per-event size to matter.

## 11. One cheap red-team if positive

`RED_TEAM = BUND_SAFE_HAVEN_ONLY`

Using the same already-accessed daily pair only, inspect the non-neutral events' absolute France leg. For adverse events, require the median France 10Y yield change (`FR_POST - FR_PRE`) to be `>= 0`; for benign events, require the median sign-adjusted France leg to be `>= 0` after multiplying benign moves by `-1`.

If the relative-spread hurdle passes but this France-leg sign check fails, verdict remains at most `PROMOTE_EXPRESSION` and **cannot** become `PROMOTE_MECHANISM`; the result may primarily reflect Bund safe-haven movement.

No additional market series is authorized for this red-team.

## 12. Prior exposure / multiplicity

Parent `disc-france-oat-bund-l1-v0` previously attempted a different public-yield route and received HTTP 404 with zero yield rows; no economic payoff was computed. One incidental TEC10 quote was previously recorded in repo history and is not used to choose this event set or thresholds.

This linked expression is not independent of the parent mechanism cluster. It adds one expression/look when outcomes are actually accessed.

## 13. Execution authorization boundary

This declaration itself authorizes **no outcome access until committed remotely**. After remote publication, a CAS/claim must be persisted before fetching/joining the official France/Germany yield histories. One execution only; no replay after realized results.
