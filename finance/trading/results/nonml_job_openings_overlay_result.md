# Résultat — Offres d'emploi US (FRED JTSJOL, JOLTS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si JOLGrowth_lag(t-1)=log(JTSJOL(t)/JTSJOL(t-12)) est dans son tercile expanding le plus BAS (contraction des offres d'emploi = défavorable), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 65.0% | +0.52 | +57.6% | -36.4% | +0.53 | +43.6% | -24.3% | OUI | non |
| NDX (40 ans) | 6148 | 30.3% | +0.52 | +894.8% | -53.7% | +0.48 | +505.6% | -42.7% | non | non |
| Russell 2000 | 6148 | 30.3% | +0.31 | +199.9% | -59.9% | +0.31 | +177.6% | -42.7% | OUI | non |
| S&P 500 | 6148 | 30.3% | +0.41 | +328.5% | -56.8% | +0.42 | +254.4% | -39.0% | OUI | non |
| DAX | 6204 | 30.5% | +0.29 | +169.9% | -59.7% | +0.26 | +120.6% | -57.7% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
