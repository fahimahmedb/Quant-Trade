# Audit — Croissance de la masse monétaire M2 (glissement annuel)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **8/1250 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200) : confirmé.
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **7/10272 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200) : confirmé.
- **OK**

## Russell 2000
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **3/6776 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200) : confirmé.
- **OK**

## Vérification spécifique du décalage d'un mois (mai 2026)
- M2Growth_lag(15 mai) = nan, M2Growth_lag(31 mai) = 0.04618193429857567 (doivent être la valeur d'avril ou plus ancienne, JAMAIS mai)
- M2Growth_lag(1 juin) = 0.04618193429857567, M2Growth_lag(2 juin) = 0.05433954697928857 (le 2 juin doit être le premier jour où mai apparaît, via shift(1))
- **OK — la valeur décalée change bien au 2 juin, cohérent avec le décalage attendu**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
