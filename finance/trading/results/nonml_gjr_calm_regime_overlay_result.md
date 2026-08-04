# Résultat — Régime discret de volatilité PRÉVUE GJR-t, overlay binaire (cycle #169)

Spécification figée dans `PREREG_gjr_calm_regime_overlay.md` (committé avant ce script). n_trials = 1. Composite exclu (SPA GJR-t non validé dessus à l'Étape C).

`position(t) = 2.0x si vol_prévue_GJR-t(t) ≤ percentile_33.33(historique expanding), 1.0x sinon`. T0=750, BURN_IN=252, REFIT_EVERY=21j, coûts 5 bps.

| Marché | Séances test. | BH Sharpe | BH Rdt | Overlay Sharpe | Overlay Rdt | Overlay MDD | % temps en régime calme (2.0x) | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| NDX (40 ans) | 9270 | +0.51 | +3624.8% | +0.52 | +5945.3% | -82.9% | 32.5% | OUI | OUI |
| S&P 500 | 13249 | +0.47 | +3411.8% | +0.46 | +4549.9% | -57.5% | 34.6% | non | OUI |
| Russell 2000 | 8779 | +0.37 | +609.7% | +0.36 | +602.2% | -61.4% | 16.5% | non | non |
| DAX | 5774 | +0.42 | +340.4% | +0.40 | +376.4% | -57.2% | 44.2% | non | OUI |

**1/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥3/4).**

**FAIL — critère pré-enregistré NON atteint.**
