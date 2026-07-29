# Pré-enregistrement — Overlay combiné tendance + vol-targeting

**Committé AVANT tout calcul.** Cycle #47 du backlog non-ML. Combine les
deux mécanismes gagnants de la session : le filtre de tendance 52w-high
indice (#37/#38, meilleur signal de tendance du backlog) et le
vol-targeting continu calibré (#46, cible 20%, PASS). Contrairement à
une simple union de deux overlays binaires (déjà testée et jugée sans
valeur ajoutée au #41), ce cycle teste une combinaison HIÉRARCHIQUE :
le vol-targeting ne s'applique QUE lorsque la tendance est haussière.

## Hypothèse

Le vol-targeting seul (#46) accepte de réduire l'exposition sous 1.0x
même en période de tendance haussière (si la vol ponctuelle est
élevée), ce qui peut coûter du rendement inutilement. En limitant le
mécanisme de vol-targeting à agir UNIQUEMENT comme amplificateur (jamais
en-dessous de 1.0x) et SEULEMENT pendant les régimes de tendance
haussière confirmés (#37), l'overlay pourrait combiner le meilleur des
deux mécanismes : rester investi à 1.0x minimum en toute circonstance
(comme les overlays #29/#37/#38 qui ont le mieux fonctionné), et
moduler l'amplification selon la vol réalisée plutôt qu'un CAP fixe.

## Définition (fixée ici, avant tout résultat)

- Signal de tendance = indice au-dessus de son plus haut glissant 252j
  à ≥95% (identique au #37).
- Vol réalisée = écart-type des rendements log quotidiens sur 20
  séances, annualisée, calcul causal identique au #43/#46.
- Vol cible = **20% annualisé** (identique au #46).
- Position(t) :
  - si tendance haussière : **clip(vol_cible / vol_réalisée(t-1), 1.0,
    CAP=2.0)** (jamais en-dessous de 1.0x, amplification module par la
    vol).
  - sinon : **1.0x** (pas de réduction sous 1.0x hors tendance
    haussière — différent du #43/#46 qui pouvaient descendre à 0.0).
- Échantillon testable = à partir de la 253e séance (contrainte du
  signal de tendance 252j).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (tous les paramètres repris identiques aux
#37/#46, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_trend_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py trend_vol_targeting_overlay`.
