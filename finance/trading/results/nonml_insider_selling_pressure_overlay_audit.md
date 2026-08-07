# Audit — Pression de vente nette des initiés (SEC Form 4, AAPL/MSFT/NVDA)

## Composite (5 ans)
- Écart max alignement causal (pandas rolling/reindex/ffill/shift vs boucle manuelle) : 1.79e-07
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## NDX (40 ans)
- Écart max alignement causal (pandas rolling/reindex/ffill/shift vs boucle manuelle) : 1.79e-07
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Russell 2000
- Écart max alignement causal (pandas rolling/reindex/ffill/shift vs boucle manuelle) : 1.79e-07
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## S&P 500
- Écart max alignement causal (pandas rolling/reindex/ffill/shift vs boucle manuelle) : 1.79e-07
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## DAX
- Écart max alignement causal (pandas rolling/reindex/ffill/shift vs boucle manuelle) : 1.79e-07
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

## Anti-lookahead (NDX, troncature à 8493 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Vérification du filtre qualité de données (prix > 5000$/action)
- Transactions avec prix > 5000$/action dans le fichier committé : 0 (doit valoir 0 — la transaction anormale MSFT du 01/09/2020 a déjà été exclue avant commit).
- **OK — filtre déjà appliqué en amont, aucune anomalie résiduelle**

## Verdict global : **CONFORME**
