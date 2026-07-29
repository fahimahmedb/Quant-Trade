# Pré-enregistrement — Analyse de sensibilité du seuil DSR (Règle 9e)

**Committé AVANT tout calcul.** Cycle #116 du backlog non-ML. Ce cycle
N'EST PAS un nouveau backtest PASS/FAIL — c'est une analyse
méthodologique sur des résultats DÉJÀ committés (#111-115), utilisant
les fonctions déjà validées `dsr()`/`expected_max_sharpe()`
(`src/prediction.py`). Aucune nouvelle donnée de marché.

## Question posée (fixée ici, avant tout calcul)

À `n_trials=110` (Règle 9e), quel Sharpe journalier faudrait-il pour
qu'un candidat atteigne `DSR > 0,95`, compte tenu de la taille
d'échantillon (T) et de la forme de distribution (skew/kurtosis)
réellement observées sur les candidats déjà testés (#111-115) ? Ce
Sharpe minimal requis est-il plausible pour une stratégie directionnelle
quotidienne sur indice, au regard de références académiques connues
(prime de risque actions, facteurs Fama-French, CTA/trend-following) ?

## Méthode (fixée ici)

1. Pour chaque candidat déjà committé avec un artefact `_pnl.npz`
   (#111 à #115), recalculer via `dsr()` le Sharpe journalier minimal
   `sr_min` tel que `DSR(sr_min, T, var_trials, n_trials=110, skew,
   kurt) = 0,95` (recherche par bissection, pas d'optimisation cachée —
   fonction monotone croissante en `sr_hat_daily`).
2. Convertir `sr_min` en Sharpe annualisé (`sr_min * sqrt(252)`) pour
   comparaison intuitive à la littérature.
3. Comparer à des repères académiques CONNUS AVANT ce calcul (pas
   choisis après coup) : prime de risque actions long terme
   (Sharpe annualisé actions US ≈ 0,4-0,5), facteurs Fama-French
   value/momentum (≈ 0,3-0,5), CTA/trend-following systématique
   (≈ 0,5-0,8), meilleurs fonds quantitatifs multi-stratégies
   (Renaissance Medallion et exceptions similaires, >2 mais à fréquence
   et diversification sans rapport avec un signal quotidien unique sur
   un seul indice).

## Ce que cette analyse NE fait PAS

Elle ne change RIEN à la Règle 9e ni au verdict déjà rendu sur #111-115
(ils restent FAIL sous la barre actuelle). Elle documente une tension
méthodologique déjà pressentie (var_trials sous-estimée, n_trials=110
peut-être mal calibré pour CE type de stratégie), sans l'utiliser comme
prétexte pour assouplir la barre — toute décision de modifier la Règle 9
nécessiterait une justification séparée, explicite, et l'accord de
l'utilisateur.

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat.
