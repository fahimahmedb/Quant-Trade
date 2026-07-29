# Audit adversarial — Overlay de vol-targeting continu, cible 20%

## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.std)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 7.99e-15 |
| NDX (40 ans) | 6.35e-14 |
| Russell 2000 | 3.33e-14 |
| S&P 500 | 1.04e-13 |
| DAX | 4.22e-14 |

**OK — position confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture** : confirme l'hypothèse -- en relevant la vol cible de 15% (#43) à 20%, l'exposition moyenne passe au-dessus de 1.0x sur 4/5 marchés (1,10x à 1,51x), ce qui referme l'écart de rendement qui faisait échouer le #43 tout en conservant une réduction substantielle du MDD partout (même sur DAX, seul marché à échouer le critère renforcé : MDD -72,7%→-67,1%).
