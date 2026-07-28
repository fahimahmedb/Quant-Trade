# Audit adversarial — Overlay levé cycle électoral américain

## 1. Recalcul indépendant du masque + taille d'échantillon effective

| Marché | Écart masque (nb j.) | Nb années pré-électorales distinctes observées | Années |
|---|---|---|---|
| Composite (5 ans) | 0 | 1 | [2023] |
| NDX (40 ans) | 0 | 10 | [1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023] |
| Russell 2000 | 0 | 10 | [1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023] |
| S&P 500 | 0 | 14 | [1971, 1975, 1979, 1983, 1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023] |
| DAX | 0 | 7 | [1999, 2003, 2007, 2011, 2015, 2019, 2023] |

**OK — masque confirmé par recalcul indépendant, aucun bug de calcul.**

## 2. Lecture honnête de la puissance statistique

Le Composite (5 ans) ne couvre qu'une SEULE année pré-électorale partielle (2023, incomplète car l'échantillon démarre en juillet 2021) -- son PASS individuel n'a quasiment aucune valeur statistique isolée (n=1 épisode). Seul NDX (40 ans, ~10 épisodes complets) offre une puissance statistique réelle pour cette hypothèse ; Russell/S&P 500/DAX ont un historique long similaire à NDX et couvrent également plusieurs cycles complets. Le critère renforcé (≥4/5) reste techniquement atteint (5/5), mais la robustesse du signal doit être jugée principalement sur les 4 marchés à historique long, pas sur le Composite.
