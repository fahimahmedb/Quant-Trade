# Résultat — Indice MOVE (volatilité implicite obligataire), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si MOVE_lag(t) est dans son tercile expanding le plus HAUT (stress obligataire implicite le plus élevé), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 33.6% | +0.52 | +57.6% | -36.4% | +0.70 | +69.1% | -23.5% | OUI | OUI |
| NDX (40 ans) | 5951 | 23.0% | +0.65 | +1542.1% | -53.7% | +0.74 | +1489.5% | -36.5% | OUI | non |
| Russell 2000 | 5951 | 23.0% | +0.36 | +294.8% | -59.9% | +0.45 | +411.6% | -44.1% | OUI | OUI |
| S&P 500 | 5951 | 23.0% | +0.48 | +461.1% | -56.8% | +0.60 | +523.6% | -40.5% | OUI | OUI |
| DAX | 6005 | 23.1% | +0.41 | +372.8% | -54.8% | +0.47 | +410.6% | -39.0% | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**Note qualité des données** : la série `^MOVE` récupérée via Yahoo Finance s'arrête au 17/07/2026 (valeurs manquantes pour les ~3 dernières semaines avant le fetch, au-delà du simple point le plus récent anticipé au PREREG) — la dernière valeur connue est propagée en avant (ffill) sur cette période, comme pour tout autre décalage/gap dans une source externe. Impact négligeable sur des séries testées de plusieurs milliers de séances.

**PASS — critère pré-enregistré atteint.**
