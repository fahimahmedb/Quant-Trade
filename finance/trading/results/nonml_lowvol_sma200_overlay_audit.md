# Audit adversarial — Low-Vol Tilt + overlay SMA200

Écart maximum sur l'exposition totale (jours avec position) : 2.22e-16
**OK — exposition exactement conforme.**

Alignement calendaire (ffill causal) : 1386/1396 dates du portefeuille correspondent exactement à une séance de l'indice NDX-100 (99.3%).

Test anti-lookahead sur le signal de tendance indice : OK — aucune fuite.

**Lecture** : contrairement au #28 (overlay calendaire sur low-vol, Sharpe dégradé +0,54→+0,49), l'overlay de TENDANCE préserve bien le MDD défensif du portefeuille low-vol (-18,9%→-19,9%, quasi inchangé) tout en améliorant nettement Sharpe et rendement -- cohérent avec le mécanisme du filtre (il coupe le levier précisément en régime baissier, ce qu'un simple calendrier ne peut pas faire).
