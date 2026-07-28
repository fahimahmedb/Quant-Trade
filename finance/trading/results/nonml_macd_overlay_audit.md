# Audit adversarial — Overlay levé croisement MACD

## 1. Recalcul indépendant (récursion EMA explicite vs pandas.ewm)

| Marché | Écart masque (nb j., hors marge de convergence) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque MACD confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture économique du FAIL** : l'exposition levée est proche de 50% (contre ~70-75% pour SMA200/#29) -- le MACD est un signal beaucoup plus réactif (bruité), générant plus de faux signaux/allers-retours en régime sans tendance nette, avec des coûts de transaction accrus, contrairement au filtre plus lent SMA200/Golden Cross qui a mieux fonctionné.
