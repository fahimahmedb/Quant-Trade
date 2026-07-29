# Audit adversarial — Overlay de vol-targeting estimateur Parkinson

## 1. Recalcul totalement indépendant (variance Parkinson recalculée depuis high/low)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 6.66e-16 |
| NDX (40 ans) | 1.55e-15 |
| Russell 2000 | 6.66e-16 |
| S&P 500 | 4.44e-15 |
| DAX | 1.11e-15 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur, high/low)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture** : le biais anticipé dans le pré-enregistrement se confirme -- l'exposition moyenne (1,31x à 1,54x) est plus élevée que celle du #46 avec l'écart-type close-to-close (1,10x à 1,51x), cohérent avec le biais à la baisse connu de l'estimateur de Parkinson (il ignore le gap d'ouverture). Ceci n'invalide pas le résultat -- le critère de succès (Sharpe ET rendement > Buy&Hold) est mesuré tel quel, net de coûts, et le PASS est net et propre (5/5, contre 4/5 pour le #46) -- mais mérite d'être signalé pour la transparence méthodologique.
