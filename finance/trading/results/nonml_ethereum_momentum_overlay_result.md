# Résultat — Momentum de l'Ethereum (CBETHUSD, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ETHmom_lag(t)=log(ETH(t-1)/ETH(t-1-21)) est dans son tercile expanding le plus BAS (repli marqué de l'Ethereum), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 38.0% | +0.52 | +77.9% | -36.4% | +0.76 | +90.1% | -30.6% | OUI | OUI |
| NDX (40 ans) | 2529 | 32.2% | +0.84 | +574.4% | -35.6% | +0.97 | +480.8% | -31.5% | OUI | non |
| Russell 2000 | 2529 | 32.2% | +0.40 | +157.9% | -43.1% | +0.46 | +143.3% | -34.4% | OUI | non |
| S&P 500 | 2529 | 32.2% | +0.71 | +262.7% | -33.9% | +0.85 | +233.4% | -26.9% | OUI | non |
| DAX | 2554 | 32.6% | +0.52 | +162.3% | -38.8% | +0.49 | +113.1% | -31.9% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
