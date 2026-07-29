# Pré-enregistrement — Overlay vol-targeting gaté par le golden cross (SMA50>SMA200)

**Committé AVANT tout calcul.** Cycle #67 du backlog non-ML. Remplace la
porte de tendance du #47 (proximité ≥95% du plus haut glissant 252j,
#37) par le golden cross (SMA50>SMA200, #34) — teste si un signal de
tendance basé sur un croisement de moyennes (généralement plus lissé,
moins de faux signaux ponctuels que la comparaison prix/SMA200 seule,
cf. #34 vs #29) améliore encore le mécanisme hiérarchique déjà validé
sur 3 types de porte (tendance #47, calendrier #54, breadth #57).

## Hypothèse

Le golden cross (#34, PASS 4/5) est un signal de tendance plus lissé que
la comparaison prix/SMA200 (#29) ou la proximité du plus haut 52-semaines
(#37) car il compare deux moyennes mobiles entre elles plutôt qu'un prix
volatil à une moyenne — moins de faux signaux ponctuels. Utiliser ce
signal comme porte du mécanisme hiérarchique vol-targeting (au lieu de
la porte #37 du #47) pourrait produire un edge au moins comparable, avec
potentiellement moins de bascules de position (turnover) grâce au
lissage du signal de porte.

## Définition (fixée ici, avant tout résultat)

- Porte tendance = golden cross, SMA50 > SMA200 (identique au #34,
  SMA_SHORT=50, SMA_LONG=200).
- Quand la porte est active : position = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%**, **CAP = 2,0x**,
  fenêtre de vol **VOL_WINDOW=20j** (paramètres identiques au #46/#47,
  aucun retuning).
- Quand la porte est inactive : position = **1,0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (tous les paramètres repris à l'identique des
cycles #34/#46/#47 déjà validés, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_goldencross_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py goldencross_vol_targeting_overlay`.
