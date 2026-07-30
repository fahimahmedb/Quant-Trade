# Pré-enregistrement — Correction taux réaliste sur le #44 généralisée à S&P 500 et Russell 2000

**Committé AVANT tout calcul.** Cycle #151 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md` — Règle 3 (généralisation
cross-marché), même traitement que le #134→#136.

## Hypothèse

Le #149 (vol-targeting défensif cible 15% + diversification
obligataire DGS10) a obtenu le meilleur résultat brut du backlog sur
NDX (Sharpe +0,84, MDD -37,9%, 4/5 Règle 9). Ce cycle teste si ce
résultat se généralise à S&P 500 et Russell 2000, comme le #134 s'était
généralisé au #136 (S&P 500 4/5, Russell 2000 3/5).

## Définition (fixée ici, identique au #149 en tout point sauf le marché)

- Position équity : `vol_target_position(r)` du #44
  (`TARGET_VOL_ANNUAL=15%`, `VOL_WINDOW=20j`, `CAP=1.0`), appliquée
  SANS RETUNING aux rendements de S&P 500 et Russell 2000.
- Proxy obligataire : IDENTIQUE au #149 (DGS10, duration modifiée 10
  ans).
- `r_combiné(t) = pos_eq(t)*r_marché(t) + (1-pos_eq(t))*r_bond(t)`.
- Coûts : 5 bps par unité de turnover.
- **Référence** : Buy & Hold 100% sur chaque marché.

## Critère de succès (pré-enregistré, IDENTIQUE au #44/#149, critère standard uniquement)

Sharpe ET rendement net de coûts > BH, par marché. Rapporté séparément
pour CHAQUE marché, aucune sélection du "meilleur marché" après coup.

## Batterie de validation renforcée (Règle 9, SI PASS, par marché PASS)

`scripts/nonml_pass_validation_battery.py
cash_rate_correction_44_crossmarket_<marché>`, n_trials=taille totale
du backlog (jamais 1).

## Anti-cheat

Ce fichier committé avant
`nonml_cash_rate_correction_44_crossmarket_backtest.py`, vérification
via `nonml_anti_cheat_check.py cash_rate_correction_44_crossmarket`.
Aucune nouvelle donnée (OHLC S&P 500/Russell 2000 et DGS10 déjà en
local).
