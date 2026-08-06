# Audit — Structure par terme du VIX (VXV 3-mois − VIX 30j)

## Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage causal d'un jour (transition 2026-07-27→2026-07-28)
- Slope brut jour précédent (2026-07-27) = 1.530000, Slope brut jour de la transition (2026-07-28) = 1.650000 (valeurs distinctes vérifiées : OUI)
- Slope_lag(2026-07-28) = 1.530000 (doit valoir 1.530000, JAMAIS 1.650000)
- Slope_lag(2026-07-29) = 1.650000 (doit être le premier jour où 1.650000 apparaît, via shift(1))
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 7594 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
