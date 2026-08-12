# Résultat — Overlay avance-retard cross-marché DAX→marchés US (pré-enregistré, règle renforcée)

`position(t) = 2.0x` si DaxRet(D-1) > 0 (continuation), `1,0x` sinon. DAX exclu comme marché cible (autocorrélation, pas spillover). Coûts 5 bps.

| Marché | Séances test. | % temps levé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 52.8% | +0.52 | +79.0% | -36.4% | +0.32 | +76.8% | -59.8% | non | non |
| NDX (40 ans) | 6711 | 53.1% | +0.33 | +1023.1% | -82.9% | +0.14 | +390.7% | -95.7% | non | non |
| Russell 2000 | 6711 | 53.1% | +0.30 | +582.6% | -59.9% | +0.01 | +13.4% | -86.2% | non | non |
| S&P 500 | 6711 | 53.1% | +0.33 | +457.3% | -56.8% | +0.04 | +40.8% | -88.0% | non | non |

**0/4 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé adapté : ≥3/4).**

**FAIL — critère pré-enregistré NON atteint.**
