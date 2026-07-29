# Pré-enregistrement — Momentum 12-1 + filtre Low-Volatility (double tri)

**Committé AVANT tout calcul.** Cycle #79 du backlog non-ML. Combine le
momentum 12-1 (#73, PASS) avec un filtre Low-Volatility par double tri
stock-level — jamais testé comme combinaison à deux facteurs dans ce
backlog (les combinaisons précédentes #33/#38/#39/#74 combinaient un
portefeuille stock-level avec un signal de tendance INDICIEL, pas un
second facteur stock-level).

## Hypothèse

La littérature documente que le momentum combiné à un filtre de faible
volatilité ("quality momentum") tend à réduire le risque de krachs
brutaux du momentum ("momentum crashes", Daniel & Moskowitz 2016) sans
sacrifier l'essentiel de l'edge. Exclure d'abord le tercile de titres
les plus volatils, puis sélectionner le momentum le plus élevé parmi les
titres restants, pourrait améliorer le ratio Sharpe/MDD du #73 sans
détruire son rendement.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés localement
  (`data/pead/prices/*.json`), identique au #4/#14/#73/#75.
- **Étape 1 (filtre vol)** : à chaque date de rebalancement, calcul de
  la volatilité réalisée sur `VOL_WINDOW=60` jours (écart-type des
  rendements log quotidiens) pour chaque titre éligible (momentum ET vol
  définis). Exclusion du tercile des titres les PLUS volatils (on ne
  garde que les 2/3 les moins volatils).
- **Étape 2 (sélection momentum)** : parmi les titres restants après le
  filtre vol, sélection du tercile (1/3 des SURVIVANTS, pas de l'univers
  initial) avec le signal momentum 12-1 le plus élevé (identique au #73 :
  `momentum(t) = close(t-SKIP)/close(t-LOOKBACK)-1`, LOOKBACK=252,
  SKIP=21).
- Équipondération au sein de la sélection finale.
- Rebalancement tous les `REBAL_EVERY=21` jours (mensuel, identique au
  #73).
- **Référence** : le portefeuille momentum 12-1 SEUL (#73), PAS Buy&Hold
  — identique à la convention du #74 (teste si l'ajout d'un filtre
  améliore le signal de base).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.
- Calendrier de référence = UNION des dates de cotation (même correction
  de bug documentée au #4).

## Univers et période

`data/pead/prices/*.json` (titres NDX-100), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille double-trié doit battre le momentum 12-1 seul (#73)
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (VOL_WINDOW=60j, LOOKBACK=252, SKIP=21,
REBAL_EVERY=21 et tercile fixés a priori — VOL_WINDOW=60 choisi par
analogie directe avec le Low-Vol tilt déjà utilisé au #15, aucune grille
testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_momentum_lowvol_doublesort_backtest.py`,
vérification via `nonml_anti_cheat_check.py momentum_lowvol_doublesort`.
