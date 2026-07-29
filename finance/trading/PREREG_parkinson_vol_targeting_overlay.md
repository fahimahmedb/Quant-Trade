# Pré-enregistrement — Overlay de vol-targeting avec estimateur Parkinson

**Committé AVANT tout calcul.** Cycle #50 du backlog non-ML. Variante du
mécanisme de vol-targeting déjà validé (#46, cible 20%, PASS 4/5) :
remplace l'écart-type close-to-close par l'estimateur de volatilité
range-based de Parkinson (1980), DÉJÀ IMPLÉMENTÉ dans le projet
(`data_loader.parkinson_var_pct`, utilisé à l'Étape C) mais jamais
utilisé dans ce backlog non-ML jusqu'ici.

## Hypothèse

L'estimateur de Parkinson exploite l'écart haut-bas de chaque séance
(pas seulement la clôture), ce qui le rend statistiquement plus
efficace (moins de variance d'estimation) que l'écart-type
close-to-close à fenêtre égale — un signal de vol moins bruité pourrait
améliorer la stabilité de l'exposition et donc les métriques
risque/rendement de l'overlay.

**Mise en garde pré-enregistrée (documentée dans le code du projet)** :
l'estimateur de Parkinson ne capture PAS l'écart d'ouverture (overnight
gap), ce qui le biaise structurellement à la baisse par rapport à la
vol close-to-close réellement subie par un investisseur. Avec la même
cible de vol que le #46 (20%), ce biais pourrait mécaniquement gonfler
l'exposition moyenne au-dessus de celle du #46 — effet anticipé et
signalé ici AVANT le résultat, pas une explication a posteriori.

## Définition (fixée ici, avant tout résultat)

- Variance de Parkinson quotidienne = `data_loader.parkinson_var_pct`
  (fonction déjà existante et validée à l'Étape C, réutilisée telle
  quelle, aucune modification).
- Vol réalisée = racine de la moyenne roulante de la variance de
  Parkinson sur **20 séances**, convertie en fraction annualisée
  (× √252 / 100, la fonction retournant des %²), calcul causal (vol
  connue à t-1, position décidée pour t) — même fenêtre que #43/#46.
- Vol cible = **20% annualisé**, IDENTIQUE au #46 (pour isoler l'effet
  du seul changement d'estimateur, pas un nouveau calibrage).
- Position(t) = **clip(vol_cible / vol_réalisée_parkinson(t-1), 0.0,
  CAP=2.0)**.
- Échantillon testable = à partir de la 21e séance.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`), colonnes
high/low déjà chargées par `data_loader.load_ohlc`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (vol cible 20%, fenêtre 20j et CAP=2.0x identiques
au #46, seul l'estimateur de vol change, aucune grille testée avant ce
résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_parkinson_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py parkinson_vol_targeting_overlay`.
