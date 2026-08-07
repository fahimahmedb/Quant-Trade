# Audit — Momentum de l'or (GLD, log-return 21j)

## Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/1229 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#347) : confirmé.
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
- **1/5472 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#347) : confirmé.
- **OK**

## Vérification spécifique du décalage causal d'un jour (transition 2026-07-10→2026-07-13, séances 10271→10272)
- GoldMom brut séance précédente (2026-07-10) = -0.035873, GoldMom brut séance de la transition (2026-07-13) = -0.020089 (valeurs distinctes vérifiées : OUI)
- GoldMom_lag séance 10272 (2026-07-13) = -0.035873 (doit valoir -0.035873, JAMAIS -0.020089)
- **OK — le décalage d’un jour est correctement appliqué**

## Anti-lookahead (NDX, troncature à 6350 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
