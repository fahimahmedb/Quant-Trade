# Audit adversarial — Overlay vol-targeting gaté par vote majoritaire (5 gates)

## 1. Recalcul indépendant du décompte de votes (boucle Python explicite, addition manuelle)

| Date (indice) | Vote original | Vote recalculé | Écart |
|---|---|---|---|
| 8887 | 0 | 0 | 0 |
| 9287 | 2 | 2 | 0 |
| 9687 | 5 | 5 | 0 |
| 10087 | 3 | 3 | 0 |

**OK — décompte de votes confirmé par recalcul indépendant.**

## 2. Test anti-lookahead sur l'infrastructure d'agrégation (mutation NDX, 20% les plus récents)

Écart max sur les positions passées (avant mutation, marge 260j) : 0.00e+00
**OK — aucune fuite du futur vers le passé.**

## 3. Cohérence du seuil de vote

**OK — porte finale (Vote>=3) cohérente sur toute la période testable.**
