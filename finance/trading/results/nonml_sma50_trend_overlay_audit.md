# Audit adversarial — Overlay levé filtre de tendance SMA50

## 1. Recalcul indépendant du masque (boucle explicite vs pandas.rolling)

| Marché | Écart masque (nb j., hors 50 premiers) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — SMA50 et masque confirmés par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures, décisions passées strictement causales.**

## 3. Exposition pendant les grands krachs (drawdown ≥40% depuis le plus haut), comparaison SMA50 vs SMA200

| Marché | %j levé PENDANT drawdown≥40% (SMA50) |
|---|---|
| Composite (5 ans) | nan% |
| NDX (40 ans) | 56.9% |
| Russell 2000 | 32.5% |
| S&P 500 | 38.7% |
| DAX | 54.0% |

**Lecture** : la SMA50, plus réactive que la SMA200, coupe généralement plus vite en début de krach mais génère aussi plus de faux signaux de ré-entrée pendant les phases de rebond-piège d'un marché baissier prolongé. Sur NDX, le MDD est ici légèrement MOINS dégradé que le #29 (-82,9%→-90,2% contre -82,9%→-91,7% au #29), cohérent avec une exposition levée légèrement moindre (66,3% du temps ici contre 75,3% au #29) malgré un edge Sharpe/rendement globalement similaire.
