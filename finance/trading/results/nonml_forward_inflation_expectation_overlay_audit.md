# Audit — Anticipation d'inflation à long terme (5 ans dans 5 ans, T5YIFR)

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
- **1/5973 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#342) : confirmé.
- **OK**

## Vérification spécifique du décalage causal d'un jour (transition 2026-08-05→2026-08-06)
- T5YIFR brut jour précédent (2026-08-05) = 2.260000, T5YIFR brut jour de la transition (2026-08-06) = 2.290000 (valeurs distinctes vérifiées : OUI)
- T5YIFR_lag(2026-08-06) = 2.260000 (doit valoir 2.260000, JAMAIS 2.290000)
- T5YIFR_lag(2026-08-07) = 2.290000 (doit être le premier jour où 2.290000 apparaît, via shift(1))
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 6355 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
