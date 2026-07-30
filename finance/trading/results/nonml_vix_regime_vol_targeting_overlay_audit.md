# Audit adversarial — Overlay vol-targeting gaté par le régime VIX

## 1. Recalcul indépendant de la porte (boucle Python explicite, médiane manuelle)

| Date NDX (indice) | Concorde |
|---|---|
| 2000 | OUI |
| 3500 | OUI |
| 5000 | OUI |
| 6500 | OUI |
| 8000 | OUI |
| 9500 | OUI |

**OK — porte confirmée par recalcul indépendant (6 dates).**

## 2. Test anti-lookahead (mutation des 20% de données VIX les plus récentes)

Écart de porte sur les séances antérieures à la mutation (marge 400j) : 0
**OK — aucune fuite, le passé est bien inchangé.**
