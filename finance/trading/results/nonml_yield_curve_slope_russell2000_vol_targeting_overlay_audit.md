# Audit adversarial — Pente de la courbe des taux US appliquée au Russell 2000

## 1. Recalcul indépendant de la porte (boucle Python explicite, médiane manuelle)

| Date marché (indice) | Concorde |
|---|---|
| 2000 | OUI |
| 4000 | OUI |
| 6000 | OUI |
| 8000 | OUI |

**OK — porte confirmée par recalcul indépendant (4 dates).**

## 2. Test anti-lookahead (mutation des 20% de données T10Y2Y les plus récentes)

Écart de porte sur les séances antérieures à la mutation (marge 400j) : 0
**OK — aucune fuite, le passé est bien inchangé.**
