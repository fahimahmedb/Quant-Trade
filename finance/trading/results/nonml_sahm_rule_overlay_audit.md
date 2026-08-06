# Audit — Règle de Sahm en temps réel (FRED SAHMREALTIME)

## Composite (5 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (seuil fixe recalculé indépendamment) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (seuil fixe recalculé indépendamment) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (seuil fixe recalculé indépendamment) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (seuil fixe recalculé indépendamment) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (seuil fixe recalculé indépendamment) : 0.00e+00
- **OK**

## Vérification spécifique du décalage d'un mois (transition autour de 2026-07-01)
- Valeur mois précédent (obs 2026-05-01) = 0.100000, valeur dernier mois disponible (obs 2026-06-01) = 0.070000 (valeurs distinctes vérifiées : OUI)
- SahmRule_lag(2026-06-30) = 0.100000, SahmRule_lag(2026-07-01) = 0.100000 (doivent valoir 0.100000, JAMAIS 0.070000)
- SahmRule_lag(2026-07-02) = 0.070000, SahmRule_lag(2026-07-03) = 0.070000 (2026-07-02 doit être le premier jour où 0.070000 apparaît, via shift(1))
- **OK — la valeur décalée change bien au jour attendu, cohérent avec le décalage attendu**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
