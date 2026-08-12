# Résultat — Overlay de vol-targeting estimateur ATR (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_ATR(t-1), 0.0, 2.0x) — vol_ATR = (ATR_14j Wilder / close) × √252. Échantillon testable = à partir de la 16e séance (lissage de Wilder n=14 + décalage d'un jour).

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1235 | +0.52 | +78.0% | -36.4% | +0.56 | +53.4% | -27.1% | 0.81x | OUI | non |
| NDX (40 ans) | 10257 | +0.53 | +25680.1% | -82.9% | +0.73 | +9637.4% | -47.4% | 0.82x | OUI | non |
| Russell 2000 | 9766 | +0.34 | +1622.1% | -59.9% | +0.43 | +1525.3% | -43.4% | 1.10x | OUI | non |
| S&P 500 | 14236 | +0.46 | +8305.0% | -56.8% | +0.54 | +8997.5% | -47.3% | 1.07x | OUI | OUI |
| DAX | 6761 | +0.24 | +330.5% | -72.7% | +0.27 | +197.4% | -52.1% | 0.88x | OUI | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
