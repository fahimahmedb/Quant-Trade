# Pré-enregistrement — Overlay vol-targeting gaté par un régime de volatilité réalisée FAIBLE

**Committé AVANT tout calcul.** Cycle #58 du backlog non-ML. Troisième
type de signal de porte pour le mécanisme hiérarchique vol-targeting
déjà validé sur la tendance (#47/#51/#53) et le calendrier (#54) et la
confirmation multi-marché (#57) : ici la porte est dérivée de la
volatilité réalisée ELLE-MÊME (pas d'un signal de prix externe), motivée
par le clustering de volatilité déjà documenté dans l'Étape A/C de ce
projet (effet ARCH massif détecté sur les deux échantillons).

## Hypothèse

La volatilité réalisée est fortement auto-corrélée ("le calme appelle le
calme" — clustering de volatilité, effet ARCH déjà quantifié à l'Étape
A/C). En régime de vol réalisée FAIBLE (sous sa propre médiane
glissante), la vol future attendue reste probablement faible : c'est
précisément le régime où le vol-targeting amplifie le plus l'exposition
(cible/vol réalisée élevé quand vol réalisée faible), et où ce levier a
le plus de chances d'être "sûr" (peu de risque de choc de vol immédiat).
Gater le vol-targeting par ce régime plutôt que par une porte externe
(tendance, calendrier, breadth) pourrait capter le même bénéfice sans
dépendre d'un second signal.

## Définition (fixée ici, avant tout résultat)

- Vol réalisée = écart-type glissant `VOL_WINDOW=20j` des rendements log,
  annualisée (racine(252)), décalée d'un jour (`vol_lagged`, identique au
  mécanisme #46/#47 — aucun paramètre nouveau ici).
- Médiane de référence = médiane glissante de `vol_lagged` sur
  `MEDIAN_WINDOW=252` jours (1 an, cohérent avec le lookback des signaux
  de tendance/breadth #37/#52 déjà utilisés dans ce backlog). Calculée
  uniquement sur des valeurs de `vol_lagged` déjà causales (chacune ne
  dépend que du passé) → aucune fuite possible par construction.
- Porte active au jour t si `vol_lagged(t) < médiane_glissante(t)`
  (régime de vol réalisée sous sa propre norme récente).
- Quand la porte est active : position = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%** et **CAP = 2,0x**
  (paramètres identiques au #46/#47, aucun retuning).
- Quand la porte est inactive (régime de vol réalisée élevé) : position
  = **1,0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (fenêtre de vol 20j et cible 20% reprises à
l'identique du #46/#47, fenêtre de médiane 252j fixée a priori par
analogie avec les autres signaux de régime du backlog, CAP=2,0x
identique, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_lowvol_regime_vol_targeting_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py lowvol_regime_vol_targeting_overlay`.
