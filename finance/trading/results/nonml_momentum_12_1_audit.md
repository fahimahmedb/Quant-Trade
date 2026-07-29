# Audit adversarial — Momentum 12-1 mois

## 1. Recalcul indépendant du signal (boucle numpy manuelle vs pandas.shift())

Écart maximum absolu sur 107895 valeurs comparables : 0.00e+00
**OK — méthodes concordantes.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur le signal calculé à un jour antérieur à la mutation (fenêtres SKIP=21j et LOOKBACK=252j n'incluant aucune donnée mutée) : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Taille de l'univers éligible au fil du temps

Min 91, max 99, médiane 95 titres cotés simultanément sur les 1396 séances — croissance progressive attendue (nouvelles entrées à l'indice/IPO), pas de saut suspect si la progression est monotone-ish.
