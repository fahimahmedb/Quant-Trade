# Pré-enregistrement — Overlay de tendance par le TEMPS depuis le dernier plus haut

**Committé AVANT tout calcul.** Cycle #91 du backlog non-ML.

## Hypothèse

Le #37 (PASS 5/5) mesure la proximité en NIVEAU au plus haut glissant
252j (`close ≥ 95% du plus haut`). Ce cycle teste une dimension
TEMPORELLE distincte : la DURÉE écoulée depuis le dernier plus haut
historique (nombre de séances consécutives sans nouveau sommet, concept
de "temps sous l'eau"/drawdown duration). Un titre peut être proche en
niveau de son plus haut (#37 actif) tout en étant "sous l'eau" depuis
longtemps (stagnation proche du sommet), ou au contraire enchaîner des
plus hauts fréquents (progression continue) — ce sont deux informations
différentes. L'hypothèse est qu'une récence élevée de nouveaux sommets
(peu de jours écoulés depuis le dernier plus haut) signale une
dynamique haussière plus vigoureuse qu'une simple proximité de niveau.

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #9/#29/#31/#37/#43.
- Plus haut = plus haut HISTORIQUE (maximum expansif du prix de clôture
  depuis le début de la série, pas glissant sur une fenêtre — capture
  la notion réelle de "dernier record absolu").
- `days_since_high(t)` = nombre de séances écoulées depuis le dernier
  jour où `close` a établi un nouveau plus haut historique (0 si t
  lui-même est un nouveau plus haut).
- Porte active si `days_since_high(t-1) ≤ THRESHOLD_DAYS=63` (environ
  un trimestre, ordre de grandeur déjà utilisé dans ce backlog pour les
  fenêtres de simulation courtes, fixé ici a priori — pas un retuning).
- Position : **CAP=2.0x** les jours de porte active, **1.0x** sinon
  (overlay binaire simple, mécanisme identique au #29/#37, pas le
  vol-targeting hiérarchique).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #9/#29/#31/#37). n_trials=1
(THRESHOLD_DAYS=63j fixé ici a priori, CAP=2.0x identique à la famille,
aucune grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant `nonml_days_since_high_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py days_since_high_overlay`.
