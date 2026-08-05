# Robustesse — Overlay vol-targeting gaté par la conjonction (ET) kurtosis + ν Student-t (grilles CAP et fenêtre de vol, PAS un retuning des paramètres des deux sous-portes)

CAP pré-enregistré = 2.0x, fenêtre de vol pré-enregistrée = 20j. Les paramètres des deux sous-portes (KURT_WINDOW=252, NU_WINDOW=252, REFIT_EVERY=21, MEDIAN_WINDOW=252) restent fixes. La conjonction n'est calculée qu'une seule fois par marché (5 marchés).

## Grille CAP (fenêtre fixée à 20j)

| CAP | Nb marchés PASS /5 |
|---|---|
| 1.5x | 4/5 |
| 2.0x | 4/5 ← CAP pré-enregistré |
| 2.5x | 3/5 |
| 3.0x | 3/5 |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | Nb marchés PASS /5 |
|---|---|
| 15j | 2/5 |
| 20j | 4/5 ← fenêtre pré-enregistrée |
| 25j | 4/5 |
| 30j | 3/5 |
