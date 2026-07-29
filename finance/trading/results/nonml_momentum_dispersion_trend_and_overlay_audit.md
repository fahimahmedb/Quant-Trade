# Audit adversarial — Double porte AND dispersion momentum + tendance 52w-high

## 1. Recalcul indépendant des deux portes (formules explicites)

| Date dispersion (indice titres) | Écart dispersion |
|---|---|
| 252 | 0.00e+00 |
| 402 | 0.00e+00 |
| 552 | 1.11e-16 |
| 702 | 5.55e-17 |
| 852 | 5.55e-17 |
| 1002 | 0.00e+00 |
| 1152 | 0.00e+00 |
| 1302 | 0.00e+00 |

| Date indice (indice NDX) | Écart tendance |
|---|---|
| 252 | concorde |
| 952 | concorde |
| 1652 | concorde |
| 2352 | concorde |
| 3052 | concorde |
| 3752 | concorde |
| 4452 | concorde |
| 5152 | concorde |
| 5852 | concorde |
| 6552 | concorde |
| 7252 | concorde |
| 7952 | concorde |
| 8652 | concorde |
| 9352 | concorde |
| 10052 | concorde |

**OK — dispersion et tendance confirmées par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart dispersion à une date antérieure à la mutation : 0.00e+00
Concordance tendance à une date antérieure à la mutation : OK
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Vérification de la logique AND (porte combinée ⊆ chaque porte individuelle)

Porte AND ⊆ porte tendance : OK. Porte AND ⊆ porte dispersion : OK.
