# Résultat — Volume RELATIF de l'indice (ratio à MA252) comme porte défensive (pré-enregistré)

`position(t) = 0.5x` si VolRatio(t-1) = Vol(t-1)/MA_252(Vol)(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps. Composite EXCLU (volume=0 documenté). Critère ajusté à ≥3/4 marchés.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| NDX (40 ans) | 10021 | 29.9% | +0.52 | +5508.9% | -82.9% | +0.51 | +3079.5% | -79.0% | non | non |
| Russell 2000 | 9530 | 31.5% | +0.37 | +742.9% | -59.9% | +0.32 | +372.2% | -55.1% | non | non |
| S&P 500 | 14000 | 29.7% | +0.46 | +3444.0% | -56.8% | +0.37 | +934.7% | -57.9% | non | non |
| DAX | 6525 | 27.2% | +0.23 | +93.7% | -69.1% | +0.21 | +77.1% | -62.7% | non | non |

**0/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère ajusté : ≥3/4, Composite exclu — volume=0).**

**FAIL — critère pré-enregistré NON atteint.**
