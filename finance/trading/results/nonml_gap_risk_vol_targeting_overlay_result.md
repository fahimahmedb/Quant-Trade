# Résultat — Overlay vol-targeting gaté par le risque de gap d'ouverture (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si le risque de gap moyen 20j est SOUS sa médiane glissante 252j (régime « calme »), sinon 1.0x. Échantillon testable = à partir de la 253e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.00 | +113.4% | -24.3% | +1.00 | +130.7% | -27.2% | 44.3% | 1.18x | non | OUI |
| NDX (40 ans) | +0.52 | +5429.9% | -82.9% | +0.55 | +9653.4% | -82.9% | 37.2% | 1.18x | OUI | OUI |
| Russell 2000 | +0.37 | +739.6% | -59.9% | +0.36 | +741.8% | -60.0% | 39.3% | 1.22x | non | OUI |
| S&P 500 | +0.46 | +3436.7% | -56.8% | +0.49 | +8172.9% | -58.1% | 46.2% | 1.32x | OUI | OUI |
| DAX | +0.23 | +93.1% | -69.1% | +0.19 | +53.4% | -70.0% | 38.4% | 1.23x | non | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
