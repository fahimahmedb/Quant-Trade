# Résultat — Overlay de vol-targeting estimateur Parkinson (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_Parkinson_20j(t-1), 0.0, 2.0x) — variante du #46 (écart-type close-to-close). Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +77.6% | -36.4% | +0.65 | +137.0% | -42.4% | 1.40x | OUI | OUI |
| NDX (40 ans) | 10252 | +0.53 | +25465.6% | -82.9% | +0.75 | +210744.6% | -66.5% | 1.31x | OUI | OUI |
| Russell 2000 | 9761 | +0.34 | +1666.8% | -59.9% | +0.40 | +4757.1% | -55.2% | 1.51x | OUI | OUI |
| S&P 500 | 14231 | +0.46 | +8735.1% | -56.8% | +0.56 | +97884.6% | -64.0% | 1.54x | OUI | OUI |
| DAX | 6756 | +0.24 | +325.5% | -72.7% | +0.26 | +477.1% | -69.9% | 1.42x | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
