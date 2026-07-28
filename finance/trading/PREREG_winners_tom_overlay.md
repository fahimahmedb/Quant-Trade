# Pré-enregistrement — Winners momentum court terme + overlay levé ToM

**Committé AVANT tout calcul.** Cycle #18 du backlog non-ML. 4e variante
de combinaison avec un mécanisme déjà validé — cette fois le portefeuille
de base est celui du cycle #14 (momentum court terme, winners), PAS le
cycle #4.

## ⚠️ Avertissement porté depuis le cycle #14 (à répéter dans le rapport final)

Le cycle #14 (Sharpe +2,35 à +3,75 selon variante) a été explicitement
flagué "prudence forte" : l'audit a montré que ce résultat reflète
probablement un marché haussier très concentré (IA/semi-conducteurs,
2021-2026) plutôt qu'un edge généralisable. **Empiler du levier
supplémentaire sur ce portefeuille risque d'amplifier un artefact de
période plutôt qu'un vrai signal.** Ce cycle teste quand même la
combinaison par discipline (n_trials=1, protocole complet), mais le
résultat — PASS ou FAIL — devra être lu avec la même réserve que le
cycle #14, pas comme une confirmation supplémentaire d'un edge solide.

## Hypothèse

Le déclencheur calendaire ToM (validé au cycle #8 sur Buy&Hold, et au
cycle #11 sur le portefeuille leaders 52-semaines) appliqué au
portefeuille "winners" momentum court terme (#14) améliore-t-il encore
le résultat ?

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = EXACTEMENT le portefeuille "winners" du cycle
  #14 (tercile supérieur par rendement 5j, NDX-100, rebalancement
  hebdomadaire, aucun paramètre changé).
- Exposition = **1.0x en permanence** sur ce portefeuille, SAUF pendant
  la fenêtre ToM (4 derniers j. de bourse du mois + 3 premiers j. du mois
  suivant, définition identique aux cycles #2/#8/#11) où exposition =
  **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de turnover (rebalancement hebdomadaire du
  portefeuille winners + transitions d'exposition ToM).
- **Référence** : le portefeuille "winners" lui-même à 1.0x (résultat du
  cycle #14), PAS Buy&Hold classique.

## Univers et période

Identique au cycle #14 : NDX-100 (99 tickers, `data/pead/prices/`),
2021-2026.

## Critère de succès RENFORCÉ (pré-enregistré)

La version levée doit battre le portefeuille winners 1.0x (référence)
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0 cohérent avec les cycles précédents,
pas choisi après résultat).

## Anti-cheat

Ce fichier committé avant `nonml_winners_tom_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py winners_tom_overlay`.
