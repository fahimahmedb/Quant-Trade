# Audit adversarial — Overlay défensif durée du drawdown

## 1. Recalcul indépendant de duration(t)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |
| DAX | 6777 | 0 |

**OK — duration(t) confirmée par recalcul indépendant (0 désaccord).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 3000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 5000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 8000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
