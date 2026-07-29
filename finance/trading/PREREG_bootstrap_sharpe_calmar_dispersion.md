# Pré-enregistrement — Intervalle de confiance bootstrap (Sharpe, Calmar) du #121

**Committé AVANT tout calcul.** Cycle #125 du backlog non-ML. Analyse
méthodologique sur le résultat DÉJÀ committé du #121 (meilleur
candidat, ensemble à 2 moteurs #115+GARCH), pas un nouveau backtest.

## Question posée (fixée ici, avant tout calcul)

Le SPA teste si le #121 bat SIGNIFICATIVEMENT Buy&Hold (réponse déjà
connue : non, p=0,45). Cette analyse mesure une chose DIFFÉRENTE et
complémentaire : quelle est la DISPERSION (incertitude d'estimation)
du Sharpe et du Calmar du #121 lui-même, indépendamment de la
comparaison au benchmark ? Un intervalle de confiance bootstrap large
signale un résultat fragile (sensible à quelles séances précises
composent l'échantillon), même si le point estimé est positif.

## Méthode (fixée ici)

- Bootstrap stationnaire de Politis-Romano (`src/volatility.py::
  _stationary_bootstrap_idx`, déjà implémenté et utilisé par
  `spa_test`, mêmes paramètres par défaut : `mean_block=20`, aucun
  retuning).
- `B=2000` répétitions (fixé ici, pas ajusté après avoir vu un
  résultat).
- Pour chaque répétition : ré-échantillonne le pnl quotidien du #121
  (`nonml_dual_engine_defensive_overlay_pnl.npz`) ET celui de Buy&Hold
  (même trajectoire d'indices ré-échantillonnés, pour préserver la
  corrélation entre les deux séries), recalcule Sharpe annualisé et
  Calmar pour les deux.
- Rapporte les intervalles [2,5e percentile, 97,5e percentile] (IC 95%)
  du Sharpe et du Calmar de l'overlay, ET de la DIFFÉRENCE
  (Sharpe_overlay - Sharpe_BH, Calmar_overlay - Calmar_BH) sur les
  mêmes répétitions bootstrap.

## Ce que cette analyse NE fait PAS

Ne change pas le verdict Règle 9 du #121 (reste FAIL, SPA/DSR déjà
tranchés). N'est pas un nouveau test de significativité formel (le SPA
reste la référence pour ça) — une mesure de dispersion descriptive,
complémentaire.

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat
(B et mean_block fixés avant tout calcul, pas ajustés après coup).
