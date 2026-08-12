# Résultat — Régime discret de volatilité PRÉVUE GJR-t, overlay binaire (cycle #169)

Spécification figée dans `PREREG_gjr_calm_regime_overlay.md` (committé avant ce script). n_trials = 1. Composite exclu (SPA GJR-t non validé dessus à l'Étape C).

`position(t) = 2.0x si vol_prévue_GJR-t(t) ≤ percentile_33.33(historique expanding), 1.0x sinon`. T0=750, BURN_IN=252, REFIT_EVERY=21j, coûts 5 bps.

| Marché | Séances test. | BH Sharpe | BH Rdt | Overlay Sharpe | Overlay Rdt | Overlay MDD | % temps en régime calme (2.0x) | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| NDX (40 ans) | 9270 | +0.51 | +13204.5% | +0.52 | +31102.5% | -82.9% | 32.5% | OUI | OUI |
| S&P 500 | 13249 | +0.47 | +7821.9% | +0.46 | +13908.2% | -57.5% | 34.6% | non | OUI |
| Russell 2000 | 8779 | +0.37 | +1570.1% | +0.36 | +1722.8% | -61.4% | 16.5% | non | OUI |
| DAX | 5774 | +0.42 | +608.1% | +0.40 | +894.7% | -57.2% | 44.2% | non | OUI |

**1/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥3/4).**

**FAIL — critère pré-enregistré NON atteint.**
