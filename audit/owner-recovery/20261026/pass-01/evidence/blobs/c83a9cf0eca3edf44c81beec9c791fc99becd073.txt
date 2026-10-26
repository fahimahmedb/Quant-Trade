# F1 Stage A — first documented discovery result

Source: Binance Vision / Binance Public Data, CC BY-NC-SA 4.0
([licence](https://creativecommons.org/licenses/by-nc-sa/4.0/)).
Non-commercial historical research; no live use or capital authority.

Execution: [37915190172](https://github.com/fahimahmedb/Quant-Trade/actions/runs/37915190172),
commit `8d93861edc4e1ff07b6265d4e80e6a429cffd0b7`.
Published evidence commit `5cfdddbd49fda9f0083b3cff2d2dfa558af38700`.
Result SHA256 `554988d5c136caf43387d5338e0db226516e4a8b9e9a7ddf42c290aac6dbab03`.
Economic harness SHA256 `5a773f45c630c559532ccfbf6888bf506adf6e8a3c31b9fbe09f65ef33ec239c`.
The original result bytes and attribution/exposure metadata are adjacent files.

RESULT = Discovery completed over 2020-01-01..2023-12-31, 1,461 calendar days,
242 symbols with usable funding, spot and perpetual data. The frozen rule
selects theta = 0.20, the cell with the highest base Sharpe. No cell is changed
or added after observation.

| Annualised funding threshold | Base mean/year | Base Sharpe | Robust t | Mean/year at doubled costs |
|---|---:|---:|---:|---:|
| 5% | 0.257% | 0.033 | 0.069 | -6.247% |
| 10% | 2.135% | 0.261 | 0.498 | -3.769% |
| **20% (selected)** | **3.823%** | **0.490** | **0.957** | **1.114%** |

EFFECT_SIZE = Selected cell: compounded total return 15.171%, CAGR 3.592%,
maximum drawdown 7.061%, exposure on 52.09% of days, 9/16 positive calendar
quarters. Only 2021 has a positive annual compounded return: 2020 -2.780%,
2021 +23.792%, 2022 -0.675%, 2023 -3.652%.

UNCERTAINTY = Fixed max(Newey-West 7, 21) SE of daily mean = 0.0001094115.
The descriptive normal 95% interval for annualised mean is -4.004%..11.651%.
The selected cell's one-sided 95% upper Sharpe bound is 1.333. These are
discovery statistics after selection among three cells, not confirmatory
intervals or evidence about the unread Stage B window.

POWER_LIMITATION = 242 symbols do not constitute 242 independent experiments;
the effective observations are calendar days with dependence handled by the
registered SE. Stage A is for discovery/selection. The registered 1,004-day B
window has an assumed i.i.d. MDE Sharpe about 1.53; 80% power needs about 2.04.
The inaccessible legacy executor history remains UNKNOWN in the metadata.
Resuming from its last published unexposed state does not prove that history
or authorize a confirmatory claim.

ECONOMIC_SIGNIFICANCE = Selected mean is 0.177 percentage points/year below
the declared assumed 4% cash comparator; doubled-cost mean is 2.886 points
below it. This comparator is an assumption, not a measured 2020–2023 yield.
The model records 531 liquidation-proxy events. Its additive NAV-unit
components are funding +0.37436, basis +0.07109, fees/slippage -0.12125 and
liquidation penalty -0.17248. These sum to the final NAV change; they are not
annual returns. Daily-bar liquidation approximations and venue risk remain
the preregistered limits.

FAILED_CRITERIA = No confirmatory claim in discovery; t = 0.957 is below the
registered B threshold 2.539 and the cash comparison is negative. The JSON
cell labels are descriptive outputs of the shared harness and must not be
interpreted as a final sealed-family verdict. Stage B has not been analysed.

LESSON = High realised funding does not translate directly into high net
portfolio return under these fees and liquidation assumptions. Raising the
threshold to the already registered 20% cell reduces costs and liquidation
events, but the observed edge remains economically weak.

FAMILY_STATUS = INCONCLUSIVE_UNDERPOWERED (discovery only; sealed verdict pending).

NEXT_DECISION = Freeze theta 0.20, result hash and harness; complete and verify
the separate B compressed capture, then execute its single documented
evaluation. Preserve legacy exposure uncertainty and withhold a registered
confirmatory claim unless that lineage is established. Never rerun A or tune
cells, costs or thresholds from these observations.

## Result falsification disposition

DECISION_CHANGING_DEFECT = NONE newly established by this result.

EVIDENCE = Original result/meta SHA256 match; selection independently checked
against all three persisted Sharpes; all series have 1,461 days; persisted
daily means and Sharpes agree with arithmetic recomputation; all 21,088
planned compressed input files were independently verified before analysis.
No experiment was rerun for this check. The exposure-history limitation
above remains explicit and limits claims.

MINIMUM_TEST_OR_FIX = No economic-code repair or parameter change. Authenticate
this exact A result and the B capture before the single B evaluation.

VERDICT = EXECUTE the single documented B evaluation when capture verification
passes; treat it as research evidence with unresolved legacy lineage, not an
authorized confirmatory or live-trading claim. This closes the bounded
result review; no additional review loop is required before execution.
