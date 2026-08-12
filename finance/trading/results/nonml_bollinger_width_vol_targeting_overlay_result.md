# Résultat — Overlay vol-targeting gaté par la largeur de bande de Bollinger glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si la largeur de Bollinger (4×écart-type_prix_20j/moyenne_prix_20j)(t-1) est ≤ sa médiane glissante 252j, sinon 1.0x. Échantillon testable à partir de la 272e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.87 | +104.3% | -24.3% | +0.87 | +122.4% | -25.3% | 41.2% | 1.15x | OUI | OUI |
| NDX (40 ans) | +0.51 | +20605.1% | -82.9% | +0.52 | +31506.1% | -82.9% | 35.5% | 1.17x | OUI | OUI |
| Russell 2000 | +0.37 | +1891.0% | -59.9% | +0.34 | +1976.5% | -60.8% | 41.0% | 1.23x | non | OUI |
| S&P 500 | +0.46 | +7789.5% | -56.8% | +0.42 | +11756.2% | -67.7% | 47.1% | 1.34x | non | OUI |
| DAX | +0.23 | +279.6% | -67.6% | +0.19 | +229.4% | -69.4% | 40.8% | 1.22x | non | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
