# Audit — Momentum du Bitcoin (CBBTCUSD, log-return 21j)

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

## Vérification spécifique du décalage causal d'un jour (transition 2026-07-10→2026-07-13, séances 10271→10272)
- BTCmom brut séance précédente (2026-07-10) = 0.036648, BTCmom brut séance de la transition (2026-07-13) = 0.010715 (valeurs distinctes vérifiées : OUI)
- BTCmom_lag séance 10272 (2026-07-13) = 0.036648 (doit valoir 0.036648, JAMAIS 0.010715)
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 8875 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
