# Audit adversarial — "January effect" (proxy prix bas) en overlay

## 1. Recalcul indépendant de la sélection tercile (boucle Python explicite)

| Date (indice) | Écart max absolu (poids) |
|---|---|
| 21 | 0.00e+00 |
| 126 | 0.00e+00 |
| 231 | 0.00e+00 |
| 336 | 0.00e+00 |
| 441 | 0.00e+00 |
| 546 | 0.00e+00 |
| 651 | 0.00e+00 |
| 756 | 0.00e+00 |
| 861 | 0.00e+00 |
| 966 | 0.00e+00 |
| 1071 | 0.00e+00 |
| 1176 | 0.00e+00 |
| 1281 | 0.00e+00 |
| 1386 | 0.00e+00 |

**OK — sélection confirmée par recalcul indépendant sur toutes les dates échantillonnées.**

## 2. Détection du mois de janvier (data-driven, pas de plage codée en dur)

| Année | Jours de bourse en janvier détectés |
|---|---|
| 2021 | 19 |
| 2022 | 20 |
| 2023 | 20 |
| 2024 | 21 |
| 2025 | 20 |
| 2026 | 20 |

**OK — nombre de jours de bourse par janvier plausible (15-23j US, ou 0 pour une année partielle).**

## 3. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la sélection calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 4. Rappel de la limite méthodologique (voir PREREG)

Le tercile 'prix bas' est un proxy imparfait de la capitalisation boursière réelle (pas de données de nombre d'actions en circulation disponibles). Le résultat teste un effet de NIVEAU DE PRIX, pas une vraie stratification par taille d'entreprise — limite documentée avant tout calcul dans le PREREG, pas découverte après coup.
