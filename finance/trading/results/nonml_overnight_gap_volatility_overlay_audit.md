# Audit — Volatilité du gap d'ouverture (composante overnight isolée)

## Composite (5 ans)
- Écart max GapVol_lag (pandas rolling().mean() vs boucle explicite) : 1.42e-15
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max GapVol_lag (pandas rolling().mean() vs boucle explicite) : 1.51e-15
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max GapVol_lag (pandas rolling().mean() vs boucle explicite) : 5.21e-15
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max GapVol_lag (pandas rolling().mean() vs boucle explicite) : 2.29e-14
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max GapVol_lag (pandas rolling().mean() vs boucle explicite) : 1.30e-15
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Observation méthodologique — précision des données S&P 500 1970-1980
- GapVol_ann moyen 1970-1980 : 0.0007 (quasi nul)
- GapVol_ann moyen 2000+ : 0.0875
- **Constat, pas un bug** : les données OHLC S&P 500 les plus anciennes (arrondies plus grossièrement) produisent une variance Parkinson quasiment identique à la variance close-to-close totale, laissant un résidu "gap" quasi nul sur cette période — ceci ancre le seuil de tercile EXPANDING à un niveau structurellement bas, ce qui explique la fraction de temps coupé élevée (69,5%) observée pour ce marché dans le résultat principal. Il ne s'agit PAS d'une fuite (le calcul reste causal à chaque instant) mais d'un artefact de la NON-STATIONNARITÉ de la précision des données sous-jacentes interagissant avec un seuil expanding — signalé honnêtement, aucune correction appliquée après avoir vu ce résultat (Règle 2).

## Anti-lookahead (NDX, troncature à 2000 séances)
- Écart max position[0:2000] pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
