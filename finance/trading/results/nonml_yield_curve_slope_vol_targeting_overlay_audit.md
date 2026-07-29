# Audit adversarial — Overlay vol-targeting gaté par la pente de la courbe des taux US (T10Y2Y)

## 1. Recalcul indépendant de la porte (boucle Python explicite, médiane manuelle, sans pandas.rolling/reindex)

| Date NDX (indice) | Concorde |
|---|---|
| 2000 | OUI |
| 3500 | OUI |
| 5000 | OUI |
| 6500 | OUI |
| 8000 | OUI |
| 9500 | OUI |

**OK — porte confirmée par recalcul indépendant (6 dates).**

## 2. Test anti-lookahead (mutation des 20% de données T10Y2Y les plus récentes)

Écart de porte sur les séances antérieures à la mutation (marge 400j pour la fenêtre médiane 252j) : 0
**OK — aucune fuite, le passé est bien inchangé.**
