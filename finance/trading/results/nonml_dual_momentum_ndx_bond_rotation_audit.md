# Audit adversarial — Momentum absolu dual (rotation) NDX / proxy obligataire (#148)

## 1. Recalcul indépendant du signal de momentum (boucle Python explicite)

| Indice séance | Momentum NDX (orig via rolling) | Momentum NDX (indép.) | Momentum bond (orig) | Momentum bond (indép.) | Position (t) | Concorde |
|---|---|---|---|---|---|---|
| 282 | 0.1835 | 0.1835 | 0.2389 | 0.2389 | 0.0 | OUI |
| 1309 | -0.1189 | -0.1189 | 0.0665 | 0.0665 | 0.0 | OUI |
| 2336 | 0.0123 | 0.0123 | -0.0803 | -0.0803 | 1.0 | OUI |
| 3363 | 0.6547 | 0.6547 | 0.1102 | 0.1102 | 1.0 | OUI |
| 4390 | -0.3429 | -0.3429 | 0.1162 | 0.1162 | 0.0 | OUI |
| 5417 | 0.0762 | 0.0762 | 0.0483 | 0.0483 | 0.0 | OUI |
| 6444 | 0.1422 | 0.1422 | 0.0654 | 0.0654 | 1.0 | OUI |
| 7471 | 0.2198 | 0.2198 | 0.0433 | 0.0433 | 1.0 | OUI |
| 8498 | 0.0682 | 0.0682 | 0.1050 | 0.1050 | 0.0 | OUI |
| 9525 | 0.2332 | 0.2332 | -0.0107 | -0.0107 | 1.0 | OUI |

**OK — signal de momentum confirmé par recalcul indépendant (10 dates).**

## 2. Test anti-lookahead (mutation des 20% de données NDX et DGS10 les plus récentes)

Écart de position sur les séances antérieures à la mutation (marge 292j) : 0
**OK — aucune fuite, le passé est bien inchangé.**
