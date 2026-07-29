# Robustesse — Overlay vol-targeting gaté par drawdown profond, seuil absolu (grilles CAP et fenêtre, PAS un retuning du seuil -20%/252j)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.

## Grille CAP (fenêtre fixée à 20j)

| CAP | PASS (Sharpe ET rendement > BH) |
|---|---|
| 1.5x | non |
| 2.0x | OUI ← CAP pré-enregistré |
| 2.5x | OUI |
| 3.0x | OUI |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | PASS (Sharpe ET rendement > BH) |
|---|---|
| 15j | non |
| 20j | OUI ← fenêtre pré-enregistrée |
| 25j | OUI |
| 30j | OUI |
