# Audit adversarial — Stratégie A : Daily Breakout (baseline)

## 1. Recalcul indépendant SMA50 / niveau de breakout (boucles explicites)

- Écart max SMA50 (vectorisé vs boucle) : 1.09e-11
- Écart max niveau breakout (vectorisé vs boucle) : 0.00e+00
- **OK**

## 2. Vérification arithmétique des trades

- Trades vérifiés : 41
- Trades avec R-multiple hors attendu (SL=-1R, TP=+2.0R exacts par construction) : 0
- **OK**

## 3. Test anti-lookahead (perturbation du futur, OHLC)

- Equity identique avant le point de coupure (séance 600) après perturbation du futur : OUI
- **OK — aucune fuite de données futures.**

## Verdict global : **CONFORME**
