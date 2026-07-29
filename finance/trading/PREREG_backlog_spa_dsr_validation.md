# Pré-enregistrement — Validation famille SPA + DSR du backlog non-ML

**Committé AVANT tout calcul.** Demande explicite utilisateur ("Tu fera
donc la validation SPA DSR"), suite au constat (question utilisateur
"110 hypothèses suffisent...") que chaque hypothèse du backlog a été
testée individuellement (n_trials=1, honnête) mais que la FAMILLE
complète n'a jamais été corrigée conjointement pour les comparaisons
multiples — contrairement à l'Étape C (GARCH) qui applique déjà SPA à
sa famille de N=6 modèles. C'est le principe même de
PROTOCOLE_ANTI_SNOOPING.md : "Toute extension doit être déclarée,
comptée (N essais) et re-testée au SPA/DSR."

## Hypothèse testée

La famille homogène des overlays "vol-targeting hiérarchique gaté"
(mécanisme identique : `position = clip(20%/vol_réalisée_20j(t-1), 1.0,
2.0x)` uniquement si une porte de régime est active, sinon 1.0x plat)
construite au fil du backlog sur NDX-100, survit-elle à une correction
formelle pour tests multiples (SPA de Hansen) et à une pénalisation DSR
(Bailey & López de Prado) sur son propre nombre d'essais ?

## Univers figé (13 membres, décidé AVANT calcul)

Choisi pour homogénéité stricte : même mécanisme
(CAP=2.0/VOL_WINDOW=20j/TARGET_VOL_ANNUAL=20%), même actif piloté (NDX
Buy&Hold, `nasdaq100_daily.txt`), même source de données titre-par-titre
(`data/pead/prices/*.json`, ~2021+), mêmes coûts (5 bps/turnover). Liste
figée (ordre = ordre d'apparition dans le backlog) :

1. `nonml_dispersion_vol_targeting_overlay` (dispersion cross-sectionnelle)
2. `nonml_weakness_breadth_vol_targeting_overlay` (breadth de faiblesse, proximité plus bas 252j)
3. `nonml_correlation_regime_vol_targeting_overlay` (corrélation moyenne cross-sectionnelle)
4. `nonml_momentum_breadth_vol_targeting_overlay` (breadth momentum 12-1 mois)
5. `nonml_sma200_breadth_vol_targeting_overlay` (breadth SMA200)
6. `nonml_net_breadth_vol_targeting_overlay` (breadth nette avance/déclin)
7. `nonml_sma200_momentum_breadth_and_overlay` (AND #5 ∧ #4)
8. `nonml_market_concentration_vol_targeting_overlay` (concentration cross-sectionnelle)
9. `nonml_momentum_dispersion_vol_targeting_overlay` (dispersion des scores de momentum)
10. `nonml_range_position_vol_targeting_overlay` (position continue dans le range 252j)
11. `nonml_momentum_dispersion_trend_and_overlay` (AND #9 ∧ tendance 52w-high)
12. `nonml_beta_dispersion_vol_targeting_overlay` (dispersion des betas individuels)
13. `nonml_internal_breadth_vol_targeting_overlay` (breadth interne générale)

Exclus explicitement de cette famille (mécanisme différent ou univers de
données différent, non comparables au même protocole SPA) : tous les
overlays basés sur des séries macro/indices externes (DAX, autres
marchés), les signaux de tendance seuls, les signaux calendaires, et les
stratégies directionnelles de l'Étape B — ceux-ci restent hors du champ
de cette validation, non re-testés ici.

## Fenêtre commune

Intersection des fenêtres testables individuelles des 13 membres (chacun
restreint à la période où son signal cross-sectionnel est disponible,
~2021+) : `start_common = max(start_i pour i=1..13)`. Cette fenêtre
commune, strictement plus courte que chaque fenêtre individuelle, est
utilisée pour TOUS les membres ET le benchmark Buy&Hold, afin de garantir
une comparaison sur exactement les mêmes séances pour les 13 membres.

## Protocole SPA (Hansen 2005, `src/volatility.py::spa_test`, déjà
implémenté et utilisé à l'Étape C)

- Perte de chaque membre : `loss_i(t) = -pnl_i(t)` (perte = moins le pnl
  net de coûts, convention Sullivan/Timmermann/White 1999).
- Benchmark : Buy&Hold NDX sur la même fenêtre commune (coûts 5 bps un
  aller simple en t=0 comme dans chaque script individuel).
- Bootstrap stationnaire, mêmes paramètres par défaut que `spa_test()`
  (déjà validés à l'Étape C, aucun retuning ici).
- H0 : aucun membre de la famille ne bat significativement le benchmark
  une fois corrigé pour les 13 essais.

## Protocole DSR (Bailey & López de Prado 2014, `src/prediction.py::dsr`,
déjà implémenté et utilisé à l'Étape B)

- `n_trials = 13` (taille de la famille figée ci-dessus).
- `var_trials = variance (ddof=1) des 13 Sharpe annualisés nets de coûts
  sur la fenêtre commune`.
- DSR calculé pour le MEILLEUR membre (Sharpe max sur la fenêtre
  commune), comme à l'Étape B pour le meilleur signal de l'univers N=4.
- Rapport secondaire, explicitement approximatif et caveaté : un second
  DSR avec `n_trials=110` (backlog complet) et `var_trials` estimé à
  partir des Sharpe des 43/110 entrées du backlog dont le Sharpe est
  directement extractible du texte (regex `Sharpe [+-]X→[+-]Y`) — reporté
  uniquement à titre indicatif, PAS comme résultat principal, car
  l'univers N=110 est hétérogène (mécanismes différents, pas seulement
  vol-targeting) et donc pas strictement comparable au sens de la théorie
  DSR (qui suppose des essais sur la MÊME métrique candidate).

## Critère de succès (pré-enregistré)

Pas de critère PASS/FAIL binaire ici (ce n'est pas un nouveau backtest,
mais un test de validité rétrospectif sur des résultats déjà committés) :
le résultat est le rapport honnête des p-values SPA et du DSR, quel que
soit leur verdict. Aucune extension, aucun ajustement de la famille
après avoir vu ces résultats.

## Anti-cheat

Ce fichier committé avant
`scripts/nonml_backlog_spa_dsr_validation.py`. Le script réimporte les
fonctions `compute_*_series()` et les constantes déjà committées de
chacun des 13 scripts de backtest (aucune ré-implémentation divergente),
et ne fait que dupliquer fidèlement la construction de la porte de
chaque `main()` déjà committé, pour en extraire le pnl quotidien au lieu
de l'écrire sur disque. Aucun paramètre n'est retuné.
