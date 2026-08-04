# Audit — Corrélation cross-marché NDX-Russell 2000 (domestique)

## Recalcul corr(t) (Pearson glissant 60j)
- Écart max corr(t) (pandas rolling().corr() vs boucle+formule Pearson manuelle) : 2.23e-14
- **OK**

## Composite (5 ans)
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 1.35e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 2.23e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 2.23e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 2.23e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 2.23e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Anti-lookahead (NDX, troncature à 2551 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
