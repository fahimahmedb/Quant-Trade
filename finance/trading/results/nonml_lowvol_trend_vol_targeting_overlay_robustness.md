# Robustesse — Low-Vol + overlay combiné tendance + vol-targeting (grilles CAP et fenêtre, PAS un retuning)

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.

## Grille CAP (fenêtre fixée à 20j)

| CAP | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |
|---|---|---|---|---|---|
| 1.5x | OUI | OUI | +0.92 | +117.9% | -18.0% |
| 2.0x | OUI | OUI | +0.96 | +151.8% | -17.9% ← CAP pré-enregistré |
| 2.5x | OUI | OUI | +0.93 | +158.8% | -17.9% |
| 3.0x | OUI | OUI | +0.90 | +155.6% | -17.9% |

## Grille fenêtre de vol (CAP fixé à 2.0x)

| Fenêtre | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |
|---|---|---|---|---|---|
| 15j | OUI | OUI | +0.97 | +153.3% | -17.7% |
| 20j | OUI | OUI | +0.96 | +151.8% | -17.9% ← fenêtre pré-enregistrée |
| 25j | OUI | OUI | +0.97 | +154.9% | -17.6% |
| 30j | OUI | OUI | +0.99 | +160.3% | -17.7% |
