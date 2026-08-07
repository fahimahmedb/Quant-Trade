# Résultat — Force relative marchés émergents vs développés (EEM/SPY, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si RatioMom_lag(t)=log(Ratio(t-1)/Ratio(t-1-21)) avec Ratio=EEM/SPY est dans son tercile expanding le plus BAS (sous-performance marquée des émergents), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 23.4% | +0.52 | +56.8% | -36.4% | +0.48 | +46.9% | -39.0% | non | non |
| NDX (40 ans) | 5826 | 42.1% | +0.64 | +1369.3% | -53.7% | +0.60 | +740.3% | -45.5% | non | non |
| Russell 2000 | 5826 | 42.1% | +0.35 | +255.9% | -59.9% | +0.26 | +108.9% | -55.1% | non | non |
| S&P 500 | 5826 | 42.1% | +0.48 | +433.6% | -56.8% | +0.38 | +195.3% | -50.2% | non | non |
| DAX | 5880 | 41.7% | +0.45 | +414.6% | -54.8% | +0.38 | +215.3% | -47.6% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
