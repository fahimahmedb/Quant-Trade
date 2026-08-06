# Audit — Taux d'épargne des ménages US (FRED PSAVERT)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/1250 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **3/9781 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

## S&P 500
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **44/14251 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

## DAX
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/6776 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

## Vérification dédiée du risque d'ancrage sur le pic COVID (déclaré au PREREG)
- Pic PSAVERT pendant 2020 (choc COVID) : 31.8%
- Maximum de PSAVERT après juin 2021 (post-choc) : 9.5%
- Le pic COVID (31.8%) est nettement supérieur au maximum observé depuis (post-COVID 9.5%) : confirme le risque déclaré à l'avance — le seuil expanding du tercile le plus haut reste ancré durablement sur cet épisode isolé, expliquant mécaniquement le taux de coupure très faible (7,9%-21,6%) et le MDD identique à Buy&Hold observés sur 4/5 marchés — effet de tendance de type ancrage sur événement extrême isolé, cohérent avec le risque explicitement anticipé dans le PREREG, pas un bug de calcul.
- **OK — comportement confirmé cohérent avec le risque anticipé au PREREG, aucune anomalie de calcul**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
