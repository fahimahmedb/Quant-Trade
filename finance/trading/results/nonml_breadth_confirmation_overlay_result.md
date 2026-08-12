# Résultat — Overlay de confirmation multi-marché NDX+Russell2000 (pré-enregistré, règle renforcée)

Position sur NDX = 1.0x en permanence, CAP=2.0x quand NDX ET Russell 2000 sont SIMULTANÉMENT ≥95% de leur plus haut 252j. 10020 séances testables (1986-09-30 → 2026-07-13).

%j confirmé NDX seul (signal A) : 54.6%
%j confirmé Russell 2000 seul (signal B, aligné ffill) : 44.8%
%j confirmation croisée (A∩B, overlay actif) : 38.5%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.52 | +21358.1% | -82.9% |
| **Overlay confirmation multi-marché x2.0** | **+0.53** | **+76614.6%** | -83.8% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
