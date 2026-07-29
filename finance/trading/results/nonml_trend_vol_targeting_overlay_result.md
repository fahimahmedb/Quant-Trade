# Résultat — Overlay combiné tendance + vol-targeting (pré-enregistré, combinaison #37+#46)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si tendance haussière (≥95% du plus haut 252j), sinon 1.0x. Échantillon testable = à partir de la 253e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 998 | +1.00 | +113.4% | -24.3% | +1.00 | +130.3% | -26.9% | 1.19x | non | OUI |
| NDX (40 ans) | 10020 | +0.52 | +5429.9% | -82.9% | +0.55 | +9213.2% | -82.9% | 1.21x | OUI | OUI |
| Russell 2000 | 9529 | +0.37 | +739.6% | -59.9% | +0.40 | +1169.2% | -61.2% | 1.25x | OUI | OUI |
| S&P 500 | 13999 | +0.46 | +3436.7% | -56.8% | +0.52 | +12506.4% | -58.9% | 1.44x | OUI | OUI |
| DAX | 6524 | +0.23 | +93.1% | -69.1% | +0.25 | +120.0% | -69.1% | 1.27x | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
