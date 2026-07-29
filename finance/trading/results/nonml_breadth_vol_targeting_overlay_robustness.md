# Robustesse — Overlay vol-targeting gaté par breadth NDX+Russell2000 (grilles CAP et fenêtre, PAS un retuning du seuil breadth)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j. Seuil breadth 95%/252j laissé fixe (identique au #52, non retesté ici).

## Grille CAP (fenêtre fixée à 20j)

| CAP | PASS (Sharpe ET rendement > BH) |
|---|---|
| 1.5x | OUI |
| 2.0x | OUI ← CAP pré-enregistré |
| 2.5x | OUI |
| 3.0x | OUI |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | PASS (Sharpe ET rendement > BH) |
|---|---|
| 15j | OUI |
| 20j | OUI ← fenêtre pré-enregistrée |
| 25j | OUI |
| 30j | OUI |
