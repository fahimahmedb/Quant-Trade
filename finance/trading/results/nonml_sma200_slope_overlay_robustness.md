# Robustesse — Overlay filtre de pente SMA200 (grilles CAP et SLOPE_LAG, PAS un retuning de la fenêtre SMA200)

CAP pré-enregistré = 2.0x, SLOPE_LAG pré-enregistré = 20j.

## Grille CAP (SLOPE_LAG fixé à 20j)

| CAP | Nb marchés PASS /5 |
|---|---|
| 1.5x | 5/5 |
| 2.0x | 5/5 ← CAP pré-enregistré |
| 2.5x | 5/5 |
| 3.0x | 5/5 |

## Grille SLOPE_LAG (CAP fixé à 2.0x)

| SLOPE_LAG | Nb marchés PASS /5 |
|---|---|
| 15j | 5/5 |
| 20j | 5/5 ← SLOPE_LAG pré-enregistré |
| 25j | 5/5 |
| 30j | 5/5 |
