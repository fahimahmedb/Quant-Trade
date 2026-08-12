# Résultat — Mécanisme hiérarchique gaté (#47) avec volatilité PRÉVUE GJR-t (cycle #168)

Spécification figée dans `PREREG_gjr_trend_gated_vol_managed.md` (committé avant ce script). n_trials = 1. Composite exclu (SPA GJR-t non validé dessus à l'Étape C).

`position(t) = clip(20% / vol_prévue_GJR-t(t), 1.0, 2.0x)` si tendance haussière (52w-high indice, seuil 95%), sinon 1.0x. T0=750, REFIT_EVERY=21j, coûts 5 bps.

| Marché | Séances test. | BH Sharpe | BH Rdt | Overlay Sharpe | Overlay Rdt | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| NDX (40 ans) | 9522 | +0.52 | +16652.5% | +0.53 | +23024.9% | -82.9% | 1.15x | OUI | OUI |
| S&P 500 | 13501 | +0.44 | +6325.6% | +0.47 | +21414.9% | -58.5% | 1.41x | OUI | OUI |
| Russell 2000 | 9031 | +0.39 | +2014.8% | +0.38 | +2576.2% | -62.1% | 1.24x | non | OUI |
| DAX | 6026 | +0.43 | +779.1% | +0.42 | +951.1% | -56.8% | 1.24x | non | OUI |

**2/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥3/4, raisonnement au PREREG §4).**

**FAIL — critère pré-enregistré NON atteint.**
