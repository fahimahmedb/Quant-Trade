# Audit — Taux d'utilisation des capacités industrielles US (FRED TCU)

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

## Vérification spécifique du décalage d'un mois (transition autour de 2026-07-01)
- Valeur mois précédent (obs 2026-05-01) = 76.1019, valeur dernier mois disponible (obs 2026-06-01) = 76.0937 (valeurs distinctes vérifiées : OUI)
- TCU_lag(2026-06-30) = 76.1019, TCU_lag(2026-07-01) = 76.1019 (doivent valoir 76.1019, JAMAIS 76.0937)
- TCU_lag(2026-07-02) = 76.0937, TCU_lag(2026-07-03) = 76.0937 (2026-07-02 doit être le premier jour où 76.0937 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Vérification dédiée du taux de coupure élevé sur Composite (73,9%)
- TCU_lag sur la fenêtre Composite : valeur de départ=77.34, pic=79.04 (atteint après 203 séances sur 1250, donc en cours de fenêtre, PAS au tout début), médiane après le pic=76.40
- **Première hypothèse (valeur de départ proche du maximum) INFIRMÉE** par inspection directe des données mensuelles brutes : le TCU monte d'abord de ~77,3 (juin 2021) à un pic de 79,04 (avril 2022), PUIS décline graduellement à ~75-76 (2023-2026) — schéma pic-puis-déclin, pas un point de départ élevé.
- La médiane post-pic (76.40) est bien inférieure au pic (79.04) : confirme que le déclin graduel post-avril 2022 (ralentissement réel de l'activité manufacturière US documenté sur cette période) alimente continuellement le tercile expanding le plus bas avec de nouvelles valeurs record-basses relativement à l'historique vu jusque-là, expliquant mécaniquement le taux de coupure élevé — effet de tendance réel, pas un bug de calcul, même famille que les effets de fenêtre courte déjà documentés sous d'autres formes (#286/#289/#294/#295/#324/#327).
- **OK — comportement confirmé cohérent avec la donnée réelle (déclin manufacturier post-2022), aucune anomalie de calcul**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
