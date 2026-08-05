# Robustesse — Overlay vol-targeting gaté par la prévision GJR-t walk-forward (grilles CAP et fenêtre de vol réalisée, PAS un retuning de T0/REFIT_EVERY/MEDIAN_WINDOW)

CAP pré-enregistré = 2.0x, fenêtre de vol réalisée pré-enregistrée = 20j. T0=750, REFIT_EVERY=21j et MEDIAN_WINDOW=252 (paramètres du modèle GJR-t et de la porte elle-même) restent fixes — la prévision et la porte sont calculées une seule fois, la grille ne fait que re-mapper la même série en positions. Marché unique NDX (périmètre du #234).

## Grille CAP (fenêtre de vol réalisée fixée à 20j)

| CAP | PASS |
|---|---|
| 1.5x | non |
| 2.0x | OUI ← CAP pré-enregistré |
| 2.5x | OUI |
| 3.0x | OUI |

## Grille fenêtre de vol réalisée (CAP fixé à 2.0x)

| Fenêtre | PASS |
|---|---|
| 15j | non |
| 20j | OUI ← fenêtre pré-enregistrée |
| 25j | non |
| 30j | non |
