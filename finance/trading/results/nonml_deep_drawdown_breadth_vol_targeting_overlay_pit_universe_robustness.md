# Robustesse — breadth de drawdown profond, univers POINT-IN-TIME

Grilles **identiques** à celles du cycle d'origine, donc fixées avant
exécution. **Pas un retuning** : le seuil de drawdown (−20 %) et la fenêtre
de médiane (252j), au cœur du critère, restent figés.

CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.

## Grille CAP (fenêtre fixée à 20j)

| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement | MDD |
|---|---|---|---|---|
| 1.5x | OUI | +0.81 | +644.0% | -36.3% |
| 2.0x | OUI ← CAP pré-enregistré | +0.82 | +698.4% | -36.9% |
| 2.5x | OUI | +0.83 | +718.6% | -36.9% |
| 3.0x | OUI | +0.83 | +726.9% | -36.9% |

**4/4 cellules PASS sur la grille CAP.**

## Grille fenêtre de volatilité (CAP fixé à 2.0x)

| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement | MDD |
|---|---|---|---|---|
| 15j | OUI | +0.82 | +686.9% | -36.6% |
| 20j | OUI ← fenêtre pré-enregistrée | +0.82 | +698.4% | -36.9% |
| 25j | OUI | +0.81 | +669.1% | -37.0% |
| 30j | OUI | +0.81 | +651.3% | -36.8% |

**4/4 cellules PASS sur la grille fenêtre.**

## Lecture

**8/8 cellules PASS au total.** Rapporté tel quel, sans réajustement.
