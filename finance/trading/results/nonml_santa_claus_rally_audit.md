# Audit adversarial — Santa Claus Rally

## Vérification de la frontière d'année (deux méthodes indépendantes)

| Marché | Écart (nb jours) | Identique ? |
|---|---|---|
| Composite (5 ans) | 0 | OUI |
| NDX (40 ans) | 0 | OUI |
| Russell 2000 | 0 | OUI |
| S&P 500 | 0 | OUI |
| DAX | 0 | OUI |

**OK — méthodes concordantes, frontière décembre/janvier correctement gérée.**

**Note méthodologique (généralisable au-delà de ce cycle)** : sous la règle renforcée (Sharpe ET rendement absolu), toute stratégie investie seulement une petite fraction de l'année (ici ~7j/252 ≈ 2,8%) est structurellement quasi incapable de battre le rendement CUMULÉ de Buy&Hold sur un historique long, simplement parce qu'elle rate presque tout le compounding — indépendamment de la qualité de l'effet de calendrier lui-même. C'est cohérent avec l'échec similaire du cycle #2 (tournant de mois, ~33% du temps investi, déjà insuffisant). Les items #8/#9 du backlog (overlay avec levier au lieu d'être flat hors fenêtre) adressent structurellement ce problème.
