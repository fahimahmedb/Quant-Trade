# Robustesse — Overlay vol-targeting gaté par le ratio de variance de Lo-MacKinlay glissant (grilles CAP et fenêtre, PAS un retuning de Q ni de VR_WINDOW)

CAP pré-enregistré = 2.0x, fenêtre de vol pré-enregistrée = 20j. Q=5 et VR_WINDOW=252 (paramètres du signal de porte lui-même) restent fixes, comme pour toutes les portes précédentes de cette famille (#47/#54/#57/#68/#78/#80/#216).

## Grille CAP (fenêtre fixée à 20j)

| CAP | Nb marchés PASS /5 |
|---|---|
| 1.5x | 4/5 |
| 2.0x | 4/5 ← CAP pré-enregistré |
| 2.5x | 4/5 |
| 3.0x | 3/5 |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | Nb marchés PASS /5 |
|---|---|
| 15j | 2/5 |
| 20j | 4/5 ← fenêtre pré-enregistrée |
| 25j | 3/5 |
| 30j | 3/5 |
