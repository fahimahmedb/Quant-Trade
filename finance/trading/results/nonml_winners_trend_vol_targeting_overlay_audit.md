# Audit adversarial — Winners momentum + overlay combiné tendance + vol-targeting

Recalcul indépendant de l'exposition vol-targeting (ddof=1, boucle explicite) : écart max = 9.10e-15
**OK.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Test anti-lookahead sur le signal de tendance indice : OK — aucune fuite.

**Lecture** : le mécanisme hiérarchique préserve encore mieux le MDD que le simple overlay binaire du #42 (-22,4%→-22,4%, EXACTEMENT identique, contre -22,4%→-26,9% au #42) tout en améliorant Sharpe et rendement -- cohérent avec la modulation fine par la vol réalisée plutôt qu'un CAP fixe uniforme. **Prudence forte maintenue** : résultat mesuré sur le même bull market 2021-2026 que le #14/#42.
