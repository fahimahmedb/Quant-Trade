# Résultat — Bilan de la Réserve fédérale (WALCL, croissance 52 semaines), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si WALCLGrowth_lag(t)=log(WALCL(t)/WALCL(t-52)) est dans son tercile expanding le plus BAS (contraction du bilan la plus marquée, régime QT actif), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 64.6% | +0.52 | +79.0% | -36.4% | +0.63 | +58.6% | -27.4% | OUI | non |
| NDX (40 ans) | 5670 | 52.1% | +0.61 | +1944.3% | -53.7% | +0.49 | +662.3% | -49.2% | non | non |
| Russell 2000 | 5670 | 52.1% | +0.31 | +434.4% | -59.9% | +0.23 | +195.4% | -56.4% | non | non |
| S&P 500 | 5670 | 52.1% | +0.46 | +586.6% | -56.8% | +0.33 | +240.4% | -52.3% | non | non |
| DAX | 5722 | 52.1% | +0.40 | +533.9% | -54.8% | +0.28 | +206.1% | -49.8% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
