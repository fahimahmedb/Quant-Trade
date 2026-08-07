# Résultat — Pression de vente nette des initiés (SEC Form 4, AAPL/MSFT/NVDA), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si NetSellPressure_lag(t) (somme glissante 21j de [valeur des ventes S − valeur des achats P] sur le panier AAPL/MSFT/NVDA) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps. Décalage de publication 3j + alignement causal quotidien standard.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 39.2% | +0.52 | +57.6% | -36.4% | +0.41 | +36.4% | -35.6% | non | non |
| NDX (40 ans) | 2779 | 53.1% | +0.76 | +391.0% | -35.6% | +0.60 | +182.0% | -28.0% | non | non |
| Russell 2000 | 2779 | 53.1% | +0.32 | +69.3% | -43.1% | +0.12 | +6.0% | -41.9% | non | non |
| S&P 500 | 2779 | 53.1% | +0.64 | +195.7% | -33.9% | +0.42 | +79.2% | -33.9% | non | non |
| DAX | 2805 | 53.1% | +0.37 | +78.5% | -38.8% | +0.14 | +11.8% | -40.5% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**Note qualité des données** : 1 transaction MSFT (01/09/2020, code S, prix affiché 2 261 327 $/action) exclue avant tout calcul — erreur de saisie confirmée dans le document XML officiel SEC lui-même (prix implausible pour MSFT ~228$ à cette date), filtre symétrique prix>5000$/action (1 seule ligne concernée sur 2544).

**FAIL — critère pré-enregistré NON atteint.**
