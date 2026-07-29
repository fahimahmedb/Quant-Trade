# Audit adversarial — Momentum de constance + overlay combiné tendance + vol-targeting, cible 15%

Recalcul indépendant de l'exposition vol-targeting (ddof=1, boucle explicite) : écart max = 6.44e-15
**OK.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Test anti-lookahead sur le signal de tendance indice (SMA200) : OK — aucune fuite.

Exposition moyenne sur la période testable : 1.03x (exposition au plancher 1.0x 74.9% du temps).

**Lecture honnête** : confirme l'hypothèse pré-enregistrée dans le sens négatif attendu — abaisser la cible de vol de 20% (#85, exposition moyenne 1,17x, plancher actif 54,6% du temps) à 15% RÉDUIT encore l'exposition moyenne (1,03x, plancher actif 74,9% du temps) et AGGRAVE le rendement (+75,5%→+70,5%) tout en laissant le Sharpe quasi identique (+0,60). Contrairement à la logique #43→#46 (cible relevée pour corriger un SOUS-dimensionnement), le problème du #85/#88 n'est pas la valeur de la cible mais la faible volatilité PROPRE du portefeuille momentum de constance elle-même — aucune cible de vol-targeting ne peut remplacer l'amplitude d'un CAP fixe (#83, PASS) quand la vol réalisée reste structurellement sous la cible la plupart du temps. Aucun bug détecté (recalcul indépendant exact, alignement calendaire correct, absence de fuite).
