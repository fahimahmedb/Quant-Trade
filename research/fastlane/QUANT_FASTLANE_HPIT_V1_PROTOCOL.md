# `QUANT_FASTLANE_HPIT_V1` protocol — DRAFT (not sealed)

Status `DRAFT_NOT_SEALED`; `open_decisions` = []. Canonical sha256 of this draft: `sha256:b6954828f9d6ff77be4c2ae679717cdae435c9068a6da1ccc57b44e9f70120af`. Sealing requires flipping status to `FINAL_FOR_SEAL` by explicit decision, then `python3 scripts/fastlane.py seal-prereg --protocol research/fastlane/QUANT_FASTLANE_HPIT_V1_PROTOCOL.json`, then committing and pushing the sealed file (grants require it on a remote-tracking branch).

## Frozen elements

- Events: SEC Insider Transactions Data Sets, original Form 4, code P / acquired A; primary = common-equity titles, frozen footnote exclusions (plan/DRIP/fees, IPO/underwritten, conversion, private placement), exact duplicates removed, backdated accessions excluded. Unfiltered = sensitivity only.
- Entry: open of the first vendor session strictly after FILING_DATE; missing entry bar → skipped; missing exit bar → next open, else delisting treatment after 20 sessions.
- Splits: discovery 2006-01-01→2018-12-31, walk-forward 2019-01-01→2021-06-30, holdout 2021-07-01→2026-06-30 (sealed, one look).
- Return: r_ex,t = Σ w_{i,t−1}(r_{i,t} − r_SPY,t)/Σ w_{i,t−1}, buy-and-hold weights on invested capital; idle cash 0 % reported separately; alpha = 252 × mean r_ex.
- Inference: one-sided studentized moving-block bootstrap (80 sessions, B = 10,000, seed 20260924) AND fixed-b HAC t (Bartlett, b = 0.1, Kiefer–Vogelsang); both below the Holm threshold. FF5+UMD robustness only.
- Multiplicity: M declared below; DSR on discovery with N = trial-ledger count; Romano-Wolf/SPA; ≤ 3 finalists with discovery and walk-forward trial records; Holm α = 0.05. Zero finalists → NO_GO, holdout unopened.
- Constructor: K = 100 slots, C0 = USD 100,000 paper; tie-break sha256(seed|sorted accessions), never CIK.
- Frictions (frozen, not calibrated): Abdi–Ranaldo with ADV20 floors 250/120/60/30/10 bp (<0.5M/0.5–2M/2–10M/10–50M/≥50M); ADV20 < USD 100k untradeable; USD 0.0035/share, min USD 0.35; impact 1.0·σ·√(Q/ADV20); participation ≤ 0.1 % ADV20; 2× stress reported.
- Delisting by class: cash acquisition / stock merger → last trade; bankruptcy/cause −100 %; unknown −30 % (stress −100 %); vendor code→class map committed before any grant. Benchmark: SPY total return from the vendor, committed manifest, no fallback.
- Outcomes: GO (all legs), INCONCLUSIVE (GO fails, one-sided 95 % upper bound ≥ 3 %/yr), NO_GO; only GO may authorize paper sizing.

## Variant grid (M = 21)

Adequacy (outcome-blind): ≥ 50 issuer-days/yr in every split and ≥ 20 average concurrent holdout positions. Disclosure: these counts include holdout-period counts (no outcomes).

