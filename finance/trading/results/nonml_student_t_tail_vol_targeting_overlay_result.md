# Résultat — Overlay vol-targeting gaté par le ν glissant (MLE Student-t) (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si ν(t) (MLE Student-t, fenêtre 252j, ré-estimé tous les 21j) est ≥ sa médiane glissante 252j, sinon 1.0x. Échantillon testable à partir de la 504e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.02 | +73.6% | -24.3% | +1.05 | +82.1% | -24.3% | 20.2% | 1.07x | OUI | OUI |
| NDX (40 ans) | +0.49 | +3669.6% | -82.9% | +0.54 | +6982.0% | -82.9% | 25.9% | 1.12x | OUI | OUI |
| Russell 2000 | +0.35 | +591.6% | -59.9% | +0.36 | +735.5% | -60.0% | 32.5% | 1.17x | OUI | OUI |
| S&P 500 | +0.45 | +3109.4% | -56.8% | +0.46 | +4881.0% | -60.9% | 41.6% | 1.26x | OUI | OUI |
| DAX | +0.30 | +189.5% | -59.7% | +0.26 | +130.1% | -59.7% | 32.4% | 1.15x | non | non |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
