# Étape P5 — Machine learning sur données historiques (étape finale)

## 1. Cadre

On applique une famille ML (régression logistique, forêt aléatoire, gradient boosting, XGBoost) aux **mêmes** variables fondamentales, sur le **même** backtest OOS que les briques précédentes. Cible : part 2nd tour de la référence (la version logistique classe l'issue puis la mappe en part). Voir `src/pp_ml.py`.

## 2. Résultats OOS (7 plis, fenêtre expansive)

| Prédicteur | n | Brier | Log-loss | MAE part | Bonne issue |
|---|---|---|---|---|---|
| ML — régression logistique | 7 | 0.356 | 1.736 | 0.133 | 57% |
| ML — random forest | 7 | 0.235 | 0.745 | 0.101 | 71% |
| ML — gradient boosting | 7 | 0.319 | 3.464 | 0.135 | 57% |
| ML — XGBoost | 7 | 0.328 | 3.475 | 0.130 | 57% |
| Structurel (P1) | 7 | 0.368 | 1.114 | 0.130 | 57% |
| Fusion (P4) | 7 | 0.139 | 0.409 | 0.071 | 86% |

## 3. Lecture (biais-variance)

- Meilleur Brier ML = **0.235** ; structurel parcimonieux = **0.368** ; fusion multi-source = **0.139**.
- L'un des modèles ML devance légèrement le structurel, mais l'écart n'est PAS significatif à cet effectif (7 plis) : à traiter comme du bruit, pas comme une preuve de supériorité.
- La **fusion** reste la meilleure approche : elle gagne en information (marchés, NLP) plutôt qu'en capacité de modèle.

## 4. Où le ML paierait vraiment : la maille circonscription

Le ML a besoin d'effectifs. Les **législatives** offrent ~577 circonscriptions × plusieurs cycles = plusieurs milliers d'observations, avec des features riches par circonscription. Schéma de données cible (à collecter, NON fourni ici — aucune donnée synthétique n'est présentée comme réelle) :

```
data/fr_circonscriptions.csv  (une ligne = une circonscription × une élection)
  circo_id, annee, sortant_camp, resultat_precedent_pct, 
  taux_chomage_local, revenu_median, part_diplomes_sup, part_65plus,
  densite_urbaine, participation_prec, resultat (cible : camp gagnant / part)
```
Sur cette maille, `MlSource` (ou un XGBoost dédié par circonscription) s'entraîne sur les cycles passés et prédit le cycle courant, toujours via le même protocole OOS expansif de `src/pp_backtest.py`. La brique se branche sans changer le contrat `pp_types` : seul le loader de données change.

## 5. Limites

- 7 plis : tout écart de Brier < ~0.1 est du bruit d'échantillonnage.
- Hyperparamètres bornés a priori (profondeur), non optimisés — les optimiser sur ces 11 élections serait du data-snooping caractérisé.
- XGBoost disponible dans cet environnement ; le module fonctionne dans les deux cas.
