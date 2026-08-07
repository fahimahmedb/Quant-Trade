# Audit — Rotation sectorielle défensive (XLP/XLK, log-return 21j)

## Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel, intersection stricte des deux séries) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel, intersection stricte des deux séries) : 0.00e+00
- **3/6907 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#352) : confirmé.
- **OK**

## Russell 2000
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel, intersection stricte des deux séries) : 0.00e+00
- **3/6907 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#352) : confirmé.
- **OK**

## S&P 500
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel, intersection stricte des deux séries) : 0.00e+00
- **3/6907 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#352) : confirmé.
- **OK**

## DAX
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel, intersection stricte des deux séries) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage causal d'un jour (transition 2026-08-05→2026-08-06)
- Ratio brut jour précédent (2026-08-05) = 0.458986, ratio brut jour de la transition (2026-08-06) = 0.459235 (valeurs distinctes vérifiées : OUI)
- **OK — transition non aveugle confirmée**

## Anti-lookahead (NDX, troncature à 5365 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
