# Audit — Emplois non-agricoles US (FRED PAYEMS)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **11/10272 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#320/#321) : confirmé.
- **OK**

## Russell 2000
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **9/9781 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#320/#321) : confirmé.
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
- Valeur mois précédent (obs 2026-05-01) = 0.002703, valeur dernier mois disponible (obs 2026-06-01) = 0.003188 (valeurs distinctes vérifiées : OUI)
- PayrollsGrowth_lag(2026-06-30) = 0.002703, PayrollsGrowth_lag(2026-07-01) = 0.002703 (doivent valoir 0.002703, JAMAIS 0.003188)
- PayrollsGrowth_lag(2026-07-02) = 0.003188, PayrollsGrowth_lag(2026-07-03) = 0.003188 (2026-07-02 doit être le premier jour où 0.003188 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Vérification dédiée du taux de coupure élevé sur Composite (88,3%)
- PayrollsGrowth_lag sur la fenêtre Composite : min=0.0007, max=0.0575, 1re valeur disponible=0.0575 (rebond post-COVID 2021)
- La première valeur disponible est proche du maximum de toute la fenêtre (0.0575 vs max 0.0575) : confirme que le seuil expanding s'ancre sur le pic de rebond de l'emploi post-COVID de 2021, rendant la quasi-totalité de la croissance normale des années suivantes relativement 'basse' en comparaison — effet mécanique de fenêtre courte, pas un bug de calcul (même schéma déjà documenté aux #286/#289/#294/#295).
- **OK — comportement confirmé cohérent avec la donnée réelle, aucune anomalie de calcul**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
