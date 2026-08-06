# Audit — Déficit budgétaire fédéral US (FRED MTSDS133FMS)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift/rolling vs boucle+searchsorted manuel) : 4.66e-10
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift/rolling vs boucle+searchsorted manuel) : 4.66e-10
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift/rolling vs boucle+searchsorted manuel) : 4.66e-10
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift/rolling vs boucle+searchsorted manuel) : 4.66e-10
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift/rolling vs boucle+searchsorted manuel) : 4.66e-10
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage d'un mois (transition autour de 2026-07-01)
- DeficitTTM mois précédent (obs 2026-05-01) = -1657193, DeficitTTM dernier mois disponible (obs 2026-06-01) = -1804508 (valeurs distinctes vérifiées : OUI)
- DeficitTTM_lag(2026-06-30) = -1657193, DeficitTTM_lag(2026-07-01) = -1657193 (doivent valoir -1657193, JAMAIS -1804508)
- DeficitTTM_lag(2026-07-02) = -1804508, DeficitTTM_lag(2026-07-03) = -1804508 (2026-07-02 doit être le premier jour où -1804508 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Vérification dédiée du taux de coupure élevé sur NDX (65,8%)
- DeficitTTM_lag sur la fenêtre NDX : médiane des 20% premières valeurs=-215589 M$, médiane des 20% dernières valeurs=-1734189 M$
- Le déficit cumulé médian récent est bien plus négatif (creusement confirmé) que le déficit cumulé médian ancien : confirme un creusement séculaire réel du déficit fédéral US sur l'historique testé, ancrant mécaniquement le seuil expanding vers des valeurs de moins en moins atteignables par les observations anciennes — même mécanisme de tendance déjà documenté au #327 (balance commerciale) et #331 (TCU), pas un bug de calcul.
- **OK — comportement confirmé cohérent avec la donnée réelle, aucune anomalie de calcul**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
