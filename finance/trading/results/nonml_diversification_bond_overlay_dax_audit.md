# Audit adversarial — Diversification obligataire sur DAX (#140)

## 1. Recalcul indépendant du rendement obligataire (taux allemand, forward-fill causal jour-à-jour : y_now = dernière observation mensuelle connue AU JOUR t, y_prev = dernière observation mensuelle connue AU JOUR t-1 -- identiques la plupart des jours, sauf au changement de mois)

| Date DAX (indice) | Original | Indépendant | Concorde |
|---|---|---|---|
| 300 | 0.000191 | 0.000191 | OUI |
| 1100 | 0.000155 | 0.000155 | OUI |
| 1900 | 0.000165 | 0.000165 | OUI |
| 2700 | 0.000101 | 0.000101 | OUI |
| 3500 | 0.000069 | 0.000069 | OUI |
| 4300 | 0.000000 | 0.000000 | OUI |
| 5100 | -0.000012 | -0.000012 | OUI |
| 5900 | 0.000087 | 0.000087 | OUI |
| 6700 | 0.000115 | 0.000115 | OUI |

**OK — recalcul indépendant confirmé (9 dates).**

## 2. Test anti-lookahead (mutation des 20% de taux allemand les plus récents)

Écart de rendement obligataire sur les séances antérieures à la mutation (marge 60j) : 0 / 3160 comparées
**OK — aucune fuite, le passé est bien inchangé.**
