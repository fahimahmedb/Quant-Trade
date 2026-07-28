# Audit adversarial — Leaders 52-semaines + overlay proximité plus haut 52-semaines indice

Écart maximum sur l'exposition totale (jours avec position) : 2.22e-16
**OK — exposition exactement conforme.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Recalcul indépendant du signal 52w-high (boucle explicite vs pandas.rolling.max) : 0 écarts. **OK.**

Test anti-lookahead sur le signal de tendance indice : OK — aucune fuite.

**Lecture** : le résultat est exceptionnellement fort (Sharpe +0,78→+1,50, rendement +81,6%→+508,3%) mais le MDD reste quasi identique (-25,7%→-25,9%) -- cohérent avec le mécanisme : ce signal coupe le levier avant le portefeuille Leaders lui-même ne s'effondre, contrairement à une exposition constante. Cette force du résultat justifie une attention particulière lors de la robustesse (grille CAP ET grille de seuil) avant de considérer ce résultat comme définitivement solide.
