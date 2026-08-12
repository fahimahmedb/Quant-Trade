# Résultat — Direction du changement de la prévision GJR-t, overlay binaire (cycle #170)

Spécification figée dans `PREREG_gjr_vol_forecast_momentum_overlay.md` (committé avant ce script). n_trials = 1. Composite exclu (SPA GJR-t non validé dessus à l'Étape C).

`delta(t) = vol_prévue_GJR-t(t) - vol_prévue_GJR-t(t-21)` ; `position(t) = 2.0x si delta(t) < 0, 1.0x sinon`. T0=750, REFIT_EVERY=21j, coûts 5 bps.

| Marché | Séances test. | BH Sharpe | BH Rdt | Overlay Sharpe | Overlay Rdt | Overlay MDD | % temps en décélération (2.0x) | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| NDX (40 ans) | 9501 | +0.52 | +16569.2% | +0.52 | +213565.1% | -95.5% | 54.0% | OUI | OUI |
| S&P 500 | 13480 | +0.44 | +6223.9% | +0.41 | +31216.5% | -84.5% | 56.2% | non | OUI |
| Russell 2000 | 9010 | +0.40 | +2239.3% | +0.35 | +6170.8% | -83.2% | 52.3% | non | OUI |
| DAX | 6005 | +0.41 | +704.1% | +0.37 | +1531.2% | -70.6% | 54.4% | non | OUI |

**1/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥3/4).**

**FAIL — critère pré-enregistré NON atteint.**
