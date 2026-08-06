# Audit — Nouvelles commandes de biens durables US (FRED DGORDER)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **4/1250 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#320/#321) : confirmé.
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
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
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage d'un mois (transition autour de 2026-07-01)
- Valeur mois précédent (obs 2026-05-01) = -0.030174, valeur dernier mois disponible (obs 2026-06-01) = 0.073141 (valeurs distinctes vérifiées : OUI)
- DGOGrowth_lag(2026-06-30) = -0.030174, DGOGrowth_lag(2026-07-01) = -0.030174 (doivent valoir -0.030174, JAMAIS 0.073141)
- DGOGrowth_lag(2026-07-02) = 0.073141, DGOGrowth_lag(2026-07-03) = 0.073141 (2026-07-02 doit être le premier jour où 0.073141 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Anti-lookahead (NDX, troncature à 3874 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
