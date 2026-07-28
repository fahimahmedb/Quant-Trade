# Pré-enregistrement — Overlay levé ToM ∪ Halloween (union des fenêtres)

**Committé AVANT tout calcul.** Cycle #21 du backlog non-ML. Combine deux
déclencheurs calendaires DÉJÀ validés séparément sur Buy&Hold (#8 ToM,
4/5 ; #17 Halloween, 4/5) — teste si leur union améliore encore le
résultat. Soumis à la règle de succès renforcée.

## Hypothèse

Un overlay qui lève l'exposition dès que L'UNE OU L'AUTRE des deux
fenêtres calendaires déjà validées (tournant-de-mois OU nov-avril) est
active devrait capturer une part plus large des deux effets, sans les
neutraliser mutuellement.

## Définition (fixée ici, avant tout résultat)

- Fenêtre ToM = 4 derniers j. de bourse du mois + 3 premiers j. du mois
  suivant (définition identique aux cycles #2/#8/#11/#20).
- Fenêtre Halloween = novembre à avril inclus (définition identique au
  cycle #17/#20).
- Position = **1.0x en permanence**, SAUF si le jour est dans la fenêtre
  ToM **OU** dans la fenêtre Halloween (union, pas intersection) où
  position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0 cohérent avec tous les cycles précédents).

## Anti-cheat

Ce fichier committé avant `nonml_tom_halloween_union_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py tom_halloween_union_overlay`.
