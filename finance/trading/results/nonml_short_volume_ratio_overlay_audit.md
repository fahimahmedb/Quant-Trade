# Audit — Ratio de volume vendu à découvert QQQ (FINRA Reg SHO)

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

## Vérification spécifique du décalage de publication (2j) + causal (1j)
- Dernière observation (2026-08-06) = 0.610457 (observation précédente 2026-08-05 = 0.748595, valeurs distinctes : OUI)
- Date de disponibilité déclarée (date + 2j) = 2026-08-08
- ShortVolRatio_lag(2026-08-08) = 0.748595 (doit valoir 0.748595, JAMAIS 0.610457)
- ShortVolRatio_lag(2026-08-09) = 0.610457 (doit être le premier jour où 0.610457 apparaît, via shift(1))
- **OK — le décalage de publication + causal est correctement appliqué**

## Anti-lookahead (NDX, troncature à 9279 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
