# Pré-enregistrement — Overlay vol-targeting gaté par la confirmation multi-marché (breadth)

**Committé AVANT tout calcul.** Cycle #57 du backlog non-ML. Combine le
signal de confirmation croisée NDX+Russell 2000 (#52, PASS marginal en
overlay binaire CAP fixe) avec le mécanisme hiérarchique vol-targeting
déjà validé sur la tendance (#47) et le calendrier (#54) — teste si un
signal par ailleurs marginal/fragile (#52) devient plus robuste utilisé
comme PORTE d'un vol-targeting continu plutôt que comme déclencheur d'un
CAP binaire fixe.

## Hypothèse

Le #52 a montré que la confirmation croisée NDX+Russell2000 apporte un
edge Sharpe minuscule (+0,0092) et dégrade même légèrement le MDD en
overlay binaire CAP=2,0x fixe. Le mécanisme hiérarchique (#47/#51/#53/#54)
a montré que moduler l'amplification par la vol réalisée (plutôt qu'un
CAP fixe) préserve mieux le MDD et améliore le couple Sharpe/rendement
pour d'autres types de portes (tendance, calendrier). Remplacer le CAP
fixe du #52 par ce mécanisme pourrait transformer un signal marginal en
un edge plus net, sur le même principe.

## Définition (fixée ici, avant tout résultat)

- Porte = confirmation croisée NDX+Russell 2000 (signal A ∩ signal B,
  identique au #52 : proximité ≥95% du plus haut glissant 252j sur
  chaque marché, alignement par date avec ffill Russell→NDX).
- Quand la porte est active : position = **clip(vol_cible / vol_réalisée
  NDX(t-1), 1.0, CAP)**, avec **vol_cible = 20% annualisé** et **CAP =
  2,0x** (paramètres identiques au #46/#47, aucun retuning), vol réalisée
  = écart-type glissant 20j des rendements log NDX, annualisée
  (racine(252)), décalée d'un jour (t-1, connue à la clôture du jour t).
- Quand la porte est inactive : position = **1,0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique sur NDX-100.

## Univers et période

`data/nasdaq100_daily.txt` (marché testé) et `data/russell2000_daily.txt`
(marché de confirmation), déjà en local — identique au #52.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. Un seul
marché testé (NDX), comme au #52, car le mécanisme nécessite un second
marché de confirmation. n_trials=1 (tous les paramètres — seuil 95%,
cible vol 20%, CAP 2,0x, fenêtre vol 20j — repris à l'identique de
cycles déjà validés, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_breadth_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py breadth_vol_targeting_overlay`.
