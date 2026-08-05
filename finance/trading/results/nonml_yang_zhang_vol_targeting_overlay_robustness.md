# Robustesse — Overlay vol-targeting Yang-Zhang (grilles CAP et fenêtre, PAS un retuning)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j (n dans la formule YZ, y compris le facteur k qui en dépend, recalculé pour chaque fenêtre testée).

## Grille CAP (fenêtre fixée à 20j)

| CAP | Nb marchés PASS /5 |
|---|---|
| 1.5x | 5/5 |
| 2.0x | 5/5 ← CAP pré-enregistré |
| 2.5x | 4/5 |
| 3.0x | 4/5 |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | Nb marchés PASS /5 |
|---|---|
| 15j | 3/5 |
| 20j | 5/5 ← fenêtre pré-enregistrée |
| 25j | 4/5 |
| 30j | 4/5 |
