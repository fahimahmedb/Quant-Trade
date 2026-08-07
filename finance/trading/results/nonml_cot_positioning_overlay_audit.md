# Audit — Positionnement spéculatif net CFTC (COT, NASDAQ-100)

## Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/1250 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#359) : confirmé.
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/4038 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#359) : confirmé.
- **OK**

## Russell 2000
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/4038 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#359) : confirmé.
- **OK**

## S&P 500
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/4038 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#359) : confirmé.
- **OK**

## DAX
- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/4073 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/.../#359) : confirmé.
- **OK**

## Vérification spécifique du décalage de publication (5j) + causal (1j)
- Dernière observation « en date du » 2026-07-28 = -3.100295 (observation précédente 2026-07-21 = -3.110846, valeurs distinctes : OUI)
- Date de disponibilité déclarée (as_of + 5j) = 2026-08-02
- NetPctSpéc_lag(2026-08-02) = -3.110846 (doit valoir -3.110846, JAMAIS -3.100295 — la valeur n'est censée devenir visible qu'au jour SUIVANT sa disponibilité, via shift(1))
- NetPctSpéc_lag(2026-08-03) = -3.100295 (doit être le premier jour où -3.100295 apparaît)
- **OK — le décalage de publication + causal est correctement appliqué**

## Anti-lookahead (NDX, troncature à 7734 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
