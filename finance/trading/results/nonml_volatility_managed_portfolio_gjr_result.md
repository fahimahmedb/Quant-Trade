# Résultat — Portefeuille volatility-managed (Moreira & Muir 2017), volatilité PRÉVUE GJR-GARCH-t

Spécification figée dans `PREREG_volatility_managed_portfolio_gjr.md` (committé avant ce script). n_trials = 1.

`position(t) = clip(20% / vol_prévue_GJR-t(t), 0.0, 2.0x)` — prévision walk-forward 1 pas, fenêtre initiale 750 obs expansive, ré-estimation tous les 21 j, coûts 5 bps sur |Δposition|.

## 1. Échantillon

- Marché : **NDX (40 ans)** (`data/nasdaq100_daily.txt`), 10273 séances, 10272 rendements (02/10/1985 → 13/07/2026).
- Fenêtre OOS évaluée (candidat ET Buy & Hold) : **9522 séances**, 20/09/1988 → 13/07/2026.
- Nombre de ré-estimations GJR-t : 454.

## 2. Comportement de l'exposition (descriptif, hors critère)

- Vol. annualisée **prévue** sur l'OOS : min 8.6 % / médiane 19.1 % / max 111.2 %.
- Exposition moyenne : **1.04x** (médiane 1.05x, min 0.18x, max 2.00x).
- Part du temps au-dessus de 1.0x : **54.5 %** ; au plafond 2.0x : 0.6 % ; sous 0,5x : 8.5 %.
- Turnover quotidien moyen |Δposition| : 0.0416 (coût total cumulé ≈ 19.8 points de rendement log).

## 3. Résultat sur la fenêtre OOS commune (net de coûts)

| Stratégie | Sharpe ann. | Rendement total | Rendement ann. | MDD | Calmar | Sortino |
|---|---|---|---|---|---|---|
| Buy & Hold | +0.52 | +4553.2% | +14.5% | -82.9% | 0.077 | +0.69 |
| **Volatility-managed GJR-t** | **+0.67** | **+7178.8%** | +14.3% | -59.9% | 0.146 | +0.94 |

## 4. Verdict contre le critère de succès RENFORCÉ pré-enregistré

- Jambe Sharpe : +0.6656 vs +0.5209 → **OUI**
- Jambe rendement total : +7178.8% vs +4553.2% → **OUI**

**PASS — les deux jambes sont atteintes (critère renforcé du 28/07/2026 : Sharpe ET rendement > Buy & Hold).**

## 5. Rappel Règle 10 (hypothèse de rémunération déclarée au PREREG)

La fraction hors-marché `(1 - position)` est rémunérée à **0 %** et la fraction empruntée (position > 1.0x) est financée à **0 %**. Cette asymétrie est déclarée, pas neutre : elle pénalise la stratégie quand elle est sous-investie et l'avantage quand elle est levée. Elle est identique à la convention des cycles #43/#46/#44/#115/#118 auxquels ce résultat doit être comparé.

**PASS de niveau 1 seulement — ce n'est PAS un verdict final.** La batterie renforcée de la Règle 9 (`scripts/nonml_pass_validation_battery.py volatility_managed_portfolio_gjr`), la grille de robustesse ±20 % et la décomposition Règle 10 doivent toutes être exécutées avant toute déclaration de validation.
