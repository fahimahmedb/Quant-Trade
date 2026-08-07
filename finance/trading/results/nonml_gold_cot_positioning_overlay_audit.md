# Audit — Positionnement spéculatif net CFTC sur l'or (COT)

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
- **2/9781 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#360) : confirmé.
- **OK**

## S&P 500
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **2/6776 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#360) : confirmé.
- **OK**

## Vérification spécifique du décalage de publication (10j) + causal (1j)
- Dernière observation « en date du » 2026-07-28 = 47.339724 (observation précédente 2026-07-21 = 47.972183, valeurs distinctes : OUI)
- Date de disponibilité déclarée (as_of + 10j) = 2026-08-07
- NetPctSpécOr_lag(2026-08-07) = 47.972183 (doit valoir 47.972183, JAMAIS 47.339724 — la valeur n'est censée devenir visible qu'au jour SUIVANT sa disponibilité, via shift(1))
- NetPctSpécOr_lag(2026-08-08) = 47.339724 (doit être le premier jour où 47.339724 apparaît)
- **OK — le décalage de publication + causal est correctement appliqué**

## Anti-lookahead (NDX, troncature à 2081 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
