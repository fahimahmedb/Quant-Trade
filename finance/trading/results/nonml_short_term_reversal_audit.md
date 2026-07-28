# Audit adversarial — Reversal court terme (1 semaine)

## 1. Recalcul indépendant du signal (pandas.pct_change vs numpy manuel)

Écart maximum sur 132347 valeurs comparables : 0.00e+00
**OK — méthodes concordantes.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur un signal antérieur à la mutation : 0.00e+00
**OK — aucune fuite.**

## 3. Concentration du panier "losers" (surreprésentation de quelques titres ?)

Titres les plus fréquents dans le panier losers sur toute la période : [('MSTR', 133), ('PDD', 123), ('WBD', 123), ('KHC', 121), ('TSLA', 121)]
Part des 5 titres les plus fréquents dans le total des sélections : 6.7%

**Concentration limitée, résultat probablement diffus sur beaucoup de titres.**
