# Pré-enregistrement — Leaders 52-semaines + overlay union des deux meilleurs signaux de tendance (SMA200 ∪ 52w-high indice)

**Committé AVANT tout calcul.** Cycle #41 du backlog non-ML. Combine le
portefeuille Leaders (#4) avec l'UNION des deux signaux de tendance les
plus performants du backlog en solo : SMA200 (#29/#33) et proximité du
plus haut 52-semaines indice (#37/#38, meilleur résultat du backlog).
Teste si l'union apporte un gain net (comme au #21, union calendaire sur
Buy&Hold, PASS) ou dilue l'edge par sur-exposition (comme au #32, union
à 3 signaux sur Buy&Hold, robustesse dégradée à fort CAP à cause d'une
exposition quasi permanente ~90%).

## Hypothèse

Puisque le signal 52w-high seul (#38) bat déjà nettement le SMA200 seul
(#33) en combinaison avec Leaders, l'union des deux pourrait soit
apporter un gain marginal supplémentaire (si les deux signaux capturent
des régimes légèrement différents), soit ne rien ajouter au-delà de ce
que le 52w-high seul apporte déjà (si les deux signaux sont fortement
corrélés, ce qui est plausible car tous deux mesurent une forme de
tendance haussière de l'indice).

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Leaders 52-semaines, IDENTIQUE au cycle #4.
- Signal A = indice NDX-100 au-dessus de sa SMA200 (identique au #29).
- Signal B = indice NDX-100 dont la clôture est ≥ 95% de son plus haut
  glissant 252j (identique au #37).
- Overlay = position de base **× CAP=2.0x** durant les jours où le
  signal A **OU** le signal B est actif (union), position de base ×1.0
  sinon. Alignement causal par ffill (même méthode qu'aux #33/#38).
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Leaders 1.0x (cycle #4), PAS Buy&Hold —
  même convention que #11/#23/#33/#35/#38/#39.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour les deux signaux de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Leaders de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x, paramètres des deux signaux
identiques à #29/#37, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_leaders_trend_union_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py leaders_trend_union_overlay`.
