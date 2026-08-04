# Audit — Prime de risque de variance (VIX - vol réalisée)

## Composite (5 ans)
- Écart max VRP (rolling/std pandas vs boucle+std manuel ddof=1) : 4.80e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max VRP (rolling/std pandas vs boucle+std manuel ddof=1) : 4.35e-13
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max VRP (rolling/std pandas vs boucle+std manuel ddof=1) : 2.27e-13
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max VRP (rolling/std pandas vs boucle+std manuel ddof=1) : 8.84e-13
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max VRP (rolling/std pandas vs boucle+std manuel ddof=1) : 3.20e-13
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position[0:2000] pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite (le seuil expanding ne dépend jamais du futur)**

## Verdict global : **CONFORME**
