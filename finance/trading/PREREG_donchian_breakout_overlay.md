# Pré-enregistrement — Overlay levé breakout de Donchian (20 séances)

**Committé AVANT tout calcul.** Cycle #40 du backlog non-ML. Signal de
suivi de tendance à horizon COURT (20 séances, ~1 mois), très différent
des signaux longs déjà testés (SMA200/#29, Golden Cross/#34, 52w-high
252j/#37). Le canal de Donchian (Turtle Traders, Dennis & Eckhardt
1983) est un classique du suivi de tendance systématique.

## Hypothèse

Une clôture qui dépasse (ou égale) le plus haut des 20 dernières séances
signale un breakout de tendance à court terme — un overlay levé sur ce
signal pourrait capturer une continuation de mouvement, à un horizon
beaucoup plus réactif que les signaux 200j/252j déjà testés (risque de
plus de faux signaux, comme observé au #36/MACD, à confirmer ou infirmer
ici).

## Définition (fixée ici, avant tout résultat)

- Canal de Donchian = plus haut glissant des 20 dernières clôtures
  (fenêtre causale).
- Régime "breakout" = clôture du jour t **≥** son plus haut glissant
  20j (canal atteint ou dépassé).
- Position = **1.0x en permanence**, SAUF les jours en régime
  "breakout" où position = **CAP = 2.0x**. Décision prise à la clôture
  de t, appliquée au rendement t→t+1.
- Échantillon testable = à partir de la 21e séance.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x et fenêtre 20j = paramètre standard
Turtle Traders, fixés a priori, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_donchian_breakout_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py donchian_breakout_overlay`.
