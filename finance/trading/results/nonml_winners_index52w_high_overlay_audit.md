# Audit adversarial — Winners momentum + overlay proximité plus haut 52-semaines indice

Écart maximum sur l'exposition totale (jours avec position) : 4.44e-16
**OK — exposition exactement conforme.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Recalcul indépendant du signal 52w-high (boucle explicite vs pandas.rolling.max) : 0 écarts. **OK.**

Test anti-lookahead sur le signal de tendance indice : OK — aucune fuite.

**Lecture** : contrairement au #18 (Winners + overlay ToM, FAIL, calendrier fixe sans lien avec le régime de marché), le filtre de tendance 52w-high réussit ici à améliorer encore un edge déjà extrême (Sharpe +2,35→+3,00) -- MAIS la **prudence forte** du #14 reste pleinement applicable : ce résultat est mesuré sur le même bull market concentré 2021-2026, sa généralisabilité hors de cet échantillon est incertaine, indépendamment de la solidité technique de l'overlay lui-même (confirmée par cet audit).
