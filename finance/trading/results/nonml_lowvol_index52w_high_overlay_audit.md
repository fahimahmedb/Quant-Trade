# Audit adversarial — Low-Vol Tilt + overlay proximité plus haut 52-semaines indice

Écart maximum sur l'exposition totale (jours avec position) : 2.22e-16
**OK — exposition exactement conforme.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Recalcul indépendant du signal 52w-high (boucle explicite vs pandas.rolling.max) : 0 écarts. **OK.**

Test anti-lookahead sur le signal de tendance indice : OK — aucune fuite.

**Lecture** : confirme le schéma déjà observé au #38 (Leaders) : le signal 52w-high indice, plus réactif que SMA200, préserve mieux le MDD du portefeuille de base (-18,9%→-19,9%, quasi identique à #35's -18,9%→-19,9%) tout en apportant un gain de Sharpe/rendement supérieur (+0,54→+0,95 contre +0,54→+0,79 au #35).
