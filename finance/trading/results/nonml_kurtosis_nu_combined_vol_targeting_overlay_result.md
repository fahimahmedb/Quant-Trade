# Résultat — Overlay vol-targeting gaté par la conjonction (ET) kurtosis + ν Student-t (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si la porte kurtosis (#219) ET la porte ν Student-t (#237) sont TOUTES DEUX actives, sinon 1.0x. Échantillon testable à partir de la 504e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte ET active | %j kurt seule | %j ν seul | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.02 | +73.6% | -24.3% | +1.06 | +82.7% | -24.3% | 19.6% | 29.0% | 26.8% | 1.07x | OUI | OUI |
| NDX (40 ans) | +0.49 | +3669.6% | -82.9% | +0.52 | +5556.2% | -82.9% | 21.3% | 52.3% | 48.0% | 1.09x | OUI | OUI |
| Russell 2000 | +0.35 | +591.6% | -59.9% | +0.36 | +669.7% | -60.0% | 26.5% | 51.4% | 50.0% | 1.14x | OUI | OUI |
| S&P 500 | +0.45 | +3109.4% | -56.8% | +0.46 | +4750.0% | -61.5% | 35.0% | 53.6% | 47.9% | 1.21x | OUI | OUI |
| DAX | +0.30 | +189.5% | -59.7% | +0.26 | +129.7% | -59.7% | 27.3% | 55.8% | 50.4% | 1.12x | non | non |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
