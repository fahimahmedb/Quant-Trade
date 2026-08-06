# Audit — Indice CBOE SKEW (risque de queue)

## Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **2/9197 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#340) : confirmé.
- **OK**

## Russell 2000
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **2/9197 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#340) : confirmé.
- **OK**

## S&P 500
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **2/9197 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#340) : confirmé.
- **OK**

## DAX
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage causal d'un jour (transition 2026-08-04→2026-08-05)
- SKEW brut jour précédent (2026-08-04) = 126.410000, SKEW brut jour de la transition (2026-08-05) = 133.320000 (valeurs distinctes vérifiées : OUI)
- SKEW_lag(2026-08-05) = 126.410000 (doit valoir 126.410000, JAMAIS 133.320000)
- SKEW_lag(2026-08-06) = 133.320000 (doit être le premier jour où 133.320000 apparaît, via shift(1))
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 3075 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
