# Audit adversarial — Expérience C' : sensibilité Stratégie A à la sortie

## 1. Recalcul indépendant SMA50 / SMA20 / niveau breakout (boucles explicites)

- Écart max SMA50 : 1.09e-11, SMA20 : 7.28e-12, breakout 20j : 0.00e+00
- **OK**

## 2. Vérification arithmétique des trades (variantes à TP fixe)

- TP=2R (référence A) : 41 trades vérifiés, 0 hors attendu — **OK**
- TP=3R : 32 trades vérifiés, 0 hors attendu — **OK**
- TP=4R : 27 trades vérifiés, 0 hors attendu — **OK**
- Time stop 10j (structure TP=2R) : 46 trades vérifiés, 0 hors attendu — **OK**

## 3. Test anti-lookahead (perturbation du futur, OHLC), par variante

- TP=2R (référence A) : OK — aucune fuite
- TP=3R : OK — aucune fuite
- TP=4R : OK — aucune fuite
- Trailing stop (chandelier, pas de TP) : OK — aucune fuite
- Pas de TP, sortie rupture tendance (close<SMA20) : OK — aucune fuite
- Time stop 10j (structure TP=2R) : OK — aucune fuite

## Verdict global : **CONFORME**
