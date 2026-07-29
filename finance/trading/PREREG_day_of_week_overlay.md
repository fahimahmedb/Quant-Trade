# Pré-enregistrement — Overlay levé "effet jour-de-semaine" (Monday effect)

**Committé AVANT tout calcul.** Cycle #56 du backlog non-ML.

## Hypothèse

L'effet "Monday effect" / "weekend effect" (French 1980 ; Gibbons & Hess
1981) documente historiquement des rendements moyens du lundi
significativement plus faibles (souvent négatifs) que ceux des autres
jours de la semaine sur les actions US, attribué au règlement différé du
week-end et à un biais de mauvaises nouvelles annoncées le vendredi soir
ou le week-end. Un overlay qui reste investi 1.0x en permanence (comme
Buy&Hold) mais AMPLIFIE l'exposition les jours de semaine hors lundi
(régime historiquement plus favorable) pourrait battre Buy&Hold, sur le
même principe structurel que les overlays calendaires déjà validés
(ToM #8, Halloween #17, union #21).

## Définition (fixée ici, avant tout résultat, sur la base de la
littérature — PAS un ajustement sur les données du projet)

- Jour de la semaine dérivé de la colonne `date` (`.dt.dayofweek`,
  0=lundi … 4=vendredi ; les données ne contiennent que des séances de
  bourse, donc pas de samedi/dimanche à exclure).
- Fenêtre "forte" = mardi, mercredi, jeudi, vendredi (dayofweek ∈
  {1,2,3,4}) → position = **CAP = 2,0x** ces jours-là.
- Lundi (dayofweek = 0) → position = **1,0x** (pas de réduction sous 1x,
  contrairement au #55 — ceci est un overlay d'AMPLIFICATION comme
  #8/#17/#21, pas un design défensif).
- Le jour de la semaine est une information calendaire connue à
  l'avance (pas une donnée de marché) — même traitement que ToM/Halloween
  dans ce backlog : aucune fuite possible par construction, `pos[t]`
  déterminé uniquement par `date[t]` (le jour de clôture du rendement
  `r[t] = log(close[t+1]/close[t])`), même convention d'alignement `[1:]`
  que #8/#17/#21.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (fenêtre "mardi-vendredi" et CAP=2,0x fixés a
priori sur la base de la littérature du Monday effect, aucune grille
testée avant ce résultat — la robustesse conditionnelle en cas de PASS
perturbera le CAP et éventuellement testera une fenêtre "mardi-jeudi"
alternative, mais SEULEMENT après le résultat principal, documentée
comme robustesse et non comme retuning).

## Anti-cheat

Ce fichier committé avant `nonml_day_of_week_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py day_of_week_overlay`.
