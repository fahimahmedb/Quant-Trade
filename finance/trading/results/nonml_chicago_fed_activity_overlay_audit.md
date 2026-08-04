# Audit — Indice d'activité nationale de la Fed de Chicago (CFNAI)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
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
- **14/6776 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#204/#205) : confirmé.
- **OK**

## Vérification spécifique du décalage d'un mois (mai 2026)
- Valeur CFNAI mai 2026 dans la source brute : -0.19
- CFNAI_lag(15 mai) = nan, CFNAI_lag(31 mai) = 0.05 (doivent être la valeur d'avril, JAMAIS mai)
- CFNAI_lag(1 juin) = 0.05, CFNAI_lag(2 juin) = -0.19 (le 2 juin doit être le premier jour où mai apparaît, via shift(1))
- **OK — la valeur de mai apparaît uniquement à partir du 2 juin, jamais avant**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
