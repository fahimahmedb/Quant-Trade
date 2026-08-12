# Résultat — Overlay défensif vitesse du taux court DGS3MO (pré-enregistré, règle renforcée)

`position(t) = 0.5x` si delta(t-1)=DGS3MO_lag(t-1)-DGS3MO_lag(t-1-63) est dans son tercile expanding le plus haut (resserrement le plus rapide), `1,0x` sinon. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1186 | 23.3% | +0.55 | +81.6% | -36.4% | +0.82 | +108.0% | -24.5% | OUI | OUI |
| NDX (40 ans) | 10208 | 31.9% | +0.52 | +22376.6% | -82.9% | +0.53 | +14125.1% | -74.1% | OUI | non |
| Russell 2000 | 9717 | 30.9% | +0.40 | +2617.4% | -59.9% | +0.40 | +1934.8% | -54.8% | OUI | non |
| S&P 500 | 11240 | 28.8% | +0.51 | +5924.2% | -56.8% | +0.52 | +4057.1% | -52.7% | OUI | non |
| DAX | 6712 | 30.9% | +0.21 | +255.4% | -72.7% | +0.20 | +208.1% | -71.6% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
