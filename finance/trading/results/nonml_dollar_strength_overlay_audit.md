# Audit — Force du dollar américain (DTWEXBGS)

## Recalcul USDChange(t) (log-rendement 21j)
- Écart max USDChange(t) (construction numpy vectorisée vs boucle+dict explicite) : 0.00e+00
- **OK**

## Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/1250 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197) : confirmé.
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
- **1/5185 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197) : confirmé.
- **OK**

## Anti-lookahead (NDX, troncature à 6130 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
