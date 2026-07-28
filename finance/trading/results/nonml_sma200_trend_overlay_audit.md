# Audit adversarial — Overlay levé filtre de tendance SMA200

## 1. Recalcul indépendant du masque (boucle explicite vs pandas.rolling)

| Marché | Écart masque (nb j., hors 200 premiers) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — SMA200 et masque confirmés par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures, décisions passées strictement causales.**

## 3. Exposition pendant les grands krachs (drawdown ≥40% depuis le plus haut)

| Marché | %j levé PENDANT drawdown≥40% |
|---|---|
| Composite (5 ans) | nan% |
| NDX (40 ans) | 61.6% |
| Russell 2000 | 8.5% |
| S&P 500 | 6.6% |
| DAX | 50.6% |
