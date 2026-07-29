# Pré-enregistrement — Tilt sur l'asymétrie (skewness) des rendements individuels

**Committé AVANT tout calcul.** Cycle #84 du backlog non-ML. Premier
signal de sélection stock-level basé sur un moment d'ordre 3
(asymétrie/skewness) de la distribution des rendements INDIVIDUELS d'un
titre, distinct de la dispersion CROSS-SECTIONNELLE du #78 (qui mesure
la dispersion entre titres à un instant donné, pas l'asymétrie de la
série temporelle d'un titre).

## Hypothèse

La littérature (Bali, Cakici & Whitelaw 2011, "MAX effect" ; préférence
pour l'asymétrie positive) documente que les investisseurs ont tendance
à surpayer les titres à forte asymétrie POSITIVE ("lottery stocks",
rendements occasionnellement très favorables mais rares), ce qui
comprime leur rendement futur attendu. À l'inverse, les titres à
asymétrie faible ou négative pourraient offrir une prime de rendement
en compensation du risque de queue gauche moins "attractif"
psychologiquement. Sélectionner le tercile de titres à l'asymétrie la
PLUS FAIBLE (évitant les "lottery stocks") pourrait battre un
portefeuille équipondéré Buy&Hold.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés localement
  (`data/pead/prices/*.json`), identique au #4/#14/#73/#75/#82.
- Signal au jour t : asymétrie (skewness) échantillon des rendements log
  quotidiens sur `SKEW_WINDOW=60` jours (identique à la fenêtre du Low-Vol
  tilt du #15, par analogie directe — moment d'ordre 3 au lieu de l'écart-type).
- Rebalancement tous les `REBAL_EVERY=21` jours (mensuel, identique au
  #4/#73/#82), sélection du tercile à l'asymétrie la PLUS FAIBLE,
  équipondération au sein du tercile.
- Référence : portefeuille équipondéré Buy&Hold sur le même univers
  (identique à la référence du #4/#73/#82).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.
- Calendrier de référence = UNION des dates de cotation (même correction
  de bug documentée au #4).

## Univers et période

`data/pead/prices/*.json` (titres NDX-100), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille "asymétrie faible" doit battre le Buy&Hold équipondéré
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (SKEW_WINDOW=60j par analogie avec le #15,
REBAL_EVERY=21 identique aux cycles précédents, tercile fixé a priori,
aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_skewness_tilt_backtest.py`,
vérification via `nonml_anti_cheat_check.py skewness_tilt`.
