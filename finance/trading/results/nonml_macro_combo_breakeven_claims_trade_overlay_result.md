# Résultat — Combinaison majoritaire (≥2/3) breakeven inflation + demandes continues + balance commerciale (pré-enregistré)

`position(t) = 0.5x` si AU MOINS 2 des 3 gates (#200 T10YIE tercile haut, #322 CCSA tercile haut, #327 BOPGSTB tercile bas) sont actifs, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 22.2% | +0.52 | +79.0% | -36.4% | +0.72 | +103.8% | -22.4% | OUI | OUI |
| NDX (40 ans) | 5917 | 47.2% | +0.65 | +2770.3% | -53.7% | +0.78 | +2017.4% | -32.8% | OUI | non |
| Russell 2000 | 5917 | 47.3% | +0.36 | +651.9% | -59.9% | +0.47 | +692.2% | -45.1% | OUI | OUI |
| S&P 500 | 5917 | 42.7% | +0.48 | +726.3% | -56.8% | +0.60 | +692.5% | -36.7% | OUI | non |
| DAX | 5973 | 44.1% | +0.42 | +706.9% | -54.8% | +0.46 | +552.7% | -42.3% | OUI | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
