# Pré-enregistrement — Rebalancement hebdomadaire du #149 (correction ciblée de la fissure coûts Russell 2000)

**Committé AVANT tout calcul.** Cycle #154 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Le #151 a révélé le premier échec de stress de coûts de toute la
famille diversification obligataire : le #149 (cible 15% +
diversification) échoue le test à 5x le coût nominal sur Russell 2000
(2/5 seulement). Hypothèse ciblée, motivée directement par ce
diagnostic (pas une nouvelle exploration générique) : le rebalancement
HEBDOMADAIRE (échantillonnage-et-maintien de la position quotidienne
tous les 5 jours, technique déjà validée au #131) réduit le turnover
et devrait donc réduire la sensibilité aux coûts, potentiellement assez
pour repasser le contrôle (a) sur Russell 2000.

## Définition (fixée ici, avant tout résultat, identique en tout point au #131 sauf le mécanisme source)

- Position équity : `pos_weekly(t)` = échantillonnage-et-maintien
  (`REBAL_FREQ=5j`, IDENTIQUE au #131) de la position quotidienne DÉJÀ
  COMMITTÉE du #151 sur Russell 2000
  (`nonml_cash_rate_correction_44_crossmarket_russell2000_pnl.npz`),
  et SUR NDX (`nonml_cash_rate_correction_defensive_vol_targeting_
  44_pnl.npz`) pour comparaison (le #151 n'avait pas échoué sur NDX,
  teste si le rebalancement hebdomadaire y a un effet neutre ou
  positif également).
- Fraction complémentaire allouée au proxy obligataire DGS10 déjà
  aligné dans les artefacts sources — inchangé.
- Coûts : 5 bps par unité de turnover (turnover recalculé sur la
  position hebdomadaire, mécaniquement plus faible).
- **Référence** : Buy & Hold 100% sur chaque marché.

## Critère de succès (pré-enregistré, IDENTIQUE au #149, critère standard)

Sharpe ET rendement net de coûts > BH, par marché.

## Batterie de validation renforcée (Règle 9, SI PASS, par marché PASS)

`scripts/nonml_pass_validation_battery.py
cash_rate_correction_44_weekly_rebalance_<marché>`, n_trials=taille
totale du backlog (jamais 1). Le contrôle CIBLE de cette hypothèse est
le volet (a) stress de coûts sur Russell 2000 — rapporté explicitement,
succès ou échec.

## Anti-cheat

Ce fichier committé avant
`nonml_cash_rate_correction_44_weekly_rebalance_backtest.py`,
vérification via `nonml_anti_cheat_check.py
cash_rate_correction_44_weekly_rebalance`. Aucune nouvelle donnée
(artefacts #149/#151 déjà committés).
