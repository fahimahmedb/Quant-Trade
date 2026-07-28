# Audit adversarial — Momentum court terme (winners)

Sharpe +2.35 est un chiffre extrême, audit renforcé (le projet flague tout Sharpe >3 comme suspect ; 2.35 en est assez proche pour justifier une vérification approfondie).

## 1. Recalcul indépendant du signal (pandas.pct_change vs numpy manuel)

Écart maximum sur 132347 valeurs comparables : 0.00e+00
**OK — méthodes concordantes.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur un signal antérieur à la mutation : 0.00e+00
**OK — aucune fuite.**

## 3. Concentration du panier "winners"

Top 10 titres les plus fréquents : [('APP', 126), ('LRCX', 126), ('MU', 125), ('NVDA', 123), ('PLTR', 122), ('CRWD', 119), ('STX', 119), ('MRVL', 118), ('DDOG', 117), ('MSTR', 116)]
Part des 10 titres les plus fréquents dans le total des sélections : 13.2%

**Concentration limitée, résultat probablement diffus.**

## 4. Titres les plus extrêmes sur toute la période (rendement total individuel)

[('SNDK', '+3451%'), ('NVDA', '+1399%'), ('STX', '+1260%'), ('WDC', '+1161%'), ('MU', '+1116%')]
Contexte : NDX-100 2021-2026 inclut des titres IA/semi-conducteurs à très forte hausse (ex. NVDA) -- un signal momentum qui capte systématiquement ces titres explique une part significative du Sharpe élevé, cohérent avec le marché haussier concentré de cette période plutôt qu'un edge généralisable.
