# Robustesse — breadth « petites caps » proxy, univers POINT-IN-TIME

Grilles **identiques** à celles du cycle d'origine, donc fixées avant exécution.
**Pas un retuning** : `IDIO_VOL_WINDOW` (60), `MOM_WINDOW` (21),
`MEDIAN_WINDOW` (252) et le seuil médian définissent l'hypothèse et restent figés.

CAP pré-enregistré = 2.0×, fenêtre de vol pré-enregistrée = 20 j.

## Grille CAP (fenêtre fixée à 20 j)

| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 1.5× | OUI | +0.80 | +639.6% |
| 2.0× ← pré-enregistré | OUI | +0.82 | +715.5% |
| 2.5× | OUI | +0.82 | +728.8% |
| 3.0× | OUI | +0.82 | +727.3% |

## Grille fenêtre de vol (CAP fixé à 2.0×)

| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |
|---|---|---|---|
| 15 j | non | +0.77 | +646.0% |
| 20 j ← pré-enregistré | OUI | +0.82 | +715.5% |
| 25 j | OUI | +0.80 | +668.9% |
| 30 j | non | +0.79 | +636.0% |

**4/4 cellules PASS sur la grille CAP, 2/4 sur la grille de fenêtre.** Rapporté tel quel, sans réajustement.

Pour mémoire, le cycle d'origine (univers biaisé par le survivant) obtient
**3/4** sur chacune des deux grilles après la correction du #404.
