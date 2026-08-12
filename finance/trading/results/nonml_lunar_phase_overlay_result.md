# Résultat — Effet lunaire (nouvelle lune), overlay levé (pré-enregistré)

`position(t) = 2.0x` si la date est dans une fenêtre de ±7 jours calendaires autour de la nouvelle lune, `1.0x` sinon. Coûts 5 bps.

| Marché | Séances test. | % temps levé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 47.4% | +0.52 | +79.0% | -36.4% | +0.39 | +98.4% | -49.5% | non | OUI |
| NDX (40 ans) | 10272 | 47.5% | +0.53 | +26208.9% | -82.9% | +0.49 | +285502.0% | -91.9% | non | OUI |
| Russell 2000 | 9781 | 47.5% | +0.34 | +1646.9% | -59.9% | +0.33 | +6608.3% | -73.1% | non | OUI |
| S&P 500 | 14251 | 47.6% | +0.45 | +7977.0% | -56.8% | +0.39 | +32861.6% | -70.0% | non | OUI |
| DAX | 6776 | 47.8% | +0.25 | +353.5% | -72.7% | +0.27 | +1121.3% | -79.0% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
