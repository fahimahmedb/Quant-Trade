# Audit adversarial — Diversification défensive vers un proxy obligataire (#115+DGS10)

## 1. Recalcul indépendant du rendement obligataire + rendement combiné (boucle Python explicite)

| Date NDX (indice) | Rendement obligataire (backtest) | Recalcul indépendant | Concorde |
|---|---|---|---|
| 10 | -0.002099 | -0.002099 | OUI |
| 1510 | -0.005870 | -0.005870 | OUI |
| 3010 | -0.006372 | -0.006372 | OUI |
| 4510 | -0.000631 | -0.000631 | OUI |
| 6010 | 0.000971 | 0.000971 | OUI |
| 7510 | -0.000802 | -0.000802 | OUI |
| 9010 | 0.003783 | 0.003783 | OUI |

**OK — recalcul indépendant confirmé (7 dates).**

## 2. Test anti-lookahead (mutation des 20% de données DGS10 les plus récentes)

Écart de rendement obligataire sur les séances antérieures à la mutation (marge 400j) : 0 / 6743 comparées
**OK — aucune fuite, le passé est bien inchangé.**
