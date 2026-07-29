# Résultat — Overlay de vol-targeting gaté par le calendrier (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si fenêtre ToM∪Halloween active, sinon 1.0x. Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +56.5% | -36.4% | +0.51 | +59.3% | -38.0% | 1.12x | non | OUI |
| NDX (40 ans) | 10252 | +0.53 | +6416.7% | -82.9% | +0.60 | +16780.5% | -82.9% | 1.17x | OUI | OUI |
| Russell 2000 | 9761 | +0.34 | +610.3% | -59.9% | +0.43 | +1681.3% | -59.8% | 1.25x | OUI | OUI |
| S&P 500 | 14231 | +0.46 | +3696.8% | -56.8% | +0.55 | +18467.4% | -58.1% | 1.36x | OUI | OUI |
| DAX | 6756 | +0.24 | +116.5% | -72.7% | +0.27 | +168.7% | -73.3% | 1.22x | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
