# Résultat — Panel élargi à 5 signaux (défaut carte #286 + NFCI #291 + BAA10Y #199 + corrélation NDX-DAX #193 + MOVE #357), vote ≥4/5, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si AU MOINS 4 des 5 signaux sont dans leur tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé (≥4/5) | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 17.6% | +0.52 | +79.0% | -36.4% | +0.60 | +80.8% | -33.8% | OUI | OUI |
| NDX (40 ans) | 5951 | 9.0% | +0.65 | +2844.6% | -53.7% | +0.71 | +2781.7% | -40.2% | OUI | non |
| Russell 2000 | 5951 | 8.8% | +0.36 | +687.8% | -59.9% | +0.44 | +776.0% | -42.9% | OUI | OUI |
| S&P 500 | 5951 | 6.6% | +0.48 | +750.7% | -56.8% | +0.57 | +838.0% | -39.6% | OUI | OUI |
| DAX | 6005 | 9.3% | +0.41 | +704.1% | -54.8% | +0.49 | +798.2% | -34.2% | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
