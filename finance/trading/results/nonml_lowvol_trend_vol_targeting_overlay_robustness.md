# Robustesse — Low-Vol + overlay combiné tendance + vol-targeting (grilles CAP et fenêtre, PAS un retuning)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.

## Grille CAP (fenêtre fixée à 20j)

| CAP | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |
|---|---|---|---|---|---|
| 1.5x | OUI | OUI | +0.77 | +78.8% | -19.4% |
| 2.0x | OUI | OUI | +0.81 | +100.3% | -19.4% ← CAP pré-enregistré |
| 2.5x | OUI | OUI | +0.79 | +103.0% | -19.4% |
| 3.0x | OUI | OUI | +0.76 | +99.8% | -19.4% |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |
|---|---|---|---|---|---|
| 15j | OUI | OUI | +0.82 | +101.7% | -19.2% |
| 20j | OUI | OUI | +0.81 | +100.3% | -19.4% ← fenêtre pré-enregistrée |
| 25j | OUI | OUI | +0.82 | +102.8% | -19.0% |
| 30j | OUI | OUI | +0.84 | +106.9% | -19.2% |
