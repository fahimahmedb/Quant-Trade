# Pré-enregistrement — Diversification obligataire (#134) généralisée à S&P 500 et Russell 2000

**Committé AVANT tout calcul.** Cycle #136 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md` — Règle 3 (généralisation
cross-marché, marchés INDÉPENDANTS de NDX).

## Hypothèse

Le #134 (diversification obligataire sur NDX) a obtenu le meilleur
score Règle 9 du backlog (4/5). Mais plusieurs signaux antérieurs de ce
backlog qui semblaient solides sur NDX ne se sont PAS généralisés à
d'autres marchés (#114→#126/#128, signal macro pente des taux : succès
NDX partiellement fortuit, échec net S&P 500/Russell 2000, #127). Ce
cycle teste si le #134 est un cas similaire (chance NDX-spécifique) ou
un mécanisme réellement transférable, en l'appliquant SANS AUCUNE
MODIFICATION à deux marchés américains indépendants (Règle 3) — le
proxy DGS10 (taux du Trésor US) est directement applicable aux deux,
puisque S&P 500 et Russell 2000 sont aussi des marchés actions US.

## Définition (fixée ici, identique au #134 en tout point sauf le marché)

- Position équity : `vol_target_position(r)` — fonction déjà validée et
  committée du #115 (`nonml_defensive_calmar_vol_targeting_overlay_
  backtest.py`), appliquée SANS RETUNING aux rendements de S&P 500 et
  Russell 2000 (`data/sp500_daily.txt`, `data/russell2000_daily.txt`).
  Mêmes paramètres exacts : `TARGET_VOL_ANNUAL=20%`, `VOL_WINDOW=20j`,
  `CAP=1.0` (jamais de levier).
- Proxy obligataire : IDENTIQUE au #134 (DGS10, duration modifiée
  10 ans, formule fermée sans paramètre libre).
- Mécanisme de diversification : IDENTIQUE au #134 — `r_combiné(t) =
  pos_eq(t)*r_marché(t) + (1-pos_eq(t))*r_bond(t)`.
- Coûts : 5 bps par unité de turnover de `pos_eq` (identique).
- **Référence** : Buy & Hold 100% sur chaque marché.

## Critère de succès (pré-enregistré, DEUX volets par marché, cohérence avec #134)

1. Critère standard : Sharpe ET rendement net de coûts > BH.
2. Critère Calmar : Calmar > BH.
Rapportés séparément pour CHAQUE marché, aucune sélection du "meilleur
marché" après coup — les deux marchés sont testés et rapportés,
PASS ou FAIL.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère, sur AU MOINS un marché)

`scripts/nonml_pass_validation_battery.py
diversification_bond_overlay_crossmarket_<marché>`, n_trials=taille
totale du backlog (jamais 1), exécutée séparément par marché PASS.

## Anti-cheat

Ce fichier committé avant
`nonml_diversification_bond_overlay_crossmarket_backtest.py`,
vérification via `nonml_anti_cheat_check.py
diversification_bond_overlay_crossmarket`. Aucune nouvelle donnée
(OHLC S&P 500/Russell 2000 et DGS10 déjà en local).
