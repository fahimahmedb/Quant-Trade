# Audit — Indice OVX (volatilité implicite pétrolière)

## Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **2/1250 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#357) : confirmé.
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

## Vérification spécifique du décalage causal d'un jour (transition 2026-08-05→2026-08-06)
- OVX brut jour précédent (2026-08-05) = 51.480000, OVX brut jour de la transition (2026-08-06) = 57.340000 (valeurs distinctes vérifiées : OUI)
- OVX_lag(2026-08-06) = 51.480000 (doit valoir 51.480000, JAMAIS 57.340000)
- OVX_lag(2026-08-07) = 57.340000 (doit être le premier jour où 57.340000 apparaît, via shift(1))
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 7450 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
