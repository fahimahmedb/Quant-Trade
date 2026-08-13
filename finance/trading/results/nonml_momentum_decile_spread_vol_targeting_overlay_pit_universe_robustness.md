# Robustesse — spread décile de momentum, univers POINT-IN-TIME

Grilles **identiques** à celles du cycle d'origine, donc fixées avant exécution.
**Pas un retuning** : `LOOKBACK` (252), `SKIP` (21),
`MEDIAN_WINDOW` (252) et `DECILE_FRACTION` (0,10) définissent l'hypothèse et restent figés.

CAP pré-enregistré = 2.0×, fenêtre de vol pré-enregistrée = 20 j.

## Grille CAP (fenêtre fixée à 20 j)

| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 1.5× | OUI | +0.82 | +678.6% |
| 2.0× ← pré-enregistré | OUI | +0.84 | +755.8% |
| 2.5× | OUI | +0.85 | +783.6% |
| 3.0× | OUI | +0.84 | +783.2% |

## Grille fenêtre de vol (CAP fixé à 2.0×)

| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 15 j | non | +0.78 | +651.7% |
| 20 j ← pré-enregistré | OUI | +0.84 | +755.8% |
| 25 j | OUI | +0.84 | +747.2% |
| 30 j | OUI | +0.84 | +746.8% |

**4/4 cellules PASS sur la grille CAP, 3/4 sur la grille de fenêtre.** Rapporté tel quel, sans réajustement.

Le cycle d'origine (univers biaisé par le survivant) sert de point de
comparaison ; son rapport de robustesse est dans
`results/nonml_momentum_decile_spread_vol_targeting_overlay_robustness.md`.
