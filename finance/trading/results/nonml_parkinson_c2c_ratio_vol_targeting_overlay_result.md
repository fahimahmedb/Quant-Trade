# Résultat — Overlay vol-targeting gaté par le ratio vol Parkinson / vol close-to-close (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_close-to-close_20j(t-1), 1.0, 2.0x) si ratio(vol_Parkinson_20j / vol_close-to-close_20j)(t-1) est ≥ sa médiane glissante 252j, sinon 1.0x. Échantillon testable à partir de la 272e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.87 | +87.3% | -24.3% | +0.77 | +82.1% | -27.2% | 35.3% | 1.15x | non | non |
| NDX (40 ans) | +0.51 | +5237.3% | -82.9% | +0.52 | +6638.1% | -82.9% | 34.4% | 1.18x | OUI | OUI |
| Russell 2000 | +0.37 | +730.6% | -59.9% | +0.34 | +596.0% | -61.1% | 39.3% | 1.23x | non | non |
| S&P 500 | +0.46 | +3328.4% | -56.8% | +0.42 | +3513.3% | -63.3% | 44.2% | 1.33x | non | OUI |
| DAX | +0.23 | +98.5% | -67.6% | +0.21 | +74.5% | -69.1% | 37.0% | 1.22x | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
