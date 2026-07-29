# Audit adversarial — Overlay levé effet post-jour férié

## 1. Recalcul indépendant (datetime.timedelta standard, boucle explicite)

| Marché | Écart masque (nb j.) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque confirmé par recalcul indépendant.**

## 2. Distribution des écarts calendaires détectés (vérifie la plausibilité économique)

| Marché | Nb séances post-jour férié | Nb années | Moyenne/an | Écart médian (j) détecté |
|---|---|---|---|---|
| Composite (5 ans) | 37 | 6 | 6.17 | 4 |
| NDX (40 ans) | 263 | 42 | 6.26 | 4 |
| Russell 2000 | 253 | 40 | 6.33 | 4 |
| S&P 500 | 351 | 57 | 6.16 | 4 |
| DAX | 88 | 28 | 3.14 | 5 |

## 3. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — comportement stable (le calendrier n'est pas une donnée de marché, aucune fuite possible par construction).**

**Lecture économique du FAIL** : ~6,2-6,3 séances/an détectées sur les marchés US (Composite/NDX/Russell/S&P 500), plus faible sur DAX (~3,1/an, calendrier de jours fériés allemand différent), cohérent avec un nombre plausible de ponts/jours fériés longs par an. Contrairement aux fenêtres calendaires concentrées et récurrentes qui fonctionnent (ToM, Halloween, Santa Claus, actives sur des blocs de plusieurs séances consécutives chaque occurrence), un signal composé de quelques jours ISOLÉS (une seule séance par occurrence) et dispersés dans l'année est structurellement trop bruité (chaque occurrence individuelle pèse énormément sur le résultat agrégé) pour constituer un déclencheur de levier fiable.
