# Résultat — Overlay défensif vitesse du taux court DGS3MO (pré-enregistré, règle renforcée)

`position(t) = 0.5x` si delta(t-1)=DGS3MO_lag(t-1)-DGS3MO_lag(t-1-63) est dans son tercile expanding le plus haut (resserrement le plus rapide), `1,0x` sinon. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1186 | 23.3% | +0.55 | +60.3% | -36.4% | +0.82 | +91.0% | -24.5% | OUI | OUI |
| NDX (40 ans) | 10208 | 31.9% | +0.52 | +5637.0% | -82.9% | +0.53 | +4771.5% | -74.1% | OUI | non |
| Russell 2000 | 9717 | 30.9% | +0.40 | +1026.9% | -59.9% | +0.40 | +887.7% | -54.8% | OUI | non |
| S&P 500 | 11240 | 28.8% | +0.51 | +2802.0% | -56.8% | +0.52 | +2215.4% | -52.7% | OUI | non |
| DAX | 6712 | 30.9% | +0.21 | +82.1% | -72.7% | +0.20 | +73.2% | -71.6% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
