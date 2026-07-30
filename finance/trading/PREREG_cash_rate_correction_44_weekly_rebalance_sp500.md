# Pré-enregistrement — Rebalancement hebdomadaire du #149 sur S&P 500 (complétion du #154)

**Committé AVANT tout calcul.** Cycle #157 du backlog non-ML.
Complétion mineure du #154 (qui n'avait testé que NDX et Russell 2000),
pas une nouvelle direction de recherche.

## Objet

Le #154 a montré que le rebalancement hebdomadaire (technique du #131)
corrige la fissure de stress de coûts détectée sur Russell 2000 (#151)
sans dégrader NDX. Le S&P 500, 3e marché déjà généralisé au #151
(4/5, aucune fissure détectée), n'a pas encore reçu ce test. Ce cycle
complète la vérification : le rebalancement hebdomadaire dégrade-t-il,
préserve-t-il, ou améliore-t-il le score déjà bon du S&P 500 ?

## Définition (fixée ici, identique au #154 sauf le marché)

- Position équity : `pos_weekly(t)` = échantillonnage-et-maintien
  (`REBAL_FREQ=5j`, IDENTIQUE au #131/#154) de la position quotidienne
  DÉJÀ COMMITTÉE du #151 sur S&P 500
  (`nonml_cash_rate_correction_44_crossmarket_sp500_pnl.npz`).
- Fraction complémentaire allouée au proxy obligataire DGS10 déjà
  aligné dans l'artefact source — inchangé.
- Coûts : 5 bps par unité de turnover.
- **Référence** : Buy & Hold 100% S&P 500.

## Critère de succès (pré-enregistré, IDENTIQUE au #149/#151, critère standard)

Sharpe ET rendement net de coûts > BH.

## Batterie de validation renforcée (Règle 9, SI PASS)

`scripts/nonml_pass_validation_battery.py
cash_rate_correction_44_weekly_rebalance_sp500`, n_trials=taille
totale du backlog (jamais 1).

## Anti-cheat

Ce fichier committé avant
`nonml_cash_rate_correction_44_weekly_rebalance_sp500_backtest.py`,
vérification via `nonml_anti_cheat_check.py
cash_rate_correction_44_weekly_rebalance_sp500`. Aucune nouvelle
donnée (artefact #151 déjà committé).
