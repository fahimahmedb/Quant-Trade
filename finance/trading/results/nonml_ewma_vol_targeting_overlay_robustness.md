# Robustesse — Overlay vol-targeting EWMA (grilles CAP et fenêtre d'amorçage, PAS un retuning de λ)

CAP pré-enregistré = 2.0x, fenêtre d'amorçage pré-enregistrée = 20j. λ=0.94 (paramètre réutilisé de ewma_path, Étape C) reste fixe.

## Grille CAP (fenêtre d'amorçage fixée à 20j)

| CAP | Nb marchés PASS /5 |
|---|---|
| 1.5x | 4/5 |
| 2.0x | 3/5 ← CAP pré-enregistré |
| 2.5x | 4/5 |
| 3.0x | 4/5 |

## Grille fenêtre d'amorçage (CAP fixé à 2.0x)

| Fenêtre | Nb marchés PASS /5 |
|---|---|
| 15j | 3/5 |
| 20j | 3/5 ← fenêtre pré-enregistrée |
| 25j | 3/5 |
| 30j | 3/5 |
