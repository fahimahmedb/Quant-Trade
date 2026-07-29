# Audit adversarial — Overlay levé effet jour-de-semaine

## 1. Recalcul indépendant (datetime.weekday() vs pandas.dt.dayofweek)

| Marché | Écart position (nb j.) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — position confirmée par recalcul indépendant.**

## 2. Distribution des jours déclencheurs (vérification qu'aucun jour n'est sur-représenté)

| Marché | Lun | Mar | Mer | Jeu | Ven |
|---|---|---|---|---|---|
| Composite (5 ans) | 231 | 259 | 258 | 251 | 252 |
| NDX (40 ans) | 1939 | 2109 | 2105 | 2066 | 2054 |
| Russell 2000 | 1844 | 2007 | 2005 | 1969 | 1957 |
| S&P 500 | 2701 | 2919 | 2921 | 2863 | 2848 |
| DAX | 1332 | 1366 | 1367 | 1369 | 1343 |

## 3. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — comportement stable (le calendrier n'est pas une donnée de marché, aucune fuite possible par construction).**

**Lecture économique du FAIL** : la fenêtre "forte" (mardi-vendredi) couvre ~80-81% des séances sur les 5 marchés -- une fenêtre aussi large équivaut quasiment à un levier permanent plutôt qu'à un signal sélectif, ce qui dégrade massivement le MDD partout (cf. #32, union à 3 signaux ~90% du temps, même écueil). Le Monday effect classique (French 1980), documenté sur des données US pré-2000, ne se manifeste pas ici avec une amplitude suffisante pour compenser le volatility drag d'un levier quasi permanent sur cet échantillon 2021-2026 (Composite) / 1985-2026 (NDX).
