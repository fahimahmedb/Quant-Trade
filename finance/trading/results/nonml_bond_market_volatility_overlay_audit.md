# Audit — Indice MOVE (volatilité implicite obligataire)

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
- **1/6005 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#356) : confirmé.
- **OK**

## Vérification spécifique du décalage causal d'un jour (transition 2026-07-16→2026-07-17)
- MOVE brut jour précédent (2026-07-16) = 68.160004, MOVE brut jour de la transition (2026-07-17) = 70.879997 (valeurs distinctes vérifiées : OUI)
- MOVE_lag(2026-07-17) = 68.160004 (doit valoir 68.160004, JAMAIS 70.879997)
- MOVE_lag(2026-07-18) = 70.879997 (doit être le premier jour où 70.879997 apparaît, via shift(1))
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 6321 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
