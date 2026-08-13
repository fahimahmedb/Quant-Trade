# Robustesse — dispersion du momentum, univers POINT-IN-TIME

Grilles **identiques** à celles du cycle d'origine, donc fixées avant exécution.
**Pas un retuning** : `LOOKBACK` (252), `SKIP` (21),
`MEDIAN_WINDOW` (252) et `MIN_LISTED` (10) définissent l'hypothèse et restent figés.

CAP pré-enregistré = 2.0×, fenêtre de vol pré-enregistrée = 20 j.

## Grille CAP (fenêtre fixée à 20 j)

| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 1.5× | OUI | +0.82 | +669.4% |
| 2.0× ← pré-enregistré | OUI | +0.84 | +737.7% |
| 2.5× | OUI | +0.84 | +754.8% |
| 3.0× | OUI | +0.83 | +748.0% |

## Grille fenêtre de vol (CAP fixé à 2.0×)

| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 15 j | OUI | +0.79 | +652.9% |
| 20 j ← pré-enregistré | OUI | +0.84 | +737.7% |
| 25 j | OUI | +0.83 | +723.4% |
| 30 j | OUI | +0.83 | +718.7% |

**4/4 cellules PASS sur la grille CAP, 4/4 sur la grille de fenêtre.** Rapporté tel quel, sans réajustement.

Le cycle d'origine (univers biaisé par le survivant) sert de point de
comparaison ; son rapport de robustesse est dans
`results/nonml_momentum_dispersion_vol_targeting_overlay_robustness.md`.
