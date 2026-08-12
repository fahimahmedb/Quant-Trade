# Résultat — Anticipation d'inflation à long terme (5 ans dans 5 ans, T5YIFR), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si T5YIFR_lag(t) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 34.6% | +0.52 | +79.0% | -36.4% | +0.67 | +90.5% | -25.6% | OUI | OUI |
| NDX (40 ans) | 5917 | 25.7% | +0.65 | +2770.3% | -53.7% | +0.67 | +2235.4% | -52.0% | OUI | non |
| Russell 2000 | 5917 | 25.7% | +0.36 | +651.9% | -59.9% | +0.37 | +579.6% | -57.2% | OUI | non |
| S&P 500 | 5917 | 25.7% | +0.48 | +726.3% | -56.8% | +0.49 | +614.1% | -54.8% | OUI | non |
| DAX | 5973 | 25.7% | +0.42 | +706.9% | -54.8% | +0.42 | +565.9% | -54.0% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
