# Étape P5 — Machine learning sur données historiques (étape finale)

## 1. Cadre

On applique une famille ML (régression logistique, forêt aléatoire, gradient boosting, XGBoost) aux **mêmes** variables fondamentales, sur le **même** backtest OOS que les briques précédentes. Cible : part 2nd tour de la référence (la version logistique classe l'issue puis la mappe en part). Voir `src/pp_ml.py`.

## 2. Résultats OOS (7 plis, fenêtre expansive)

| Prédicteur | n | Brier | Log-loss | MAE part | Bonne issue |
|---|---|---|---|---|---|
| ML — régression logistique | 7 | 0.215 | 0.910 | 0.095 | 71% |
| ML — random forest | 7 | 0.291 | 0.864 | 0.105 | 57% |
| ML — gradient boosting | 7 | 0.279 | 3.381 | 0.126 | 71% |
| ML — XGBoost | 7 | 0.450 | 3.894 | 0.137 | 43% |
| Structurel (P1) | 7 | 0.295 | 0.909 | 0.120 | 57% |
| Fusion (P4) | 7 | 0.294 | 0.892 | 0.118 | 57% |

## 3. Lecture (biais-variance)

- Meilleur Brier ML = **0.215** ; structurel parcimonieux = **0.295** ; fusion multi-source = **0.294**.
- L'un des modèles ML devance légèrement le structurel, mais l'écart n'est PAS significatif à cet effectif (7 plis) : à traiter comme du bruit, pas comme une preuve de supériorité.
- **Correction d'audit** : marchés et NLP étant désormais *forward-only* (données rétrospectives supprimées, cf. `results/AUDIT.md`), la fusion historique se **réduit au modèle structurel** — elle n'ajoute plus aucune information sur le passé. Tout écart entre ML, structurel et fusion à 7 plis est du **bruit d'échantillonnage**, pas une hiérarchie fiable. Le gain réel d'une fusion multi-source ne pourra se mesurer que sur un scrutin futur (2027), avec de vraies données de marché/Trends horodatées.

## 4. Où le ML paie vraiment : la maille circonscription → voir **Étape P9**

Le ML a besoin d'effectifs. À n=11 élections nationales, aucun écart n'est significatif (ci-dessus). Le vrai terrain est la **circonscription** : **c'est désormais fait, sur données réelles**, dans `scripts/run_etape_P9_ml_circonscription.py` (données ministère de l'Intérieur, présidentielle 2017→2022 par circonscription et par parti, LFI explicite).

Résultat P9 : un Gradient Boosting prédit la part 2022 par circonscription et **bat la baseline du swing national uniforme de façon massivement significative** — MAE 1.78 → 0.56 sur 5094 prédictions hors-échantillon, Wilcoxon p ≈ 0, significatif pour les 9 partis. Là où le national ne pouvait rien prouver (n=11), la circonscription le peut (n=5094). Voir `results/etape_P9_ml_circonscription.md`.

## 5. Limites

- 7 plis : tout écart de Brier < ~0.1 est du bruit d'échantillonnage.
- Hyperparamètres bornés a priori (profondeur), non optimisés — les optimiser sur ces 11 élections serait du data-snooping caractérisé.
- XGBoost disponible dans cet environnement ; le module fonctionne dans les deux cas.
