# Pré-enregistrement — Overlay vol-targeting gaté par la pente de la SMA200

**Committé AVANT tout calcul.** Cycle #68 du backlog non-ML. Remplace la
porte de tendance du #47 (proximité ≥95% du plus haut glissant 252j,
#37) par la pente de la SMA200 (#66, PASS 5/5 en overlay binaire) —
complète la famille des signaux de tendance testés comme porte du
mécanisme hiérarchique vol-targeting (52w-high #47, calendrier #54,
breadth #57, golden cross #67, maintenant pente SMA200).

## Hypothèse

Le #66 a montré que la pente de la SMA200 (SMA200 croissante sur 20
jours) est un signal de tendance robuste (PASS 5/5, plateau parfait) et
que sa capacité à couper l'exposition plus tôt en début de retournement
semblait légèrement meilleure que le filtre de niveau (#29) sur certains
marchés (audit #66). Combiner ce signal avec le mécanisme hiérarchique
vol-targeting (déjà validé sur 4 autres types de porte) pourrait produire
un edge comparable ou supérieur au #47 (52w-high), qui reste jusqu'ici
le signal de tendance le plus robuste testé dans ce mécanisme (le golden
cross, #67, n'a pas réussi à le dépasser).

## Définition (fixée ici, avant tout résultat)

- Porte tendance = pente positive de la SMA200 (identique au #66,
  SMA_WINDOW=200, SLOPE_LAG=20 : SMA200(t) > SMA200(t-20)).
- Quand la porte est active : position = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%**, **CAP = 2,0x**,
  fenêtre de vol **VOL_WINDOW=20j** (paramètres identiques au
  #46/#47/#67, aucun retuning).
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
cycles #46/#47/#66 déjà validés, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_slope_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py slope_vol_targeting_overlay`.
