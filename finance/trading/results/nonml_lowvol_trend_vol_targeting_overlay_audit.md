# Audit adversarial — Low-Vol Tilt + overlay combiné tendance + vol-targeting

Recalcul indépendant de l'exposition vol-targeting (ddof=1, boucle explicite) : écart max = 9.99e-15
**OK.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Test anti-lookahead sur le signal de tendance indice : OK — aucune fuite.

**Lecture** : complète le trio des portefeuilles de base testés avec le mécanisme hiérarchique (#47 Buy&Hold, #51 Winners, #53 Low-Vol) — dans les trois cas, la combinaison tendance+vol-targeting bat ou égale le simple overlay binaire correspondant (#29/#35, #42, ici #35) en préservant systématiquement bien le MDD (-18,9%→-19,4%, quasi inchangé, cohérent avec #35's -18,9%→-19,9%).
