# Résultat — Overlay défensif EWMA + ensemble 3 moteurs (pré-enregistré)

## 1. EWMA seul (walk-forward, λ=0.94, T0=750, REFIT_EVERY=21j)

9522 séances OOS.

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (NDX) | +0.52 | +4553.2% | -82.9% | 0.077 |
| **Overlay EWMA défensif** | **+0.70** | **+6221.4%** | -56.5% | **0.151** |

Critère standard : PASS. Critère Calmar : PASS.

## 2. Ensemble à 3 moteurs (#115 + GARCH#118 + EWMA)/3, fenêtre commune 9522 séances

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (NDX) | +0.52 | +4553.2% | -82.9% | 0.077 |
| **Overlay 3 moteurs** | **+0.70** | **+7718.4%** | -56.9% | **0.159** |

Critère standard : PASS. Critère Calmar : PASS.

## Comparaison au #121 (ensemble à 2 moteurs, déjà committé) : rendements décroissants ?

| Ensemble | Sharpe ann. | Calmar |
|---|---|---|
| #121 (2 moteurs : réalisé + GARCH) | +0.69 | 0.162 |
| #124 (3 moteurs : réalisé + GARCH + EWMA) | +0.70 | 0.159 |

**Au moins un PASS niveau 1 (EWMA seul et/ou ensemble 3 moteurs) sur au moins un critère -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py` avant toute déclaration finale.**
