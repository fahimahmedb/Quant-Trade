# Robustesse — concentration du marché (HHI), univers POINT-IN-TIME

Grilles **identiques** à celles du cycle d'origine, donc fixées avant exécution.
**Pas un retuning** : `CONC_WINDOW` (60),
`MEDIAN_WINDOW` (252) et `MIN_LISTED` (10) définissent l'hypothèse et restent figés.

CAP pré-enregistré = 2.0×, fenêtre de vol pré-enregistrée = 20 j.

## Grille CAP (fenêtre fixée à 20 j)

| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 1.5× | OUI | +0.83 | +696.7% |
| 2.0× ← pré-enregistré | OUI | +0.85 | +793.0% |
| 2.5× | OUI | +0.85 | +824.6% |
| 3.0× | OUI | +0.85 | +827.3% |

## Grille fenêtre de vol (CAP fixé à 2.0×)

| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 15 j | OUI | +0.80 | +704.6% |
| 20 j ← pré-enregistré | OUI | +0.85 | +793.0% |
| 25 j | OUI | +0.84 | +772.1% |
| 30 j | OUI | +0.84 | +762.9% |

**4/4 cellules PASS sur la grille CAP, 4/4 sur la grille de fenêtre.** Rapporté tel quel, sans réajustement.

Le cycle d'origine (univers biaisé par le survivant) sert de point de
comparaison ; son rapport de robustesse est dans
`results/nonml_market_concentration_vol_targeting_overlay_robustness.md`.
