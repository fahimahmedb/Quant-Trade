# Pré-enregistrement — Leaders 52-semaines + overlay levé sur accélération du signal

**Committé AVANT tout calcul.** Cycle #16 du backlog non-ML. 3e variante
de combinaison avec le cycle #4 (momentum 52-semaines, PASS) : après le
déclencheur calendaire (#11, ToM, PASS) et le déclencheur vol-calme (#9,
FAIL), ce cycle teste un déclencheur ENDOGÈNE au signal lui-même
(accélération du momentum) plutôt qu'un signal calendaire ou de
volatilité externe.

## Hypothèse

Quand le signal momentum du portefeuille leaders s'accélère d'un
rebalancement à l'autre (le ratio moyen prix/plus-haut-52sem du panier
augmente), c'est un signal de conviction renforcée — lever l'exposition
dans ces phases devrait améliorer le résultat par rapport au portefeuille
leaders à exposition constante 1.0x.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = EXACTEMENT le portefeuille "leaders" du cycle #4
  (tercile supérieur par ratio prix/plus-haut-52sem, NDX-100,
  rebalancement 21j, aucun paramètre changé).
- À chaque rebalancement *t* (à partir du 2e), calcul du ratio moyen des
  titres sélectionnés dans le panier leaders. Si ce ratio moyen est
  SUPÉRIEUR à celui du rebalancement précédent (accélération), exposition
  = **CAP = 2.0x** pour la période suivante ; sinon exposition = 1.0x.
  Premier rebalancement (pas de comparaison possible) : exposition 1.0x
  par défaut.
- **Coûts** : 5 bps par unité de turnover (rebalancement + transitions
  d'exposition).
- **Référence** : le portefeuille "leaders" lui-même à 1.0x (résultat du
  cycle #4), comme pour le cycle #11 — pas Buy&Hold classique.

## Univers et période

Identique aux cycles #4/#11 : NDX-100 (99 tickers, `data/pead/prices/`),
2022-2026.

## Critère de succès RENFORCÉ (pré-enregistré)

La version levée doit battre le portefeuille leaders 1.0x (référence)
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0 cohérent avec les cycles #8/#9/#10/#11,
pas choisi après résultat).

## Anti-cheat

Ce fichier committé avant `nonml_leaders_accel_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py leaders_accel_overlay`.
