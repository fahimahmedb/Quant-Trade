# `QUANT_FASTLANE_HPIT_V1` protocol — DRAFT (not sealed)

Status `DRAFT_NOT_SEALED`; `open_decisions` = []. Canonical sha256 of this draft: `sha256:726b0db2e74d619943e30a7ffb3e0371df9c2893d28d17cbe91dd5e9024b666e`. Sealing requires flipping status to `FINAL_FOR_SEAL` by explicit decision, then `python3 scripts/fastlane.py seal-prereg --protocol research/fastlane/QUANT_FASTLANE_HPIT_V1_PROTOCOL.json`, then committing and pushing the sealed file (grants require it in a branch the remote advertises, in a complete clone: run `git fetch --unshallow` first if the clone is shallow).

## Frozen elements

- Events: SEC Insider Transactions Data Sets, original Form 4, code P / acquired A; primary = common-equity titles, frozen footnote exclusions (plan/DRIP/fees, IPO/underwritten, conversion, private placement), exact duplicates removed, backdated accessions excluded. Unfiltered = sensitivity only.
- Entry: open of the first vendor session strictly after FILING_DATE; missing entry bar → skipped; missing exit bar → next open, else delisting treatment after 20 sessions.
- Splits: discovery 2006-01-01→2018-12-31, walk-forward 2019-01-01→2021-06-30, holdout 2021-07-01→2026-06-30 (sealed, one look).
- Return: r_ex,t = Σ w_{i,t−1}(r_{i,t} − r_SPY,t)/Σ w_{i,t−1}, buy-and-hold weights on invested capital; idle cash 0 % reported separately; alpha = 252 × mean r_ex.
- Inference: one-sided studentized moving-block bootstrap (80 sessions, B = 10,000, seed 20260924) AND fixed-b HAC t (Bartlett, b = 0.1, Kiefer–Vogelsang); both below the Holm threshold. FF5+UMD robustness only.
- Multiplicity: M declared below; N_trials = max(M_declared, trial-ledger evaluations) for DSR and the Holm context; ALL declared variants need discovery trial records before a holdout request; Romano-Wolf/SPA; ≤ 3 finalists with discovery and walk-forward trial records; Holm α = 0.05. Zero finalists → NO_GO, holdout unopened.
- Seed robustness (reporting only, never gating): seeds [20260925, 20260926, 20260927, 20260928, 20260929].
- Constructor: K = 100 slots, C0 = USD 100,000 paper; tie-break sha256(seed|sorted accessions), never CIK.
- Frictions (frozen, not calibrated): Abdi–Ranaldo with ADV20 floors 250/120/60/30/10 bp (<0.5M/0.5–2M/2–10M/10–50M/≥50M); ADV20 < USD 100k untradeable; USD 0.0035/share, min USD 0.35; impact 1.0·σ·√(Q/ADV20); participation ≤ 0.1 % ADV20; 2× stress reported.
- Delisting by class: cash acquisition / stock merger → last trade; bankruptcy/cause −100 %; unknown −30 % (stress −100 %); vendor code→class map committed before any grant. Benchmark: SPY total return from the vendor, committed manifest, no fallback.
- Outcomes: GO (all legs), INCONCLUSIVE (GO fails, one-sided 95 % upper bound ≥ 3 %/yr), NO_GO; only GO may authorize paper sizing.
- Anchoring: grants need a complete (non-shallow) clone and the seal, request and vendor manifests contained in a branch the real remote advertises; the request pins the seal commit. OWNER ACTIONS: branch protection (no force-push/deletion) and an external record of the seal and request commit hashes. Residual risk: a force-push that rewrites only the request commit is caught only by those owner actions.

## Variant grid (M = 22)

Adequacy (outcome-blind): ≥ 50 issuer-days/yr in every split and ≥ 20 average concurrent holdout positions. Disclosure: these counts include holdout-period counts (no outcomes).

