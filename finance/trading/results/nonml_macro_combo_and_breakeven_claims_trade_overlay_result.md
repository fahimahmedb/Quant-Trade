# Résultat — Combinaison ET (3/3) breakeven inflation + demandes continues + balance commerciale (pré-enregistré)

`position(t) = 0.5x` si LES 3 gates (#200 T10YIE tercile haut, #322 CCSA tercile haut, #327 BOPGSTB tercile bas) sont SIMULTANÉMENT actifs, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 11.1% | +0.52 | +79.0% | -36.4% | +0.60 | +87.4% | -30.0% | OUI | OUI |
| NDX (40 ans) | 5917 | 6.8% | +0.65 | +2770.3% | -53.7% | +0.66 | +2819.3% | -51.1% | OUI | OUI |
| Russell 2000 | 5917 | 6.7% | +0.36 | +651.9% | -59.9% | +0.40 | +815.5% | -57.9% | OUI | OUI |
| S&P 500 | 5917 | 6.0% | +0.48 | +726.3% | -56.8% | +0.50 | +767.2% | -53.4% | OUI | OUI |
| DAX | 5973 | 6.4% | +0.42 | +706.9% | -54.8% | +0.42 | +666.7% | -52.6% | non | non |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
