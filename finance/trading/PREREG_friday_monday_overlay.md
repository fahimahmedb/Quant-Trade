# Pré-enregistrement — Overlay levé fenêtre élargie vendredi-lundi

**Committé AVANT tout calcul.** Cycle #25 du backlog non-ML. Variante EN
OVERLAY (reste investi 1.0x en permanence, comme les cycles #8/#17/#21,
PAS flat hors fenêtre) du cycle #3 (effet jour-de-semaine testé flat par
jour individuel, FAIL 0/5) — le enseignement des cycles précédents (#2 vs
#8, #6/#7 vs aucun overlay testé) est qu'un design "flat hors fenêtre" ne
peut structurellement pas battre le rendement composé de Buy&Hold même
avec un edge de Sharpe réel ; on teste donc ici la variante overlay, sur
une fenêtre élargie (vendredi ET lundi combinés, pas testés ensemble
au #3) plutôt qu'un seul jour isolé.

## Hypothèse

L'effet week-end documenté (rendements vendredi/lundi statistiquement
différents des autres jours, littérature classique French 1980) pourrait
n'émerger qu'en combinant les deux jours adjacents au week-end (plutôt
que testés séparément comme au #3), et seulement visible sous forme
d'overlay (le #3 individuel avait échoué, mais sous un design flat qui
biaise structurellement les résultats vers le FAIL en rendement absolu).

## Définition (fixée ici, avant tout résultat)

- Fenêtre = vendredi **OU** lundi (jour de la semaine calculé sur la
  date de clôture, dayofweek pandas : lundi=0, vendredi=4).
- Position = **1.0x en permanence**, SAUF les jours dans la fenêtre où
  position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant `nonml_friday_monday_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py friday_monday_overlay`.
