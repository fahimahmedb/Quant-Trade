# Audit adversarial — Momentum de constance + overlay combiné tendance + vol-targeting

Recalcul indépendant de l'exposition vol-targeting (ddof=1, boucle explicite) : écart max = 8.44e-15
**OK.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Test anti-lookahead sur le signal de tendance indice (SMA200) : OK — aucune fuite.

Exposition moyenne sur la période testable : 1.17x (exposition au plancher 1.0x 54.6% du temps).

**Lecture honnête** : contrairement aux trois autres portefeuilles de base testés avec ce même mécanisme hiérarchique (#47 Buy&Hold PASS, #51 Winners PASS, #53 Low-Vol PASS), le momentum de constance (#82) est ici le premier cas où le mécanisme hiérarchique sous-performe le simple overlay binaire équivalent (#83, PASS, Sharpe +0,90/rendement +256,4% à CAP fixe 2.0x) ET la référence 1.0x elle-même. Le portefeuille momentum de constance a une volatilité réalisée propre relativement modérée (sélection de titres à rendements mensuels consistants, par construction moins erratiques) : la modulation fine n'apporte pas ici le même bénéfice que sur des portefeuilles plus volatils (Winners #14) ou explicitement construits pour la faible vol (#15) — le simple CAP fixe (#83) capture mieux l'edge de tendance sur cette construction précise. Aucun bug détecté (recalcul indépendant exact, alignement calendaire correct, absence de fuite).
