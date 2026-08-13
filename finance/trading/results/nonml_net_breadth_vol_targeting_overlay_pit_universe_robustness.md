# Robustesse — breadth nette hauts-bas, univers POINT-IN-TIME

Grilles **identiques** à celles du cycle d'origine, donc fixées avant exécution.
**Pas un retuning** : `INDEX_LOOKBACK` (252), les seuils de proximité (0,95 / 1,05)
et le **seuil de porte (0,0)** définissent l'hypothèse et restent figés.

CAP pré-enregistré = 2.0×, fenêtre de vol pré-enregistrée = 20 j.

## Grille CAP (fenêtre fixée à 20 j)

| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 1.5× | OUI | +0.78 | +815.5% |
| 2.0× ← pré-enregistré | OUI | +0.79 | +930.4% |
| 2.5× | OUI | +0.79 | +972.2% |
| 3.0× | OUI | +0.79 | +977.2% |

## Grille fenêtre de vol (CAP fixé à 2.0×)

| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 15 j | OUI | +0.76 | +863.7% |
| 20 j ← pré-enregistré | OUI | +0.79 | +930.4% |
| 25 j | OUI | +0.78 | +869.0% |
| 30 j | OUI | +0.79 | +883.5% |

**4/4 cellules PASS sur la grille CAP, 4/4 sur la grille de fenêtre.** Rapporté tel quel, sans réajustement.

Le cycle d'origine (univers biaisé par le survivant) sert de point de
comparaison ; son rapport de robustesse est dans
`results/nonml_net_breadth_vol_targeting_overlay_robustness.md`.
