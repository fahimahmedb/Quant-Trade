# Analyse — Levier optimal de Kelly (continu) sur NDX / Composite

f* = μ_annualisé (fenêtre expansive, causal) / σ²_annualisé (GJR-GARCH(1,1)-t walk-forward, Étape C, déjà validé). Plafond CAP=3.0 fixé a priori. Kelly plein ET demi-Kelly testés (le plein Kelly est connu pour être très sensible au bruit d'estimation de μ — ceci n'est pas une découverte a posteriori, c'est pourquoi les deux variantes sont rapportées dès le départ).

| Marché | Variante | Sharpe ann. | Calmar | MDD % | Rdt ann. % | Expo moy. | Expo max |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | BuyHold | +0.78 | +0.62 | -24.3 | +18.9 | 1.00× | 1.00× |
| Composite (5 ans) | Kelly plein | +0.38 | +0.35 | -35.5 | +16.6 | 2.10× | 3.00× |
| Composite (5 ans) | Demi-Kelly | +0.11 | +0.09 | -26.4 | +2.9 | 1.30× | 3.00× |
| NDX (40 ans) | BuyHold | +0.52 | +0.08 | -82.9 | +14.5 | 1.00× | 1.00× |
| NDX (40 ans) | Kelly plein | +0.70 | +0.16 | -89.0 | +42.5 | 2.49× | 3.00× |
| NDX (40 ans) | Demi-Kelly | +0.65 | +0.21 | -66.8 | +25.8 | 1.86× | 3.00× |

**Lecture honnête** : contrairement au vol-targeting (Étape D), le levier de Kelly dépend directement de μ estimé — un estimateur bien plus bruité que la volatilité. Une exposition moyenne élevée ici reflète surtout la prime de risque actions historique moyenne sur la fenêtre, pas une compétence de timing. À interpréter comme un choix d'ALLOCATION (accepter plus de risque pour plus de rendement espéré), pas comme un signal prédictif.