| Variant | Disc/yr | WF/yr | Holdout/yr | Avg concurrent (K=100) | Per-event MDE (bp) | Portfolio MDE, TE 8% (%/yr) | Holm-step (%/yr) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `OD_V10K_H5` | 7538.5 | 6608.4 | 5981.8 | 100.0 | 13.4 | 11.18 | 13.35 |
| `OD_V10K_H20` | 7538.5 | 6608.4 | 5981.8 | 100.0 | 53.7 | 11.18 | 13.35 |
| `OD_V10K_H60` | 7538.5 | 6608.4 | 5981.8 | 100.0 | 161.1 | 11.18 | 13.35 |
| `OD_V100K_H5` | 2580.3 | 2762.4 | 2618.6 | 52.0 | 18.6 | 12.93 | 15.45 |
| `OD_V100K_H20` | 2580.3 | 2762.4 | 2618.6 | 100.0 | 53.7 | 11.18 | 13.35 |
| `OD_V100K_H60` | 2580.3 | 2762.4 | 2618.6 | 100.0 | 161.1 | 11.18 | 13.35 |
| `OD_V1M_H20` | 500.2 | 626.0 | 601.2 | 47.7 | 77.8 | 13.23 | 15.81 |
| `OD_V1M_H60` | 500.2 | 626.0 | 601.2 | 100.0 | 161.1 | 11.18 | 13.35 |
| `CEO_CFO_V10K_H5` | 2090.2 | 2035.2 | 1912.8 | 38.0 | 21.8 | 14.14 | 16.88 |
| `CEO_CFO_V10K_H20` | 2090.2 | 2035.2 | 1912.8 | 100.0 | 53.7 | 11.18 | 13.35 |
| `CEO_CFO_V10K_H60` | 2090.2 | 2035.2 | 1912.8 | 100.0 | 161.1 | 11.18 | 13.35 |
| `CEO_CFO_V100K_H20` | 744.4 | 786.8 | 823.6 | 65.4 | 66.4 | 12.22 | 14.59 |
| `CEO_CFO_V100K_H60` | 744.4 | 786.8 | 823.6 | 100.0 | 161.1 | 11.18 | 13.35 |
| `CEO_CFO_V1M_H60` | 123.7 | 153.6 | 172.2 | 41.0 | 251.7 | 13.82 | 16.5 |
| `FROZEN_FV_10S_V10K_H5` | 1959.0 | 1676.0 | 1425.8 | 28.3 | 25.2 | 15.53 | 18.54 |
| `FROZEN_FV_10S_V10K_H20` | 1959.0 | 1676.0 | 1425.8 | 100.0 | 53.7 | 11.18 | 13.35 |
| `FROZEN_FV_10S_V10K_H60` | 1959.0 | 1676.0 | 1425.8 | 100.0 | 161.1 | 11.18 | 13.35 |
| `FROZEN_FV_10S_V100K_H20` | 899.0 | 1001.2 | 861.0 | 68.3 | 65.0 | 12.09 | 14.44 |
| `FROZEN_FV_10S_V100K_H60` | 899.0 | 1001.2 | 861.0 | 100.0 | 161.1 | 11.18 | 13.35 |
| `FROZEN_FV_10S_V1M_H60` | 198.6 | 264.4 | 246.2 | 58.6 | 210.5 | 12.54 | 14.98 |
| `FROZEN_FV_10S_V0_H20` | 2306.4 | 1849.2 | 1552.6 | 100.0 | 53.7 | 11.18 | 13.35 |

Excluded cells:

- `OD_V1M_H5`: holdout average concurrent positions 11.9 < 20
- `CEO_CFO_V100K_H5`: holdout average concurrent positions 16.3 < 20
- `CEO_CFO_V1M_H5`: holdout average concurrent positions 3.4 < 20
- `CEO_CFO_V1M_H20`: holdout average concurrent positions 13.7 < 20
- `FROZEN_FV_10S_V100K_H5`: holdout average concurrent positions 17.1 < 20
- `FROZEN_FV_10S_V1M_H5`: holdout average concurrent positions 4.9 < 20
- `FROZEN_FV_10S_V1M_H20`: holdout average concurrent positions 19.5 < 20

## Power reading

Audit per-event table reproduced (bp, 5-year holdout, h=20): {'300': 110.1, '500': 85.3, '1000': 60.3, '2000': 42.6}.

The holdout tests a portfolio. With σ20d = 14 %, deff 1.5 and 8 %/yr tracking error vs SPY, the annualized MDE on invested capital is ≈ 17.55 %/yr at K = 20 and ≈ 11.18 %/yr at K = 100 (13.35 %/yr at the first Holm step). All exceed the 3 %/yr GO bar: the significance legs bind, and a true 3–10 %/yr alpha will most likely read INCONCLUSIVE rather than GO.
