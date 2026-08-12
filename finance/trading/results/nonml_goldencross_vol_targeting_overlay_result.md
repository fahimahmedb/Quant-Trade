# Résultat — Overlay vol-targeting gaté par le golden cross (pré-enregistré, combinaison #34+#46)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si SMA50 > SMA200 (golden cross), sinon 1.0x. Échantillon testable = à partir de la 201e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.79 | +110.3% | -24.3% | +0.78 | +128.4% | -27.5% | 55.4% | 1.20x | non | OUI |
| NDX (40 ans) | +0.51 | +19772.5% | -82.9% | +0.52 | +37271.6% | -82.9% | 48.8% | 1.22x | OUI | OUI |
| Russell 2000 | +0.37 | +1877.9% | -59.9% | +0.34 | +2189.5% | -61.0% | 54.2% | 1.31x | non | OUI |
| S&P 500 | +0.47 | +8773.7% | -56.8% | +0.54 | +67779.0% | -58.9% | 66.8% | 1.46x | OUI | OUI |
| DAX | +0.21 | +241.7% | -70.4% | +0.22 | +328.7% | -72.0% | 53.4% | 1.29x | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
