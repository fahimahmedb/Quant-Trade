# Résultat — Overlay de vol-targeting continu, cible 20% (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 0.0, 2.0x) — variante du #43 (vol cible 15%). Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +77.6% | -36.4% | +0.60 | +90.1% | -31.6% | 1.10x | OUI | OUI |
| NDX (40 ans) | 10252 | +0.53 | +25465.6% | -82.9% | +0.73 | +60397.8% | -58.5% | 1.12x | OUI | OUI |
| Russell 2000 | 9761 | +0.34 | +1666.8% | -59.9% | +0.40 | +2376.9% | -49.7% | 1.30x | OUI | OUI |
| S&P 500 | 14231 | +0.46 | +8735.1% | -56.8% | +0.53 | +48280.1% | -62.2% | 1.51x | OUI | OUI |
| DAX | 6756 | +0.24 | +325.5% | -72.7% | +0.23 | +274.9% | -67.1% | 1.22x | non | non |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
