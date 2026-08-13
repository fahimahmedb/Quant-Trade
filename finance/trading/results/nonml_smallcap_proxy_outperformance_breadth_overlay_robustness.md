# Robustesse — Overlay vol-targeting gaté par surperformance petites caps (grilles CAP et fenêtre, PAS un retuning de IdioVol/Mom/seuil médian)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.

## Grille CAP (fenêtre fixée à 20j)

| CAP | PASS (Sharpe ET rendement > BH) |
|---|---|
| 1.5x | OUI |
| 2.0x | OUI ← CAP pré-enregistré |
| 2.5x | OUI |
| 3.0x | non |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | PASS (Sharpe ET rendement > BH) |
|---|---|
| 15j | non |
| 20j | OUI ← fenêtre pré-enregistrée |
| 25j | OUI |
| 30j | OUI |
