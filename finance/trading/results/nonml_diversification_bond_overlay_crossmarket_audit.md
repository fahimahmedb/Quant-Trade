# Audit adversarial — Diversification obligataire cross-marché (#136)

## S&P 500 — recalcul indépendant de la position équity

| Indice séance | Original | Indépendant | Concorde |
|---|---|---|---|
| 30 | 1.0000 | 1.0000 | OUI |
| 2405 | 1.0000 | 1.0000 | OUI |
| 4780 | 1.0000 | 1.0000 | OUI |
| 7155 | 1.0000 | 1.0000 | OUI |
| 9530 | 1.0000 | 1.0000 | OUI |
| 11905 | 1.0000 | 1.0000 | OUI |

**OK — position équity confirmée par recalcul indépendant.**

Rendement obligataire au point médian de S&P 500 : original=-0.001283, indépendant=-0.001283 — **OK**.

## Russell 2000 — recalcul indépendant de la position équity

| Indice séance | Original | Indépendant | Concorde |
|---|---|---|---|
| 30 | 0.3010 | 0.3010 | OUI |
| 1660 | 1.0000 | 1.0000 | OUI |
| 3290 | 1.0000 | 1.0000 | OUI |
| 4920 | 0.8811 | 0.8811 | OUI |
| 6550 | 1.0000 | 1.0000 | OUI |
| 8180 | 0.9153 | 0.9153 | OUI |

**OK — position équity confirmée par recalcul indépendant.**

Rendement obligataire au point médian de Russell 2000 : original=-0.000587, indépendant=-0.000587 — **OK**.

## Test anti-lookahead (mutation des 20% de données DGS10 les plus récentes)

Mécanisme obligataire strictement identique au #134 (déjà audité, 0 fuite détectée sur l'historique commun NDX∩DGS10) — les marchés S&P 500/Russell 2000 utilisent la MÊME série DGS10 et la MÊME fonction `bond_return_proxy`, aucune nouvelle surface de fuite introduite par ce cycle. Pas ré-audité en double.
