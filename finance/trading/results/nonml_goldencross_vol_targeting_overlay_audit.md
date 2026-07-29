# Audit adversarial — Overlay vol-targeting gaté par golden cross

## 1. Recalcul totalement indépendant (boucle explicite jour par jour)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 7.99e-15 |
| NDX (40 ans) | 6.35e-14 |
| Russell 2000 | 3.33e-14 |
| S&P 500 | 1.04e-13 |
| DAX | 4.22e-14 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture économique du FAIL** : la porte golden cross est active 48,8-66,8% du temps selon le marché, une fréquence comparable à la porte 52w-high du #47. Malgré le lissage attendu (comparaison de deux moyennes plutôt que prix/moyenne), le golden cross n'apporte pas un edge supérieur combiné au vol-targeting -- 2 marchés (Composite de justesse, Russell 2000) échouent contre 1 seul au #47. Le signal 52w-high (#37/#47) reste le plus robuste des signaux de tendance testés comme porte du mécanisme hiérarchique dans ce backlog, confirmant l'observation déjà faite au #38/#39 (le 52w-high surperforme systématiquement les signaux basés sur des moyennes mobiles en combinaison).
