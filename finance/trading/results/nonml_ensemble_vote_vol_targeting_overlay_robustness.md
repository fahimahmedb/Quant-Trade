# Robustesse — Overlay vote majoritaire (grilles CAP, fenêtre de vol, ET seuil de vote)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j, seuil de vote pré-enregistré = 3/5.

## Grille CAP (fenêtre 20j, seuil de vote 3/5)

| CAP | PASS (Sharpe ET rendement > BH) |
|---|---|
| 1.5x | OUI |
| 2.0x | OUI ← CAP pré-enregistré |
| 2.5x | OUI |
| 3.0x | OUI |

## Grille fenêtre de vol (CAP 2.0x, seuil de vote 3/5)

| Fenêtre | PASS (Sharpe ET rendement > BH) |
|---|---|
| 15j | OUI |
| 20j | OUI ← fenêtre pré-enregistrée |
| 25j | OUI |
| 30j | OUI |

## Grille seuil de vote (CAP 2.0x, fenêtre 20j)

| Seuil (sur 5) | %j actif | PASS (Sharpe ET rendement > BH) |
|---|---|---|
| 2/5 | 72.1% | OUI |
| 3/5 | 53.8% | OUI ← seuil pré-enregistré |
| 4/5 | 40.3% | OUI |
