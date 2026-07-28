# Pré-enregistrement — Leaders 52-semaines + overlay levé sur fenêtre ToM

**Committé AVANT tout calcul.** Cycle #11 du backlog non-ML. Combine
deux mécanismes DÉJÀ validés séparément (cycle #4 : sélection de titres
par proximité du plus haut 52 semaines ; cycle #8 : levier temporaire
déclenché par la fenêtre calendaire tournant-de-mois), plutôt qu'un
levier constant (déjà démontré mathématiquement Sharpe-invariant et
inefficace au cycle #10).

## Hypothèse

Le portefeuille "leaders" (#4) bat déjà Buy&Hold. Le déclencheur ToM (#8)
a déjà démontré qu'un levier CONDITIONNEL (pas constant) peut améliorer
Sharpe ET rendement. Cette combinaison teste si appliquer le même
déclencheur conditionnel (levier CAP=2.0x pendant la fenêtre ToM
seulement, 1.0x sinon) AU PORTEFEUILLE LEADERS (au lieu du portefeuille
équipondéré simple de #8) améliore encore le résultat.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = EXACTEMENT le portefeuille "leaders" du cycle #4
  (tercile supérieur par ratio prix/plus-haut-52sem, univers NDX-100,
  rebalancement 21j, aucun paramètre changé).
- Exposition = **1.0x en permanence** sur ce portefeuille leaders, SAUF
  pendant la fenêtre ToM (4 derniers j. de bourse du mois + 3 premiers j.
  du mois suivant, définition identique aux cycles #2/#8) où exposition =
  **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de turnover (rebalancement mensuel du
  portefeuille leaders + transitions d'exposition ToM).
- **Référence** : le portefeuille "leaders" lui-même à 1.0x (résultat du
  cycle #4), PAS Buy&Hold classique — pour isoler l'apport spécifique du
  levier conditionnel par-dessus un edge déjà validé.

## Univers et période

Identique au cycle #4 : NDX-100 (99 tickers, `data/pead/prices/`),
2022-2026.

## Critère de succès RENFORCÉ (pré-enregistré)

La version levée doit battre le portefeuille leaders 1.0x (référence)
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0 cohérent avec les cycles #8/#9/#10, pas
choisi après résultat).

## Anti-cheat

Ce fichier committé avant `nonml_leaders_tom_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py leaders_tom_overlay`.
