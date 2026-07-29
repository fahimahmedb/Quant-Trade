# Pré-enregistrement — Momentum de CONSTANCE (fraction de mois positifs)

**Committé AVANT tout calcul.** Cycle #82 du backlog non-ML. Quatrième
construction de momentum testée dans ce backlog, distincte de
l'amplitude cumulée (#4 52w-high, #73 12-1 mois) et du momentum court
terme (#14) : ici le signal mesure la CONSTANCE du momentum (fraction
des 12 derniers mois avec un rendement positif) plutôt que son
amplitude — un titre qui monte régulièrement chaque mois (même
modestement) pourrait être un meilleur pari qu'un titre porté par
quelques mois exceptionnels, robuste aux valeurs aberrantes (un seul
mois extrême ne domine pas le classement).

## Hypothèse

Un signal de constance (fraction de mois positifs) pourrait capter un
momentum plus "sain"/robuste que l'amplitude cumulée, moins sensible à
un seul mois extrême (positif ou négatif). Sélectionner le tercile de
titres avec la plus forte constance, rebalancé mensuellement, pourrait
battre un portefeuille équipondéré Buy&Hold sur le même univers.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés localement
  (`data/pead/prices/*.json`), identique au #4/#14/#73/#75.
- Découpage du calendrier de cotation en blocs non chevauchants de
  `BLOCK_LEN=21` séances (≈1 mois de bourse, cohérent avec le
  REBAL_EVERY=21 déjà utilisé partout dans ce backlog — pas un
  découpage calendaire par mois civil, pour rester purement séquentiel
  et simple).
- Signal au jour t : Consistency(t) = fraction des `N_BLOCKS=12`
  derniers blocs de 21 séances (soit `LOOKBACK=252` séances, identique
  au #4/#73) avec un rendement de bloc positif
  (`close(fin_bloc)/close(début_bloc) - 1 > 0`).
- Rebalancement tous les `REBAL_EVERY=21` jours (mensuel, identique au
  #4/#73), sélection du **tercile supérieur** (titres à la constance la
  plus élevée), équipondération au sein du tercile.
- Référence : portefeuille équipondéré Buy&Hold sur le même univers
  (identique à la référence du #4/#73).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.
- Calendrier de référence = UNION des dates de cotation (même correction
  de bug documentée au #4).

## Univers et période

`data/pead/prices/*.json` (titres NDX-100), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille "momentum de constance" doit battre le Buy&Hold
équipondéré **simultanément** en Sharpe annualisé net de coûts ET en
rendement total net de coûts. n_trials=1 (BLOCK_LEN=21, N_BLOCKS=12,
REBAL_EVERY=21 et tercile fixés a priori par analogie directe avec le
#4/#73, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_momentum_consistency_backtest.py`,
vérification via `nonml_anti_cheat_check.py momentum_consistency`.
