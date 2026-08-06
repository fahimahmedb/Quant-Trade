# Audit — Inflation réalisée US (FRED CPIAUCSL)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/10272 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

## Russell 2000
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/9781 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

## S&P 500
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/14251 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

## DAX
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage d'un mois (transition autour de 2026-07-01)
- Valeur mois précédent (obs 2026-05-01) = 0.041814, valeur dernier mois disponible (obs 2026-06-01) = 0.036588 (valeurs distinctes vérifiées : OUI)
- CPIGrowth_lag(2026-06-30) = 0.041814, CPIGrowth_lag(2026-07-01) = 0.041814 (doivent valoir 0.041814, JAMAIS 0.036588)
- CPIGrowth_lag(2026-07-02) = 0.036588, CPIGrowth_lag(2026-07-03) = 0.036588 (2026-07-02 doit être le premier jour où 0.036588 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Anti-lookahead (NDX, troncature à 4000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Anti-lookahead (NDX, troncature à 6000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
