# Robustesse — Overlay proximité plus haut 52-semaines indice (grilles CAP et seuil, PAS un retuning)

CAP pré-enregistré = 2.0x, seuil pré-enregistré = 95%.

## Grille CAP (seuil fixé à 95%)

| CAP | Nb marchés PASS /5 |
|---|---|
| 1.5x | 5/5 |
| 2.0x | 5/5 ← CAP pré-enregistré |
| 2.5x | 5/5 |
| 3.0x | 5/5 |

## Grille seuil de proximité (CAP fixé à 2.0x)

| Seuil | Nb marchés PASS /5 |
|---|---|
| 90% | 5/5 |
| 93% | 5/5 |
| 95% | 5/5 ← seuil pré-enregistré |
| 97% | 1/5 |
