# Résultat — Overlay vol-targeting gaté par la largeur de bande de Bollinger glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si la largeur de Bollinger (4×écart-type_prix_20j/moyenne_prix_20j)(t-1) est ≤ sa médiane glissante 252j, sinon 1.0x. Échantillon testable à partir de la 272e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.87 | +87.3% | -24.3% | +0.87 | +99.6% | -25.3% | 41.2% | 1.15x | OUI | OUI |
| NDX (40 ans) | +0.51 | +5237.3% | -82.9% | +0.52 | +6634.1% | -82.9% | 35.5% | 1.17x | OUI | OUI |
| Russell 2000 | +0.37 | +730.6% | -59.9% | +0.34 | +612.6% | -60.8% | 41.0% | 1.23x | non | non |
| S&P 500 | +0.46 | +3328.4% | -56.8% | +0.42 | +3500.2% | -67.7% | 47.1% | 1.34x | non | OUI |
| DAX | +0.23 | +98.5% | -67.6% | +0.19 | +47.2% | -69.4% | 40.8% | 1.22x | non | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
