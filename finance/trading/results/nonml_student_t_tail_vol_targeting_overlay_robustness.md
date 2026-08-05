# Robustesse — Overlay vol-targeting gaté par le ν glissant (MLE Student-t) (grilles CAP et fenêtre de vol, PAS un retuning de NU_WINDOW/REFIT_EVERY/MEDIAN_WINDOW)

CAP pré-enregistré = 2.0x, fenêtre de vol pré-enregistrée = 20j. NU_WINDOW=252, REFIT_EVERY=21j et MEDIAN_WINDOW=252 (paramètres du signal de porte lui-même) restent fixes, comme pour toutes les portes précédentes de cette famille (#47/#54/#57/#78/#80/#216-#223/#234). La porte n'est calculée qu'une seule fois par marché (5 marchés).

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
