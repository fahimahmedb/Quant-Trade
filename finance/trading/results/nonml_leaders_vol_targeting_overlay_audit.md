# Audit adversarial — Leaders 52-semaines + overlay de vol-targeting continu

Recalcul indépendant de l'exposition (boucle explicite, ddof=1) : écart max = 1.22e-14
**OK.**

Exposition totale appliquée (jours avec position) : écart max = 4.44e-16
**OK — exposition exactement conforme.**

Test anti-lookahead (perturbation du futur) : OK — aucune fuite.

**Lecture** : même écueil qu'au #43 -- l'exposition moyenne (0,91x) reste sous 1.0x, ce qui pénalise le rendement composé même quand la vol-targeting s'applique à un portefeuille à edge positif (Leaders) plutôt qu'à un indice neutre. Le MDD est amélioré (-21,3%→-17,7%) mais insuffisant pour compenser la perte de rendement selon la règle renforcée.
