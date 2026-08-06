# Audit — Profits des entreprises US (FRED CP)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **4/6776 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#320) : confirmé.
- **OK**

## Vérification spécifique du décalage de 3 mois (transition autour de 2026-04-01)
- Valeur trimestre précédent (obs 2025-10-01) = 0.027468, valeur dernier trimestre disponible (obs 2026-01-01) = 0.169181 (valeurs distinctes vérifiées : OUI)
- CPGrowth_lag(2026-03-16) = 0.027468, CPGrowth_lag(2026-03-31) = 0.027468 (doivent valoir 0.027468, JAMAIS 0.169181)
- CPGrowth_lag(2026-04-01) = 0.027468, CPGrowth_lag(2026-04-02) = 0.169181 (2026-04-02 doit être le premier jour où 0.169181 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
