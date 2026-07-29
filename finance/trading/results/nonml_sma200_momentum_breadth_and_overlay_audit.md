# Audit adversarial — Double porte AND breadth SMA200 + breadth de momentum

## 1. Recalcul indépendant des deux breadth (boucle Python explicite)

| Date (indice) | Écart SMA200 | Écart momentum | Porte AND concorde |
|---|---|---|---|
| 252 | 0.00e+00 | 0.00e+00 | OUI |
| 402 | 0.00e+00 | 0.00e+00 | OUI |
| 552 | 0.00e+00 | 0.00e+00 | OUI |
| 702 | 0.00e+00 | 0.00e+00 | OUI |
| 852 | 0.00e+00 | 0.00e+00 | OUI |
| 1002 | 0.00e+00 | 0.00e+00 | OUI |
| 1152 | 0.00e+00 | 0.00e+00 | OUI |
| 1302 | 0.00e+00 | 0.00e+00 | OUI |

**OK — les deux breadth et la porte AND sont confirmées par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur les breadth calculées à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Vérification de la logique AND (porte combinée ⊆ chaque porte individuelle)

Porte AND ⊆ porte SMA200 : OK. Porte AND ⊆ porte momentum : OK.
