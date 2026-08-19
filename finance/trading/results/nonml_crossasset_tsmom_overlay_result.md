# Momentum cross-actifs — E3 (pré-enregistré, exécuté une fois)

Fenêtre commune : **2017-08-22 → 2026-07-13** (2233 séances). Jambes : NDX, TLT, GLD, UUP. Lookback TSMOM causal : **252** séances.

## Fraction du temps, chaque jambe active

| Jambe | % du temps active (tendance positive) |
|---|---|
| NDX | 86.5 % |
| TLT | 32.1 % |
| GLD | 74.2 % |
| UUP | 55.2 % |

- exposition brute moyenne du portefeuille : **62.0 %** (vs 100 % pour Buy&Hold)

## Niveau 1 — Sharpe et rendement net de coûts

| | Overlay TSMOM | Buy&Hold équipondéré |
|---|---|---|
| Sharpe annualisé | +0.83 | +0.98 |
| Rendement total net | +66.0 % | +104.3 % |
| MDD | -9.9 % | -17.6 % |

**PASS niveau 1** (Sharpe ET rendement > Buy&Hold) : **NON**

## Règle 9

**Sans objet** — niveau 1 déjà FAIL, la batterie Règle 9 ne s'applique qu'aux PASS niveau 1 (convention du backlog).

## Mes trois prédictions, confrontées

| Prédiction | Verdict |
|---|---|
| PASS niveau 1 (50/50, incertain) | mesuré : FAIL |
| Si PASS niveau 1, DSR échoue (cohérent 372 essais) | **sans objet** — la prémisse (PASS niveau 1) ne tient pas |

## Critères de succès (procédure de ce cycle)

1. Univers et fenêtre conformes au pré-enregistrement — **OUI**.
2. Niveau 1 calculé et publié — **OUI**.
3. Règle 9 exécutée si niveau 1 PASS, sinon explicitement sans objet — **OUI**.
4. Aucun ajustement du signal après résultat intermédiaire — **OUI**.
5. `.npz` sauvegardé au schéma portefeuille pour audit indépendant — **OUI**.

**PASS** (procédure) — verdict de la stratégie elle-même : niveau 1 **FAIL**.
