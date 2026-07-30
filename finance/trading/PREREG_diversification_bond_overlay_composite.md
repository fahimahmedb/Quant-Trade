# Pré-enregistrement — Diversification obligataire (#134) sur le Composite (échantillon de référence, 5 ans)

**Committé AVANT tout calcul.** Cycle #143 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md` — Règle 3 (généralisation
cross-marché), complète le 4e marché du projet.

## Hypothèse

Le #136 a confirmé le mécanisme du #134 sur S&P 500 et Russell 2000
(marchés US, taux US DGS10). `nasdaq_composite_daily.txt` (5 ans,
13/07/2021→10/07/2026) est l'échantillon PRÉ-ENREGISTRÉ de référence du
projet (CLAUDE.md : "toutes les analyses 'protocole figé' de référence
tournent dessus par défaut"), jamais testé avec ce mécanisme précis
dans ce backlog. Rupture attendue : échantillon BEAUCOUP plus court
(1251 séances vs 9522-14231 pour NDX/S&P500/Russell2000), donc moins de
puissance statistique et une seule "vraie" fenêtre de stress couverte
(2022, pas de dot-com/2008/COVID — hors de la période). Cette limite
est reconnue AVANT calcul.

## Définition (fixée ici, avant tout résultat, identique en tout point au #134/#136)

- Position équity : `vol_target_position(r)` du #115, SANS RETUNING,
  appliquée aux rendements du Composite (`data/nasdaq_composite_daily.txt`).
- Rendement obligataire : IDENTIQUE au #134 (DGS10, duration modifiée
  10 ans, formule fermée, corrigée du bug de singularité y=0 au #141).
- `r_combiné(t) = pos_eq(t)*r_Composite(t) + (1-pos_eq(t))*r_bond(t)`.
- Coûts : 5 bps par unité de turnover.
- **Référence** : Buy & Hold 100% Composite, même fenêtre.

## Critère de succès (pré-enregistré, DEUX volets, cohérence avec #134/#136)

1. Critère standard : Sharpe ET rendement net de coûts > BH.
2. Critère Calmar : Calmar > BH.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py
diversification_bond_overlay_composite`, n_trials=taille totale du
backlog (jamais 1). **Limite reconnue à l'avance** : l'échantillon
(1251 séances) est trop court pour couvrir 3 des 4 fenêtres de crise du
contrôle (b) — seul 2022 est dans l'historique disponible ; les 3
autres seront rapportées "hors couverture", pas comme un échec
silencieux (Règle 5 du protocole).

## Anti-cheat

Ce fichier committé avant
`nonml_diversification_bond_overlay_composite_backtest.py`,
vérification via `nonml_anti_cheat_check.py
diversification_bond_overlay_composite`. Aucune nouvelle donnée
(Composite et DGS10 déjà en local).
