# Pré-enregistrement — Overlay levé cycle électoral américain (année pré-électorale)

**Committé AVANT tout calcul.** Cycle #30 du backlog non-ML. Anomalie
documentée (Hirsch, "Stock Trader's Almanac", depuis 1986) : la 3e année
du mandat présidentiel américain (année précédant l'élection) serait
historiquement la plus forte du cycle de 4 ans, sur l'hypothèse d'un
stimulus économique/monétaire pré-électoral. Testable en profondeur
seulement sur NDX (40 ans, ~10 cycles complets) ; les 4 autres marchés
gardent le protocole standard du backlog malgré un nombre de cycles
observés parfois très faible (ex. Composite, 5 ans, ne couvre qu'une
fraction d'un seul cycle) — limite explicitement signalée.

## Hypothèse

L'année précédant une élection présidentielle américaine (peu importe le
marché testé, l'effet étant documenté comme global via la politique
monétaire US) affiche un rendement/Sharpe structurellement meilleur que
le reste du cycle de 4 ans.

## Définition (fixée ici, avant tout résultat)

- Année pré-électorale = année civile `Y` telle que `(Y+1) % 4 == 0`
  (ex. 2023, 2019, 2015... précédent une élection en 2024, 2020, 2016).
  Calcul déterministe sur l'année civile de la date de clôture, aucun
  calendrier électoral codé "à la main" en dehors de cette formule.
- Position = **1.0x en permanence**, SAUF les séances de l'année
  pré-électorale où position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`). Limite
explicitement signalée : le nombre de cycles électoraux complets varie
fortement selon la longueur d'historique de chaque marché (NDX ~10
cycles, Composite <1 cycle).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant `nonml_presidential_cycle_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py presidential_cycle_overlay`.
