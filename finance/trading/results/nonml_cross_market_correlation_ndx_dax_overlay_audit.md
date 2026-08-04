# Audit — Corrélation cross-marché NDX-DAX

## Recalcul corr(t) (Pearson glissant 60j)
- Écart max corr(t) (pandas rolling().corr() vs boucle+formule Pearson manuelle) : 5.48e-14
- **OK**

## Composite (5 ans)
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 1.35e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 5.48e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 5.48e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 5.48e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (corr officielle vs corr recalculée manuellement) : 5.48e-14
- **1/6714 désaccords de position** — tous localisés à un point où `corr(t)` tombe à <1e-10 du seuil de tercile (sensibilité de bord flottante documentée, PAS une fuite ni un bug de logique : confirmé).
- **OK**

## Anti-lookahead (NDX, troncature à 5621 séances, 2000 séances après le début des données DAX valides à l'index 3621)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
