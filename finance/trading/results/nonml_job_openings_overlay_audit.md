# Audit — Offres d'emploi US (FRED JTSJOL, JOLTS)

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
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage de 2 mois (transition autour de 2026-08-01)
- Valeur mois précédent (obs 2026-05-01) = 0.030581, valeur dernier mois disponible (obs 2026-06-01) = 0.021288 (valeurs distinctes vérifiées : OUI)
- JOLGrowth_lag(2026-07-31) = 0.030581, JOLGrowth_lag(2026-08-01) = 0.030581 (doivent valoir 0.030581, JAMAIS 0.021288)
- JOLGrowth_lag(2026-08-02) = 0.021288, JOLGrowth_lag(2026-08-03) = 0.021288 (2026-08-02 doit être le premier jour où 0.021288 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Anti-lookahead (NDX, troncature à 6124 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
