# `QUANT_FASTLANE_HPIT_V1` protocol — DRAFT (not sealed)

Status `DRAFT_NOT_SEALED`. Canonical sha256 of this draft: `sha256:ab70360418ec472f084b638a4adf1370f0cebd01cbb805912ffac9b4f59a98c5`. Sealing requires flipping status to `FINAL_FOR_SEAL` by explicit decision, then `python3 scripts/fastlane.py seal-prereg --protocol research/fastlane/QUANT_FASTLANE_HPIT_V1_PROTOCOL.json`; the seal is write-once.

## Frozen D5 elements

- Events: SEC Insider Transactions Data Sets, original Form 4 only, code P / acquired A.
- Entry: open of the first vendor session strictly after FILING_DATE.
- Splits: discovery 2006-01-01→2018-12-31, walk-forward 2019-01-01→2021-06-30, holdout 2021-07-01→2026-06-30 (sealed, one look).
- Inference: daily net return of a calendar-time portfolio in excess of SPY; 80-session block bootstrap; FF5+UMD robustness.
- Multiplicity: M ≤ 48 declared; DSR + Romano-Wolf/SPA on discovery; ≤ 3 finalists; Holm α=0.05 on holdout.
- Frictions: Abdi–Ranaldo spread with ADV20-bucket floor, per-share commission with minimum, square-root impact, participation ≤ 0.1 % ADV20; missing delisting −30 % (−100 % stress); capacity at 1×/10×/100× C0.
- GO: net alpha vs SPY ≥ 3 %/yr AND Holm p < 0.05 AND positive at 1× C0 AND DSR > 0.95 AND a GO-eligible vendor attestation.

## Variant grid (M = 21)

Adequacy (outcome-blind): ≥ 50 issuer-days/yr in every split and ≥ 20 average concurrent holdout positions.

| Variant | Disc/yr | WF/yr | Holdout/yr | Avg concurrent (K=100) | Per-event MDE (bp) | Portfolio MDE (%/yr) | Holm-step MDE (%/yr) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `OD_V10K_H5` | 8366.8 | 7320.4 | 6656.4 | 100.0 | 13.4 | 6.77 | 8.08 |
| `OD_V10K_H20` | 8366.8 | 7320.4 | 6656.4 | 100.0 | 53.7 | 6.77 | 8.08 |
| `OD_V10K_H60` | 8366.8 | 7320.4 | 6656.4 | 100.0 | 161.1 | 6.77 | 8.08 |
| `OD_V100K_H5` | 2917.0 | 3103.2 | 2967.6 | 58.9 | 17.5 | 8.82 | 10.53 |
| `OD_V100K_H20` | 2917.0 | 3103.2 | 2967.6 | 100.0 | 53.7 | 6.77 | 8.08 |
| `OD_V100K_H60` | 2917.0 | 3103.2 | 2967.6 | 100.0 | 161.1 | 6.77 | 8.08 |
| `OD_V1M_H20` | 588.8 | 755.6 | 717.8 | 57.0 | 71.2 | 8.97 | 10.71 |
| `OD_V1M_H60` | 588.8 | 755.6 | 717.8 | 100.0 | 161.1 | 6.77 | 8.08 |
| `CEO_CFO_V10K_H5` | 2332.0 | 2247.6 | 2135.0 | 42.4 | 20.6 | 10.4 | 12.42 |
| `CEO_CFO_V10K_H20` | 2332.0 | 2247.6 | 2135.0 | 100.0 | 53.7 | 6.77 | 8.08 |
| `CEO_CFO_V10K_H60` | 2332.0 | 2247.6 | 2135.0 | 100.0 | 161.1 | 6.77 | 8.08 |
| `CEO_CFO_V100K_H20` | 847.1 | 901.6 | 939.0 | 74.5 | 62.2 | 7.84 | 9.36 |
| `CEO_CFO_V100K_H60` | 847.1 | 901.6 | 939.0 | 100.0 | 161.1 | 6.77 | 8.08 |
| `CEO_CFO_V1M_H60` | 141.8 | 192.4 | 205.8 | 49.0 | 230.2 | 9.67 | 11.55 |
| `FROZEN_FV_10S_V10K_H5` | 2249.5 | 1956.8 | 1663.0 | 33.0 | 23.4 | 11.78 | 14.07 |
| `FROZEN_FV_10S_V10K_H20` | 2249.5 | 1956.8 | 1663.0 | 100.0 | 53.7 | 6.77 | 8.08 |
| `FROZEN_FV_10S_V10K_H60` | 2249.5 | 1956.8 | 1663.0 | 100.0 | 161.1 | 6.77 | 8.08 |
| `FROZEN_FV_10S_V100K_H20` | 1040.4 | 1160.0 | 1003.6 | 79.7 | 60.2 | 7.58 | 9.06 |
| `FROZEN_FV_10S_V100K_H60` | 1040.4 | 1160.0 | 1003.6 | 100.0 | 161.1 | 6.77 | 8.08 |
| `FROZEN_FV_10S_V1M_H20` | 240.4 | 337.2 | 302.6 | 24.0 | 109.6 | 13.81 | 16.49 |
| `FROZEN_FV_10S_V1M_H60` | 240.4 | 337.2 | 302.6 | 72.0 | 189.8 | 7.97 | 9.52 |

Excluded cells:

- `OD_V1M_H5`: holdout average concurrent positions 14.2 < 20
- `CEO_CFO_V100K_H5`: holdout average concurrent positions 18.6 < 20
- `CEO_CFO_V1M_H5`: holdout average concurrent positions 4.1 < 20
- `CEO_CFO_V1M_H20`: holdout average concurrent positions 16.3 < 20
- `FROZEN_FV_10S_V100K_H5`: holdout average concurrent positions 19.9 < 20
- `FROZEN_FV_10S_V1M_H5`: holdout average concurrent positions 6.0 < 20

## Power reading

Audit per-event table reproduced (bp, 5-year holdout, h=20): {'300': 110.1, '500': 85.3, '1000': 60.3, '2000': 42.6}.

The holdout tests a *portfolio*, whose noise falls with the number of concurrent positions, not with the number of events. With σ20d = 14 % and deff 1.5, the annualized MDE on invested capital is ≈ 15.1 %/yr at K = 20 concurrent positions and ≈ 6.8 %/yr at K = 100. Both exceed the 3 %/yr GO bar, so the Holm p < 0.05 leg — not the 3 % leg — is the binding GO condition. The drafted constructor therefore uses K = 100 slots and C0 = USD 100,000; the audit's K = 20 / C0 = USD 10,000 remains an owner option.

## Open decisions before sealing

- constructor slots/C0 (K=100, C0=USD 100k drafted; audit K=20, C0=USD 10k gives ~15%/yr holdout MDE)
- commission schedule of the actual paper broker
- spread floors by ADV20 bucket
