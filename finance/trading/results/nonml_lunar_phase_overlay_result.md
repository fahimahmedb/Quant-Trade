# Résultat — Effet lunaire (nouvelle lune), overlay levé (pré-enregistré)

`position(t) = 2.0x` si la date est dans une fenêtre de ±7 jours calendaires autour de la nouvelle lune, `1.0x` sinon. Coûts 5 bps.

| Marché | Séances test. | % temps levé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 47.4% | +0.52 | +57.6% | -36.4% | +0.39 | +46.0% | -49.5% | non | non |
| NDX (40 ans) | 10272 | 47.5% | +0.53 | +6599.5% | -82.9% | +0.49 | +10247.6% | -91.9% | non | OUI |
| Russell 2000 | 9781 | 47.5% | +0.34 | +602.0% | -59.9% | +0.33 | +663.9% | -73.1% | non | OUI |
| S&P 500 | 14251 | 47.6% | +0.45 | +3369.2% | -56.8% | +0.39 | +4111.6% | -70.0% | non | OUI |
| DAX | 6776 | 47.8% | +0.25 | +130.5% | -72.7% | +0.27 | +141.1% | -79.0% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
