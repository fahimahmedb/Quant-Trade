# Résultat — Taux réel TIPS 10 ans (DFII10), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DFII10_lag(t) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 81.4% | +0.52 | +79.0% | -36.4% | +0.47 | +36.1% | -21.6% | non | non |
| NDX (40 ans) | 5917 | 24.4% | +0.65 | +2770.3% | -53.7% | +0.61 | +1603.2% | -47.0% | non | non |
| Russell 2000 | 5917 | 24.4% | +0.36 | +651.9% | -59.9% | +0.33 | +439.8% | -51.7% | non | non |
| S&P 500 | 5917 | 24.4% | +0.48 | +726.3% | -56.8% | +0.44 | +459.5% | -50.5% | non | non |
| DAX | 5973 | 24.5% | +0.42 | +706.9% | -54.8% | +0.35 | +391.4% | -50.9% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
