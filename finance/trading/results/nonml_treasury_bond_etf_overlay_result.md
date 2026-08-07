# Résultat — Momentum de l'ETF obligataire TLT (log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si TLTmom_lag(t)=log(TLT(t-1)/TLT(t-1-21)) est dans son tercile expanding le plus HAUT (hausse marquée de TLT, flight-to-quality obligataire), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 35.6% | +0.52 | +56.8% | -36.4% | +0.22 | +12.1% | -39.0% | non | non |
| NDX (40 ans) | 6004 | 31.1% | +0.64 | +1607.2% | -53.7% | +0.51 | +545.3% | -52.6% | non | non |
| Russell 2000 | 6004 | 31.1% | +0.35 | +276.1% | -59.9% | +0.25 | +108.2% | -63.1% | non | non |
| S&P 500 | 6004 | 31.1% | +0.47 | +434.3% | -56.8% | +0.32 | +141.4% | -60.1% | non | non |
| DAX | 6059 | 31.2% | +0.37 | +288.0% | -54.8% | +0.33 | +182.9% | -49.1% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
