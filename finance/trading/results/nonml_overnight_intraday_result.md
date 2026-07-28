# Résultat — Overnight vs Intraday (pré-enregistré, exécuté une fois)

| Marché | BH Sharpe | Overnight Sharpe | Intraday Sharpe | Overnight bat BH ? | Intraday bat BH ? |
|---|---|---|---|---|---|
| Composite (5 ans) | +0.52 | -0.45 | -0.38 | non | non |
| NDX (40 ans) | +0.53 | -0.69 | -0.16 | non | non |
| Russell 2000 | +0.34 | -2.05 | -0.36 | non | non |
| S&P 500 | +0.45 | -2.82 | -0.38 | non | non |
| DAX | +0.25 | -0.57 | -0.70 | non | non |

**0/5 marchés où Overnight-only OU Intraday-only bat Buy&Hold net de coûts (critère pré-enregistré : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**

## Décomposition brute (rendement moyen quotidien, avant coûts)

| Marché | Rendement overnight moy./j (brut) | Rendement intraday moy./j (brut) |
|---|---|---|
| Composite (5 ans) | +0.0249% | +0.0217% |
| NDX (40 ans) | +0.0189% | +0.0354% |
| Russell 2000 | +0.0075% | +0.0217% |
| S&P 500 | +0.0053% | +0.0255% |
| DAX | +0.0266% | -0.0042% |

**Lecture honnête** : Overnight-only et Intraday-only impliquent une transaction PAR JOUR (turnover maximal), contre 1 seule transaction pour Buy & Hold sur toute la période — un coût de 5bps/jour peut à lui seul dominer un rendement moyen quotidien qui est typiquement de l'ordre de quelques points de base. Si le critère échoue, ce n'est pas nécessairement parce que l'anomalie overnight n'existe pas (la décomposition brute ci-dessus le dit), mais parce qu'elle n'est pas monétisable à ce niveau de coûts de transaction avec un rebalancement quotidien — distinction importante, pas masquée.
