# Audit — Momentum de l'Ethereum (CBETHUSD, log-return 21j)

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
- ETHmom brut séance précédente (2026-07-10) = 0.088915, ETHmom brut séance de la transition (2026-07-13) = 0.088847 (valeurs distinctes vérifiées : OUI)
- ETHmom_lag séance 10272 (2026-07-13) = 0.088915 (doit valoir 0.088915, JAMAIS 0.088847)
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 9243 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
