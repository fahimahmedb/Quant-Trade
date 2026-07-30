# Pré-enregistrement — Diversification obligataire (#134) sur DAX avec taux allemand

**Committé AVANT tout calcul.** Cycle #140 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md` — Règle 3 (généralisation
cross-marché, avec un taux domestique ADAPTÉ cette fois, contrairement
au #136 qui avait réutilisé DGS10 US sur des marchés US uniquement).

## Hypothèse

Le #136 a confirmé le mécanisme du #134 sur S&P 500 et Russell 2000
(marchés US, taux US DGS10 économiquement cohérent). DAX (marché
allemand/européen) n'a pas été testé dans ce backlog avec ce mécanisme
car aucun taux zone euro n'était encore récupéré. Ce cycle recherche un
proxy de taux allemand et teste si le mécanisme se généralise
également à un marché non-US avec un taux domestique adapté.

## Limite de données reconnue AVANT calcul (pas après avoir vu un résultat)

**Le seul taux allemand long terme trouvé librement et rapidement
accessible est MENSUEL, pas quotidien** : FRED `IRLTLT01DEM156N`
(OECD MEI, rendement des obligations d'État allemandes 10 ans, 1956-05
→2026-06, 842 observations MENSUELLES). Contrairement à DGS10 (US,
quotidien) utilisé pour le #134/#136/#137/#139, ce proxy sera
forward-fillé du mensuel au quotidien (dernière valeur connue reportée
jusqu'à la prochaine publication) — le rendement obligataire calculé
par la formule de duration produira donc des variations de prix
GROUPÉES au changement mensuel plutôt qu'une évolution quotidienne
lisse. **C'est une dégradation méthodologique reconnue explicitement**
(pas cachée) : le résultat de ce cycle est donc moins probant qu'une
vraie série quotidienne, et sera interprété avec cette réserve, PASS ou
FAIL.

## Définition (fixée ici, avant tout résultat)

- Position équity : `vol_target_position(r)` du #115
  (`nonml_defensive_calmar_vol_targeting_overlay_backtest.py`), SANS
  RETUNING, appliquée aux rendements DAX (`data/dax_daily.txt`).
- Rendement obligataire : MÊME formule de duration modifiée que le
  #134 (10 ans, fermée, sans paramètre libre), appliquée à
  `data/de10y_monthly.csv` (FRED `IRLTLT01DEM156N`) forward-fillé au
  calendrier DAX.
- `r_combiné(t) = pos_eq(t)*r_DAX(t) + (1-pos_eq(t))*r_bund(t)`.
- Coûts : 5 bps par unité de turnover de `pos_eq`.
- **Référence** : Buy & Hold 100% DAX.

## Critère de succès (pré-enregistré, DEUX volets, cohérence avec #134/#136)

1. Critère standard : Sharpe ET rendement net de coûts > BH.
2. Critère Calmar : Calmar > BH.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py
diversification_bond_overlay_dax`, n_trials=taille totale du backlog
(jamais 1).

## Anti-cheat

Ce fichier committé avant
`nonml_diversification_bond_overlay_dax_backtest.py`, vérification via
`nonml_anti_cheat_check.py diversification_bond_overlay_dax`. Fichier
de données `data/de10y_monthly.csv` committé en même temps que ce
PREREG.
