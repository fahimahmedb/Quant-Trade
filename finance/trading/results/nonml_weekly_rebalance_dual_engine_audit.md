# Audit adversarial — Rebalancement hebdomadaire du mécanisme #121

## 1. Recalcul indépendant de la position hebdomadaire (formule fermée, indépendante de la boucle du backtest)

| Indice séance | Concorde |
|---|---|
| 0 | OUI |
| 733 | OUI |
| 1466 | OUI |
| 2199 | OUI |
| 2932 | OUI |
| 3665 | OUI |
| 4398 | OUI |
| 5131 | OUI |
| 5864 | OUI |
| 6597 | OUI |
| 7330 | OUI |
| 8063 | OUI |
| 8796 | OUI |

**OK — position hebdomadaire confirmée par recalcul indépendant (13 dates).**

## 2. Test anti-lookahead (mutation des 20% de positions quotidiennes les plus récentes)

Écart de position hebdo sur les séances antérieures à la mutation (marge 15 séances) : 0
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Vérification turnover : changements uniquement aux multiples de REBAL_FREQ

Changements de position hebdo hors multiples de 5 : 0 / 1474 changements totaux
**OK — tous les changements tombent sur un multiple de REBAL_FREQ.**
