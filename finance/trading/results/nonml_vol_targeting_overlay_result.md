# Résultat — Overlay de vol-targeting continu (pré-enregistré, règle renforcée)

Position(t) = clip(15% / vol_réalisée_20j(t-1), 0.0, 2.0x). Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +77.6% | -36.4% | +0.58 | +59.9% | -24.8% | 0.83x | OUI | non |
| NDX (40 ans) | 10252 | +0.53 | +25465.6% | -82.9% | +0.73 | +13121.3% | -48.3% | 0.86x | OUI | non |
| Russell 2000 | 9761 | +0.34 | +1666.8% | -59.9% | +0.42 | +1276.8% | -40.3% | 1.05x | OUI | non |
| S&P 500 | 14231 | +0.46 | +8735.1% | -56.8% | +0.51 | +10463.0% | -52.0% | 1.22x | OUI | OUI |
| DAX | 6756 | +0.24 | +325.5% | -72.7% | +0.22 | +159.3% | -56.5% | 0.94x | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
