# Résultat — Décomposition du turn-of-month (pré-enregistré, 2 variantes, règle renforcée)

## Variante A — fin de mois seule

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.52 | +79.0% | -36.4% | +0.50 | +101.5% | -40.4% | 19.5% | non | OUI |
| NDX (40 ans) | +0.53 | +26208.9% | -82.9% | +0.53 | +100638.1% | -89.3% | 19.1% | OUI | OUI |
| Russell 2000 | +0.34 | +1646.9% | -59.9% | +0.47 | +12944.0% | -49.8% | 19.1% | OUI | OUI |
| S&P 500 | +0.45 | +7977.0% | -56.8% | +0.47 | +28925.8% | -58.4% | 19.1% | OUI | OUI |
| DAX | +0.25 | +353.5% | -72.7% | +0.29 | +771.1% | -68.1% | 18.9% | OUI | OUI |

**4/5 marchés (critère renforcé : ≥4/5).**
**PASS** pour la variante A — fin de mois seule.

## Variante B — début de mois seul

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.52 | +79.0% | -36.4% | +0.40 | +71.0% | -41.4% | 14.6% | non | non |
| NDX (40 ans) | +0.53 | +26208.9% | -82.9% | +0.56 | +136057.9% | -85.8% | 14.3% | OUI | OUI |
| Russell 2000 | +0.34 | +1646.9% | -59.9% | +0.32 | +2472.5% | -71.7% | 14.3% | non | OUI |
| S&P 500 | +0.45 | +7977.0% | -56.8% | +0.49 | +28968.0% | -64.9% | 14.3% | OUI | OUI |
| DAX | +0.25 | +353.5% | -72.7% | +0.29 | +719.9% | -76.2% | 14.2% | OUI | OUI |

**3/5 marchés (critère renforcé : ≥4/5).**
**FAIL** pour la variante B — début de mois seul.

## Synthèse

- Variante A — fin de mois seule : 4/5 — **PASS**
- Variante B — début de mois seul : 3/5 — **FAIL**

Rappel : le #8 (ToM complet, union des deux sous-fenêtres) est PASS (4/5).
