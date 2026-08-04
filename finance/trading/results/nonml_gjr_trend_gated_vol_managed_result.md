# Résultat — Mécanisme hiérarchique gaté (#47) avec volatilité PRÉVUE GJR-t (cycle #168)

Spécification figée dans `PREREG_gjr_trend_gated_vol_managed.md` (committé avant ce script). n_trials = 1. Composite exclu (SPA GJR-t non validé dessus à l'Étape C).

`position(t) = clip(20% / vol_prévue_GJR-t(t), 1.0, 2.0x)` si tendance haussière (52w-high indice, seuil 95%), sinon 1.0x. T0=750, REFIT_EVERY=21j, coûts 5 bps.

| Marché | Séances test. | BH Sharpe | BH Rdt | Overlay Sharpe | Overlay Rdt | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| NDX (40 ans) | 9522 | +0.52 | +4553.2% | +0.53 | +5523.7% | -82.9% | 1.15x | OUI | OUI |
| S&P 500 | 13501 | +0.44 | +2714.7% | +0.47 | +6335.3% | -58.5% | 1.41x | OUI | OUI |
| Russell 2000 | 9031 | +0.39 | +791.2% | +0.38 | +854.4% | -62.1% | 1.24x | non | OUI |
| DAX | 6026 | +0.43 | +410.6% | +0.42 | +445.1% | -56.8% | 1.24x | non | OUI |

**2/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥3/4, raisonnement au PREREG §4).**

**FAIL — critère pré-enregistré NON atteint.**
