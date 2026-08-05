# Résultat — Overlay de vol-targeting estimateur ATR (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_ATR(t-1), 0.0, 2.0x) — vol_ATR = (ATR_14j Wilder / close) × √252. Échantillon testable = à partir de la 16e séance (lissage de Wilder n=14 + décalage d'un jour).

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1235 | +0.52 | +56.8% | -36.4% | +0.56 | +44.5% | -27.1% | 0.81x | OUI | non |
| NDX (40 ans) | 10257 | +0.53 | +6470.0% | -82.9% | +0.73 | +5885.3% | -47.4% | 0.82x | OUI | non |
| Russell 2000 | 9766 | +0.34 | +592.2% | -59.9% | +0.43 | +838.8% | -43.4% | 1.10x | OUI | OUI |
| S&P 500 | 14236 | +0.46 | +3511.0% | -56.8% | +0.54 | +4840.6% | -47.3% | 1.07x | OUI | OUI |
| DAX | 6761 | +0.24 | +119.0% | -72.7% | +0.27 | +120.4% | -52.1% | 0.88x | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
