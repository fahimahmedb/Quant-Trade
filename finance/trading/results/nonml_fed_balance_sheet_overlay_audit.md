# Audit — Bilan de la Réserve fédérale (WALCL, croissance 52 semaines)

## Composite (5 ans)
- Écart max alignement causal (pandas Timedelta/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas Timedelta/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (pandas Timedelta/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (pandas Timedelta/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas Timedelta/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage de 7 jours (transition autour de 2026-08-12)
- Valeur semaine précédente (obs 2026-07-29) = 0.014291, valeur dernière semaine disponible (obs 2026-08-05) = 0.016091 (valeurs distinctes vérifiées : OUI)
- WALCLGrowth_lag(2026-08-11) = 0.014291, WALCLGrowth_lag(2026-08-12) = 0.014291 (doivent valoir 0.014291, JAMAIS 0.016091)
- WALCLGrowth_lag(2026-08-13) = 0.016091, WALCLGrowth_lag(2026-08-14) = 0.016091 (2026-08-13 doit être le premier jour où 0.016091 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Anti-lookahead (NDX, troncature à 6602 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
