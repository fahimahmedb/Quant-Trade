# Pré-enregistrement — Momentum "12-1 mois" (Jegadeesh & Titman 1993)

**Committé AVANT tout calcul.** Cycle #73 du backlog non-ML. Troisième
construction de momentum testée dans ce backlog, distincte du #4
(proximité du plus haut 52-semaines, ratio prix/plus-haut) et du #14
(momentum court terme, rendement 5j). Ici la construction académique
standard de Jegadeesh & Titman (1993) : rendement cumulé sur 12 mois EN
EXCLUANT le mois le plus récent, pour éviter la contamination par le
renversement de court terme (short-term reversal, French 1980, Jegadeesh
1990) déjà documenté comme un phénomène distinct du momentum.

## Hypothèse

Le signal "12-1" (12 mois de rendement, mois le plus récent exclu) est
la construction de momentum la plus citée et la plus robuste de la
littérature académique (Jegadeesh & Titman 1993, Fama & French 1996).
Sélectionner le tercile supérieur de titres NDX-100 selon ce signal,
rebalancé mensuellement, pourrait battre un portefeuille équipondéré
Buy&Hold sur le même univers — sur le même principe que le #4 (52w-high,
PASS) mais avec une construction de signal différente et plus proche de
la littérature académique originale.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés localement
  (`data/pead/prices/*.json`), identique au #4/#14.
- Signal de momentum au jour t : `momentum(t) = close(t-SKIP) /
  close(t-LOOKBACK) - 1`, avec **LOOKBACK=252** (≈12 mois de séances) et
  **SKIP=21** (≈1 mois de séances, exclu du calcul en utilisant le prix
  d'il y a 21 séances plutôt que le prix du jour). Ceci exclut
  explicitement le rendement du dernier mois du signal, conformément à
  la construction académique standard.
- Rebalancement tous les **REBAL_EVERY=21** jours (mensuel, identique au
  #4), sélection du **tercile supérieur** (titres avec le momentum le
  plus élevé), équipondération au sein du tercile.
- Référence : portefeuille équipondéré Buy&Hold sur le même univers
  (tous les titres cotés, identique à la référence du #4).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.
- Calendrier de référence = UNION des dates de cotation des titres (pas
  intersection stricte), chaque titre traité comme absent avant sa date
  d'introduction (même correction de bug documentée au #4).

## Univers et période

`data/pead/prices/*.json` (titres NDX-100), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille "momentum 12-1" doit battre le Buy&Hold équipondéré
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (LOOKBACK=252, SKIP=21, REBAL_EVERY=21 et
tercile fixés a priori sur la construction académique standard, aucune
grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_momentum_12_1_backtest.py`,
vérification via `nonml_anti_cheat_check.py momentum_12_1`.