| Variant | Disc/yr | WF/yr | Holdout/yr | Avg concurrent (K=100) | Per-event MDE (bp) | Portfolio MDE, TE 8% (%/yr) | Holm-step (%/yr) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `OD_V10K_H5` | 7945.8 | 6950.0 | 6277.0 | 100.0 | 13.4 | 11.18 | 13.35 |
| `OD_V10K_H20` | 7945.8 | 6950.0 | 6277.0 | 100.0 | 53.7 | 11.18 | 13.35 |
| `OD_V10K_H60` | 7945.8 | 6950.0 | 6277.0 | 100.0 | 161.1 | 11.18 | 13.35 |
| `OD_V100K_H5` | 2759.4 | 2916.0 | 2771.6 | 55.0 | 18.1 | 12.74 | 15.22 |
| `OD_V100K_H20` | 2759.4 | 2916.0 | 2771.6 | 100.0 | 53.7 | 11.18 | 13.35 |
| `OD_V100K_H60` | 2759.4 | 2916.0 | 2771.6 | 100.0 | 161.1 | 11.18 | 13.35 |
| `OD_V1M_H20` | 540.5 | 667.6 | 637.2 | 50.6 | 75.5 | 13.03 | 15.56 |
| `OD_V1M_H60` | 540.5 | 667.6 | 637.2 | 100.0 | 161.1 | 11.18 | 13.35 |
| `CEO_CFO_V10K_H5` | 2212.2 | 2125.2 | 2003.8 | 39.8 | 21.3 | 13.94 | 16.65 |
| `CEO_CFO_V10K_H20` | 2212.2 | 2125.2 | 2003.8 | 100.0 | 53.7 | 11.18 | 13.35 |
| `CEO_CFO_V10K_H60` | 2212.2 | 2125.2 | 2003.8 | 100.0 | 161.1 | 11.18 | 13.35 |
| `CEO_CFO_V100K_H20` | 799.0 | 831.2 | 873.6 | 69.3 | 64.5 | 12.05 | 14.39 |
| `CEO_CFO_V100K_H60` | 799.0 | 831.2 | 873.6 | 100.0 | 161.1 | 11.18 | 13.35 |
| `CEO_CFO_V1M_H60` | 130.5 | 162.0 | 178.8 | 42.6 | 247.0 | 13.67 | 16.32 |
| `FROZEN_FV_10S_V10K_H5` | 2086.7 | 1791.6 | 1524.4 | 30.2 | 24.4 | 15.18 | 18.14 |
| `FROZEN_FV_10S_V10K_H20` | 2086.7 | 1791.6 | 1524.4 | 100.0 | 53.7 | 11.18 | 13.35 |
| `FROZEN_FV_10S_V10K_H60` | 2086.7 | 1791.6 | 1524.4 | 100.0 | 161.1 | 11.18 | 13.35 |
| `FROZEN_FV_10S_V100K_H20` | 962.3 | 1062.0 | 915.4 | 72.7 | 63.0 | 11.92 | 14.24 |
| `FROZEN_FV_10S_V100K_H60` | 962.3 | 1062.0 | 915.4 | 100.0 | 161.1 | 11.18 | 13.35 |
| `FROZEN_FV_10S_V1M_H20` | 214.0 | 283.6 | 261.4 | 20.7 | 117.9 | 17.32 | 20.68 |
| `FROZEN_FV_10S_V1M_H60` | 214.0 | 283.6 | 261.4 | 62.2 | 204.3 | 12.36 | 14.76 |
| `FROZEN_FV_10S_V0_H20` | 2453.4 | 1991.2 | 1671.4 | 100.0 | 53.7 | 11.18 | 13.35 |

Excluded cells:

- `OD_V1M_H5`: holdout average concurrent positions 12.6 < 20
- `CEO_CFO_V100K_H5`: holdout average concurrent positions 17.3 < 20
- `CEO_CFO_V1M_H5`: holdout average concurrent positions 3.5 < 20
- `CEO_CFO_V1M_H20`: holdout average concurrent positions 14.2 < 20
- `FROZEN_FV_10S_V100K_H5`: holdout average concurrent positions 18.2 < 20
- `FROZEN_FV_10S_V1M_H5`: holdout average concurrent positions 5.2 < 20

## Power reading

Audit per-event table reproduced (bp, 5-year holdout, h=20): {'300': 110.1, '500': 85.3, '1000': 60.3, '2000': 42.6}.

The holdout tests a portfolio. With σ20d = 14 %, deff 1.5 and 8 %/yr tracking error vs SPY, the annualized MDE on invested capital is ≈ 17.55 %/yr at K = 20 and ≈ 11.18 %/yr at K = 100 (13.35 %/yr at the first Holm step). All exceed the 3 %/yr GO bar: the significance legs bind, and a true 3–10 %/yr alpha will most likely read INCONCLUSIVE rather than GO.
