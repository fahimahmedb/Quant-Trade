# Résultat — Overlay vol-targeting gaté par la profondeur de drawdown glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si le drawdown_60j(t-1) est ≥ sa médiane glissante 252j (drawdown moins profond que la norme récente), sinon 1.0x. Échantillon testable à partir de la 312e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.11 | +137.2% | -24.3% | +1.03 | +144.3% | -27.1% | 41.9% | 1.17x | non | OUI |
| NDX (40 ans) | +0.52 | +20561.6% | -82.9% | +0.53 | +32477.8% | -82.9% | 36.2% | 1.18x | OUI | OUI |
| Russell 2000 | +0.37 | +1967.4% | -59.9% | +0.43 | +4439.7% | -61.6% | 39.4% | 1.23x | OUI | OUI |
| S&P 500 | +0.45 | +7415.3% | -56.8% | +0.43 | +10984.1% | -61.6% | 45.6% | 1.32x | non | OUI |
| DAX | +0.23 | +272.7% | -67.6% | +0.20 | +247.9% | -69.4% | 38.7% | 1.22x | non | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
