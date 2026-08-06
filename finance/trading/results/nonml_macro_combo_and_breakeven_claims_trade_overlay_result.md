# Résultat — Combinaison ET (3/3) breakeven inflation + demandes continues + balance commerciale (pré-enregistré)

`position(t) = 0.5x` si LES 3 gates (#200 T10YIE tercile haut, #322 CCSA tercile haut, #327 BOPGSTB tercile bas) sont SIMULTANÉMENT actifs, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 11.1% | +0.52 | +57.6% | -36.4% | +0.60 | +67.6% | -30.0% | OUI | OUI |
| NDX (40 ans) | 5917 | 6.8% | +0.65 | +1516.1% | -53.7% | +0.66 | +1580.5% | -51.1% | OUI | OUI |
| Russell 2000 | 5917 | 6.7% | +0.36 | +278.1% | -59.9% | +0.40 | +372.1% | -57.9% | OUI | OUI |
| S&P 500 | 5917 | 6.0% | +0.48 | +446.8% | -56.8% | +0.50 | +480.2% | -53.4% | OUI | OUI |
| DAX | 5973 | 6.4% | +0.42 | +380.5% | -54.8% | +0.42 | +362.1% | -52.6% | non | non |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
