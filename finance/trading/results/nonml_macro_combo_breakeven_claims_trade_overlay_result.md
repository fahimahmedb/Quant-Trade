# Résultat — Combinaison majoritaire (≥2/3) breakeven inflation + demandes continues + balance commerciale (pré-enregistré)

`position(t) = 0.5x` si AU MOINS 2 des 3 gates (#200 T10YIE tercile haut, #322 CCSA tercile haut, #327 BOPGSTB tercile bas) sont actifs, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 22.2% | +0.52 | +57.6% | -36.4% | +0.72 | +84.5% | -22.4% | OUI | OUI |
| NDX (40 ans) | 5917 | 47.2% | +0.65 | +1516.1% | -53.7% | +0.78 | +1419.6% | -32.8% | OUI | non |
| Russell 2000 | 5917 | 47.3% | +0.36 | +278.1% | -59.9% | +0.47 | +420.1% | -45.1% | OUI | OUI |
| S&P 500 | 5917 | 42.7% | +0.48 | +446.8% | -56.8% | +0.60 | +512.1% | -36.7% | OUI | OUI |
| DAX | 5973 | 44.1% | +0.42 | +380.5% | -54.8% | +0.46 | +359.3% | -42.3% | OUI | non |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
