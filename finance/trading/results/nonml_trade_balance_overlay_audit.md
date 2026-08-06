# Audit — Balance commerciale US (FRED BOPGSTB)

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
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage de 2 mois (transition autour de 2026-08-01)
- Valeur mois précédent (obs 2026-05-01) = -77647, valeur dernier mois disponible (obs 2026-06-01) = -73261 (valeurs distinctes vérifiées : OUI)
- BOPGSTB_lag(2026-07-31) = -77647, BOPGSTB_lag(2026-08-01) = -77647 (doivent valoir -77647, JAMAIS -73261)
- BOPGSTB_lag(2026-08-02) = -73261, BOPGSTB_lag(2026-08-03) = -73261 (2026-08-02 doit être le premier jour où -73261 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Vérification dédiée du taux de coupure élevé sur NDX/Russell/S&P500 (77,7%)
- BOPGSTB_lag sur la fenêtre NDX : 1re valeur disponible=-2026, médiane des 20% premières valeurs=-7887, médiane des 20% dernières valeurs=-63925
- Le déficit médian récent (-63925) est bien plus négatif que le déficit médian ancien (-7887) : confirme un creusement séculaire du déficit commercial US sur l'historique testé, ce qui ancre mécaniquement le seuil expanding vers des valeurs de moins en moins atteignables par les observations anciennes — la porte reste donc majoritairement active en fin d'échantillon, effet structurel de tendance (même famille que les effets de fenêtre courte déjà documentés #286/#289/#294/#295/#324), pas un bug de calcul.
- **OK — comportement confirmé cohérent avec la donnée réelle, aucune anomalie de calcul**

## Anti-lookahead (NDX, troncature à 3622 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
