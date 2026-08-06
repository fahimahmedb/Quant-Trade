# Résultat — Overlay défensif durée du drawdown (pré-enregistré, règle renforcée)

`position(t) = 0.5x` si duration(t-1) (séances depuis le dernier plus haut glissant) est dans son tercile expanding le plus haut, `1,0x` sinon. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 49.1% | +0.52 | +57.6% | -36.4% | +0.63 | +58.4% | -24.3% | OUI | OUI |
| NDX (40 ans) | 10272 | 49.4% | +0.53 | +6599.5% | -82.9% | +0.53 | +3293.7% | -63.3% | OUI | non |
| Russell 2000 | 9781 | 42.7% | +0.34 | +602.0% | -59.9% | +0.32 | +336.8% | -43.1% | non | non |
| S&P 500 | 14251 | 35.8% | +0.45 | +3369.2% | -56.8% | +0.43 | +1975.9% | -56.9% | non | non |
| DAX | 6776 | 36.7% | +0.25 | +130.5% | -72.7% | +0.27 | +134.9% | -54.9% | OUI | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
