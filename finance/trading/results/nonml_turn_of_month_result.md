# Résultat — Effet tournant de mois (pré-enregistré, exécuté une fois)

Fenêtre ToM = 4 derniers j. de bourse du mois + 3 premiers j. du mois suivant (Lakonishok & Smidt 1988).

| Marché | BH Sharpe | ToM-only Sharpe | % jours en ToM | ToM bat BH ? |
|---|---|---|---|---|
| Composite (5 ans) | +0.52 | +0.21 | 34.1% | non |
| NDX (40 ans) | +0.53 | +0.57 | 33.4% | OUI |
| Russell 2000 | +0.34 | +0.61 | 33.4% | OUI |
| S&P 500 | +0.45 | +0.59 | 33.3% | OUI |
| DAX | +0.25 | +0.46 | 33.1% | OUI |

**4/5 marchés où ToM-only bat Buy&Hold net de coûts (critère pré-enregistré : ≥4/5).**

**PASS — critère pré-enregistré atteint.**

## Décomposition brute (rendement moyen quotidien, avant coûts)

| Marché | Rendement moy./j EN ToM (brut) | Rendement moy./j HORS ToM (brut) |
|---|---|---|
| Composite (5 ans) | +0.0455% | +0.0471% |
| NDX (40 ans) | +0.1156% | +0.0235% |
| Russell 2000 | +0.1019% | -0.0072% |
| S&P 500 | +0.0824% | +0.0050% |
| DAX | +0.0840% | -0.0082% |

**Lecture honnête** : contrairement à overnight/intraday (turnover quotidien), cette stratégie ne transacte qu'environ 24 fois par an — les coûts pèsent beaucoup moins. Si le critère échoue malgré ça, c'est un signal plus direct que l'effet, si présent dans la décomposition brute, n'est pas assez fort pour battre le Buy&Hold en risque-ajusté sur cet échantillon, pas juste noyé par les coûts.
