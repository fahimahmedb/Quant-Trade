# Robustesse — Overlay vol-targeting gaté par la kurtosis glissante (grilles CAP et fenêtre, PAS un retuning de KURT_WINDOW ni de MEDIAN_WINDOW)

CAP pré-enregistré = 2.0x, fenêtre de vol pré-enregistrée = 20j. KURT_WINDOW=252 et MEDIAN_WINDOW=252 (paramètres du signal de porte lui-même) restent fixes, comme pour toutes les portes précédentes de cette famille (#47/#54/#57/#68/#78/#80/#216/#217/#218).

## Grille CAP (fenêtre fixée à 20j)

| CAP | Nb marchés PASS /5 |
|---|---|
| 1.5x | 4/5 |
| 2.0x | 4/5 ← CAP pré-enregistré |
| 2.5x | 4/5 |
| 3.0x | 4/5 |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | Nb marchés PASS /5 |
|---|---|
| 15j | 4/5 |
| 20j | 4/5 ← fenêtre pré-enregistrée |
| 25j | 4/5 |
| 30j | 4/5 |
