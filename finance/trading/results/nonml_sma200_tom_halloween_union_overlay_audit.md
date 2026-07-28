# Audit adversarial — Overlay levé union SMA200∪(ToM∪Halloween)

## 1. Union à 3 ensembles (inclusion-exclusion)

| Marché | %SMA200 | %ToM | %Halloween | %Union mesurée | %Union incl-excl | Écart |
|---|---|---|---|---|---|---|
| Composite (5 ans) | 75.4% | 34.3% | 46.8% | 91.5% | 91.5% | 1.11e-16 |
| NDX (40 ans) | 75.3% | 33.4% | 49.1% | 91.9% | 91.9% | 1.11e-16 |
| Russell 2000 | 68.8% | 33.4% | 49.1% | 89.2% | 89.2% | 0.00e+00 |
| S&P 500 | 72.3% | 33.4% | 49.4% | 91.2% | 91.2% | 0.00e+00 |
| DAX | 67.8% | 33.2% | 48.9% | 89.1% | 89.1% | 0.00e+00 |

**OK — union à 3 ensembles cohérente, aucun bug de fusion.**

## 2. Test anti-lookahead sur le signal SMA200

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture honnête** : la fraction de jours levés (~90%) est proche d'un levier quasi-permanent -- le gain de Sharpe reste réel mais modeste sur chaque marché (ex. NDX +0,51→+0,55), la majeure partie du gain de rendement affiché vient simplement de l'effet multiplicatif du levier sur un actif à drift positif (mécanique déjà mise en évidence au cycle #10), pas d'un edge nouveau créé par la triple union en tant que telle. Le MDD se dégrade fortement partout (ex. NDX -82,9%→-95,8%), risque assumé mais à souligner.
