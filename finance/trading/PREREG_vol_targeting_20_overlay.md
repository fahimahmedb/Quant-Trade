# Pré-enregistrement — Overlay de vol-targeting continu, cible 20%

**Committé AVANT tout calcul.** Cycle #46 du backlog non-ML. Dernier
item de la file actuelle. Variante du cycle #43 (vol-targeting continu,
vol cible 15%, FAIL 3/5 sur le rendement, exposition moyenne souvent
<1x) et du #45 (même mécanisme sur Leaders, FAIL). Hypothèse
MÉCANIQUEMENT DISTINCTE et nouvellement pré-enregistrée (pas un
retuning du #43) : teste si une vol cible plus élevée (20% au lieu de
15%), en relevant l'exposition moyenne plus près de 1.0x, referme
l'écart de rendement qui a fait échouer le #43 sans sacrifier le
bénéfice de MDD.

## Hypothèse

Le #43 a échoué sur le rendement car sa vol cible (15%) est
structurellement inférieure à la vol réalisée moyenne des marchés
actions (typiquement 18-22% annualisé), ce qui pousse l'exposition
moyenne sous 1.0x en permanence. Une vol cible de 20% (plus proche de
la vol de marché typique) devrait rapprocher l'exposition moyenne de
1.0x, réduisant l'écart de rendement tout en conservant une partie du
bénéfice de réduction du MDD en période de stress (vol >> 20%).

## Définition (fixée ici, avant tout résultat)

- Vol réalisée = écart-type des rendements log quotidiens sur une
  fenêtre roulante de **20 séances**, annualisée (× √252), calcul
  causal identique au #43.
- Vol cible = **20% annualisé** (SEUL paramètre modifié par rapport au
  #43, qui utilisait 15%).
- Position(t) = **clip(vol_cible / vol_réalisée(t-1), 0.0, CAP=2.0)**
  — identique au #43 (même CAP, même fenêtre).
- Échantillon testable = à partir de la 21e séance.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique (position 1.0x fixe).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (vol cible 20%, fenêtre 20j et CAP=2.0x fixés a
priori, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_vol_targeting_20_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py vol_targeting_20_overlay`.
