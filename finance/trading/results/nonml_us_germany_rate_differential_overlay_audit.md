# Audit — Différentiel de taux US-Allemagne (DGS10-DE10Y)

## Composite (5 ans)
- Écart max DGS10_lag (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max DE10Y_lag (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- **1/1250 désaccords de position** — tous localisés à un point où `RateDiff(t)` tombe à <1e-10 du seuil de tercile alors que les DONNÉES sous-jacentes (DGS10_lag, DE10Y_lag) sont identiques à la machine près — sensibilité de bord flottante du calcul de percentile lui-même (même pattern que le #193/DAX), PAS une fuite ni un désaccord de données : confirmé.
- **OK**

## NDX (40 ans)
- Écart max DGS10_lag (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max DE10Y_lag (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max DGS10_lag (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max DE10Y_lag (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max DGS10_lag (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max DE10Y_lag (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max DGS10_lag (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max DE10Y_lag (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Vérification spécifique du décalage d'un mois (mai 2026)
- Valeur DE10Y mai 2026 dans la source brute : 3.0465
- DE10Y_lag(15 mai) = nan, DE10Y_lag(31 mai) = 3.001 (doivent être NaN ou la valeur d'avril, JAMAIS mai)
- DE10Y_lag(1 juin) = 3.001, DE10Y_lag(2 juin) = 3.0465 (le 2 juin doit être le premier jour où mai apparaît, via shift(1))
- **OK — la valeur de mai apparaît uniquement à partir du 2 juin, jamais avant**

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
