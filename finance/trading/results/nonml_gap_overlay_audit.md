# Audit adversarial — Overlay levé après un gap d'ouverture extrême

## 1. Recalcul indépendant (boucle event-driven vs boucle du backtest)

| Marché | Écart position (nb j.) | %j levé |
|---|---|---|
| Composite (5 ans) | 0 | 7.5% |
| NDX (40 ans) | 0 | 4.4% |
| Russell 2000 | 0 | 0.6% |
| S&P 500 | 0 | 0.4% |
| DAX | 0 | 2.6% |

**OK — position confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur, close ET open)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture économique du FAIL** : le gap d'ouverture extrême (≥2%) est un événement rare (0,4% à 7,5% du temps levé selon le marché) et, comme les chocs de clôture-à-clôture déjà testés (#22/#24), il coïncide souvent avec le début d'un mouvement de marché qui se poursuit plutôt qu'un point de rebond fiable -- confirme que le timing basé sur un choc ponctuel (quelle que soit sa définition précise : clôture ou ouverture) ne constitue pas un signal de levier exploitable dans ce cadre.
