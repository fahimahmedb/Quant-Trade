# Audit adversarial — Overlay levé filtre de pente SMA200

## 1. Recalcul indépendant (boucle explicite vs pandas.rolling)

| Marché | Écart masque (nb j., hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque de pente confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

## 3. Exposition pendant les grands krachs (drawdown ≥40%) : pente (#66) vs niveau (#29)

| Marché | %j levé PENDANT drawdown≥40% (pente, #66) | %j levé PENDANT drawdown≥40% (niveau, #29) |
|---|---|---|
| Composite (5 ans) | nan% | nan% |
| NDX (40 ans) | 61.6% | 61.6% |
| Russell 2000 | 0.0% | 8.5% |
| S&P 500 | 0.0% | 6.6% |
| DAX | 50.0% | 50.6% |

**Lecture** : si le filtre de pente coupe réellement plus tôt en début de retournement que le filtre de niveau, le %j levé pendant les grands krachs devrait être PLUS FAIBLE pour la pente (#66) que pour le niveau (#29). Les chiffres ci-dessus permettent de juger cette hypothèse sans qu'elle ait été utilisée pour ajuster un paramètre — la comparaison est faite APRÈS coup, à titre d'explication du résultat déjà obtenu, pas de retuning.
