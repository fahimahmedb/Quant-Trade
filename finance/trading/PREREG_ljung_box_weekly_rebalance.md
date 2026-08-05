# Pré-enregistrement — Rebalancement hebdomadaire de la porte Ljung-Box (#242)

**Committé AVANT tout calcul.** Cycle #249 du backlog non-ML. Après 5
FAIL sur les 6 derniers cycles de découverte de nouveaux signaux
(#233/#236/#239/#247/#248), ce cycle change délibérément de nature :
au lieu d'un nouveau signal, il teste une CORRECTION MÉCANIQUE ciblée
sur un candidat déjà PASS niveau 1 mais fragile en Règle 9, réutilisant
une technique déjà validée deux fois dans ce backlog (Règle 7).

## Contexte et motivation

Le #242 (porte de clustering ARCH par Ljung-Box glissante) est PASS
niveau 1 (4/5) mais sa batterie Règle 9 (#243) échoue précisément sur
**les coûts (dès 25 bps) ET la stabilité temporelle (2/4 folds)** —
signature typique d'un turnover trop élevé pour son edge. Deux
précédents dans ce backlog ont montré qu'un simple rebalancement
hebdomadaire (position échantillonnée tous les 5 jours et maintenue
constante, SANS modifier le signal sous-jacent) corrige ce type de
fissure : **#154** (cash rate correction, Russell 2000, contrôle coûts
2/5→3/5) et **#167** (portefeuille volatility-managed GJR-t, #165,
Règle 9 2/5→3/5 sur le contrôle coûts). Ce cycle applique la même
correction mécanique au #242.

## Hypothèse

Le rebalancement hebdomadaire de la porte Ljung-Box améliore-t-il son
score Règle 9 (#243, 2/5, échecs coûts et stabilité), sans modifier le
signal de porte lui-même ?

## Définitions (déclarées avant calcul, réutilisation stricte Règle 7)

- `weekly_hold_position(pos_daily, freq=5)` réutilisée À L'IDENTIQUE de
  `nonml_gjr_vol_managed_weekly_rebalance_backtest.py` (elle-même
  réutilisée du #154) : la position quotidienne du #242 (calculée sans
  aucune modification de `calm_lb_mask`/`combined_position`) est
  échantillonnée tous les `REBAL_FREQ=5` jours (une semaine de bourse) et
  maintenue constante entre deux rebalancements.
- Aucun paramètre du signal Ljung-Box (`LB_WINDOW=252`, `LB_MAXLAG=22`,
  `MEDIAN_WINDOW=252`) ni du mécanisme #46 sous-jacent (`VOL_WINDOW=20`,
  `TARGET_VOL_ANNUAL=20%`, `CAP=2.0x`, `COST_BPS=5`) n'est modifié.

## Univers et période

NDX (40 ans) — marché de référence de la batterie Règle 9 du #243, pour
comparaison directe.

## Critère de succès (n_trials=1)

Ce cycle ne re-teste PAS le PASS niveau 1 (déjà acquis au #242, signal
inchangé). Il évalue si la batterie Règle 9 (`nonml_pass_validation_
battery.py`) s'améliore par rapport au score du #243 (2/5) — succès
défini comme une amélioration d'AU MOINS un contrôle supplémentaire
(donc ≥3/5), échec sinon. Les 5 contrôles restent identiques (coûts
×3/×5, crise, stabilité 4 folds, SPA, DSR à n_trials=249).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le rebalancement hebdomadaire réduit le turnover mais aussi la
   réactivité du signal — pourrait dégrader le Sharpe/rendement niveau 1
   lui-même (le #167 a préservé le PASS niveau 1 du #165, mais ce n'est
   pas garanti ici).
2. L'échec de stabilité temporelle du #243 (2/4 folds) n'est pas
   nécessairement lié au turnover — un rebalancement plus lent pourrait
   ne rien changer à ce contrôle spécifique, seulement aux coûts.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_ljung_box_weekly_rebalance_backtest.py` (nouveau,
réutilise `calm_lb_mask`/`combined_position` du #242 et
`weekly_hold_position` du #154 sans modification). Vérification via
`nonml_anti_cheat_check.py ljung_box_weekly_rebalance`.
