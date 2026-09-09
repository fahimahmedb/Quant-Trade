# Audit adversarial — Stratégie B : Score multi-facteurs /10 (daily)

## 1. Recalcul indépendant du score (boucles explicites)

- Écart max score (vectorisé vs boucle), séances valides des deux côtés : 0.00e+00
- Désaccords NaN (amorçage) entre les deux implémentations : 0
- **OK**

## 2. Vérification arithmétique des trades

- Trades vérifiés : 58
- Trades avec R-multiple hors attendu (SL=-1R, TP=+2.0R exacts par construction) : 0
- **OK**

## 3. Test anti-lookahead (perturbation du futur, OHLC)

- Equity identique avant le point de coupure (séance 420) après perturbation du futur : OUI
- **OK — aucune fuite de données futures.**

## Verdict global : **CONFORME**
