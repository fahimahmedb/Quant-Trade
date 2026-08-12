# Résultat — Momentum de l'ETF obligataire TLT (log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si TLTmom_lag(t)=log(TLT(t-1)/TLT(t-1-21)) est dans son tercile expanding le plus HAUT (hausse marquée de TLT, flight-to-quality obligataire), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 35.6% | +0.52 | +77.9% | -36.4% | +0.22 | +23.9% | -39.0% | non | non |
| NDX (40 ans) | 6004 | 31.1% | +0.64 | +3022.5% | -53.7% | +0.51 | +886.1% | -52.6% | non | non |
| Russell 2000 | 6004 | 31.1% | +0.35 | +658.0% | -59.9% | +0.25 | +234.2% | -63.1% | non | non |
| S&P 500 | 6004 | 31.1% | +0.47 | +718.4% | -56.8% | +0.32 | +221.1% | -60.1% | non | non |
| DAX | 6059 | 31.2% | +0.37 | +580.3% | -54.8% | +0.33 | +314.6% | -49.1% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
