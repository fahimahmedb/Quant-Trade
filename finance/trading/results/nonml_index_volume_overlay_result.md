# Résultat — Volume anormal de l'indice comme porte défensive (pré-enregistré)

`position(t) = 0.5x` si Vol(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps. Composite EXCLU (volume=0 documenté, voir PREREG). Critère ajusté à ≥3/4 marchés.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| NDX (40 ans) | 10272 | 83.4% | +0.53 | +26208.9% | -82.9% | +0.52 | +2026.9% | -58.5% | non | non |
| Russell 2000 | 9781 | 89.0% | +0.34 | +1646.9% | -59.9% | +0.32 | +305.4% | -36.7% | non | non |
| S&P 500 | 14251 | 93.1% | +0.45 | +7977.0% | -56.8% | +0.36 | +559.3% | -43.1% | non | non |
| DAX | 6776 | 40.5% | +0.25 | +353.5% | -72.7% | +0.33 | +316.8% | -58.1% | OUI | non |

**0/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère ajusté : ≥3/4, Composite exclu — volume=0).**

**FAIL — critère pré-enregistré NON atteint.**
