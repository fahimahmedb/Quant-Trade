# Pré-enregistrement — Pente de la courbe des taux US (T10Y2Y) appliquée au Russell 2000

**Committé AVANT tout calcul.** Cycle #128 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Complète le tableau cross-marché du signal T10Y2Y (mécanisme du #114) :
NDX (PASS niveau 1 + SPA significatif, mais succès en crise partiellement
fortuit d'après le diagnostic #127), S&P 500 (#126, FAIL net — porte
active pendant les crises, MDD dégradé). Dernier marché indépendant
autorisé par la Règle 3 : **Russell 2000** (small-caps US), plus
sensible au cycle du crédit que le S&P 500 large-cap — la pente de la
courbe des taux, indicateur de conditions de crédit, pourrait avoir une
pertinence économique différente sur ce segment. Choix pré-enregistré
AVANT tout calcul (pas après avoir vu S&P 500 échouer) : ce marché était
déjà nommé comme "dernier restant" dans la proposition du backlog #126,
avant l'exécution du #126 lui-même.

## Définition (fixée ici, avant tout résultat — IDENTIQUE au #114/#126,
seul le marché piloté change)

- Signal, alignement causal, MEDIAN_WINDOW, mécanisme, coûts :
  IDENTIQUES au #114/#126, AUCUN paramètre retuné.
- **Univers piloté** : Russell 2000 (`russell2000_daily.txt`, déjà en
  local).
- **Référence** : Buy & Hold sur Russell 2000.

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1 pour ce marché précis.

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

`scripts/nonml_pass_validation_battery.py yield_curve_slope_russell2000_
vol_targeting_overlay`, n_trials=taille totale du backlog.

## Robustesse prévue (SI PASS niveau 1)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j}.

## Anti-cheat

Ce fichier committé avant
`nonml_yield_curve_slope_russell2000_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
yield_curve_slope_russell2000_vol_targeting_overlay`.
