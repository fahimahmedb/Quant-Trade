# Résultat — Overlay vol-targeting gaté par double porte tendance+vol faible (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si tendance haussière (≥95% du plus haut 252j) ET vol réalisée sous sa médiane glissante 252j, sinon 1.0x.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.02 | +73.6% | -24.3% | +0.95 | +78.7% | -26.9% | 45.6% | 1.22x | non | OUI |
| NDX (40 ans) | +0.49 | +3669.6% | -82.9% | +0.49 | +4533.1% | -82.9% | 30.1% | 1.17x | OUI | OUI |
| Russell 2000 | +0.35 | +591.6% | -59.9% | +0.35 | +655.3% | -60.6% | 29.2% | 1.18x | OUI | OUI |
| S&P 500 | +0.45 | +3109.4% | -56.8% | +0.47 | +6094.3% | -58.4% | 38.5% | 1.32x | OUI | OUI |
| DAX | +0.30 | +189.5% | -59.7% | +0.30 | +190.8% | -59.7% | 34.1% | 1.24x | non | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
