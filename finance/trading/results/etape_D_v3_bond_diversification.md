# Étape D v3 — Overlay défensif (vol-targeting réalisée) + diversification obligataire vs Buy & Hold

Formalise dans l'infrastructure officielle Étape D le mécanisme déjà validé dans le backlog non-ML (`PREREG_defensive_calmar_vol_targeting_overlay.md` = #115, `PREREG_defensive_diversification_bond_overlay.md` = #134, PASS niveau 1, meilleur score Règle 9 du backlog non-ML : 4/5 — coûts/crise/stabilité OK, SPA/DSR à n_trials=backlog encore en échec).

**Protocole figé** : `TARGET_VOL_ANNUAL=20%` (variantes 20) ou `15%` (variante 15), `VOL_WINDOW=20j`, `CAP=1.0×` (jamais de levier — mécanisme DÉFENSIF), proxy obligataire Trésor US 10 ans (DGS10, duration modifiée, formule fermée) ; coûts 5 bps aller-retour ; univers de 4 variantes (N=4 pour le DSR), figé avant évaluation.

## Composite (5 ans)

- Fenêtre : 11/08/2021 → 10/07/2026 (1230 obs, ~4.9 ans).
- Exposition équity cible 20% : moy. 0.89×, min 0.33×, max 1.00× — cible 15% : moy. 0.77×, min 0.25×, max 1.00× (cap 1.0×, jamais de levier).

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.72 | +0.26 | -36.4 | +12.5 | 1.09 | 0.850 |
| VolTarget-Défensif20 | +0.62 | +0.89 | +0.32 | -29.8 | +12.1 | 1.11 | 0.897 |
| VolTarget-Défensif20+Diversification | +0.59 | +0.85 | +0.28 | -32.5 | +11.5 | 1.10 | 0.882 |
| VolTarget-Défensif15+Diversification | +0.60 | +0.86 | +0.26 | -30.2 | +9.9 | 1.10 | 0.886 |

- **VolTarget-Défensif20 vs BuyHold** : réduction MDD relative = +18.2% (seuil >25%), rendement ann. conservé = 97.0% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget-Défensif20+Diversification vs BuyHold** : réduction MDD relative = +10.6% (seuil >25%), rendement ann. conservé = 91.8% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget-Défensif15+Diversification vs BuyHold** : réduction MDD relative = +17.1% (seuil >25%), rendement ann. conservé = 78.9% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**

## NDX (40 ans)

- Fenêtre : 30/10/1985 → 13/07/2026 (10252 obs, ~40.7 ans).
- Exposition équity cible 20% : moy. 0.87×, min 0.19×, max 1.00× — cible 15% : moy. 0.76×, min 0.14×, max 1.00× (cap 1.0×, jamais de levier).

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.53 | +0.68 | +0.08 | -82.9 | +14.6 | 1.10 | 0.993 |
| VolTarget-Défensif20 | +0.71 | +0.99 | +0.15 | -58.5 | +13.6 | 1.13 | 1.000 |
| VolTarget-Défensif20+Diversification | +0.77 | +1.08 | +0.19 | -50.9 | +14.8 | 1.14 | 1.000 |
| VolTarget-Défensif15+Diversification | +0.84 | +1.17 | +0.26 | -37.9 | +13.4 | 1.15 | 1.000 |

- **VolTarget-Défensif20 vs BuyHold** : réduction MDD relative = +29.4% (seuil >25%), rendement ann. conservé = 93.4% du BuyHold (seuil ≥80%) → **critère de succès atteint**
- **VolTarget-Défensif20+Diversification vs BuyHold** : réduction MDD relative = +38.6% (seuil >25%), rendement ann. conservé = 101.7% du BuyHold (seuil ≥80%) → **critère de succès atteint**
- **VolTarget-Défensif15+Diversification vs BuyHold** : réduction MDD relative = +54.3% (seuil >25%), rendement ann. conservé = 91.8% du BuyHold (seuil ≥80%) → **critère de succès atteint**

## S&P 500

- Fenêtre : 02/02/1970 → 13/07/2026 (14231 obs, ~56.4 ans).
- Exposition équity cible 20% : moy. 0.96×, min 0.19×, max 1.00× — cible 15% : moy. 0.91×, min 0.15×, max 1.00× (cap 1.0×, jamais de levier).

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.46 | +0.58 | +0.09 | -56.8 | +8.3 | 1.09 | 0.998 |
| VolTarget-Défensif20 | +0.51 | +0.69 | +0.10 | -51.4 | +7.7 | 1.09 | 1.000 |
| VolTarget-Défensif20+Diversification | +0.55 | +0.74 | +0.12 | -50.1 | +8.3 | 1.10 | 1.000 |
| VolTarget-Défensif15+Diversification | +0.60 | +0.83 | +0.13 | -45.0 | +8.1 | 1.11 | 1.000 |

- **VolTarget-Défensif20 vs BuyHold** : réduction MDD relative = +9.4% (seuil >25%), rendement ann. conservé = 93.7% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget-Défensif20+Diversification vs BuyHold** : réduction MDD relative = +11.8% (seuil >25%), rendement ann. conservé = 101.0% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget-Défensif15+Diversification vs BuyHold** : réduction MDD relative = +20.8% (seuil >25%), rendement ann. conservé = 98.2% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**

## Russell 2000

- Fenêtre : 09/10/1987 → 13/07/2026 (9761 obs, ~38.8 ans).
- Exposition équity cible 20% : moy. 0.92×, min 0.18×, max 1.00× — cible 15% : moy. 0.83×, min 0.13×, max 1.00× (cap 1.0×, jamais de levier).

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.34 | +0.43 | +0.08 | -59.9 | +7.7 | 1.07 | 0.960 |
| VolTarget-Défensif20 | +0.39 | +0.53 | +0.11 | -46.3 | +6.8 | 1.07 | 0.980 |
| VolTarget-Défensif20+Diversification | +0.44 | +0.60 | +0.13 | -43.1 | +7.6 | 1.08 | 0.991 |
| VolTarget-Défensif15+Diversification | +0.47 | +0.64 | +0.16 | -33.1 | +6.8 | 1.08 | 0.995 |

- **VolTarget-Défensif20 vs BuyHold** : réduction MDD relative = +22.6% (seuil >25%), rendement ann. conservé = 87.8% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget-Défensif20+Diversification vs BuyHold** : réduction MDD relative = +28.0% (seuil >25%), rendement ann. conservé = 98.3% du BuyHold (seuil ≥80%) → **critère de succès atteint**
- **VolTarget-Défensif15+Diversification vs BuyHold** : réduction MDD relative = +44.7% (seuil >25%), rendement ann. conservé = 88.8% du BuyHold (seuil ≥80%) → **critère de succès atteint**

## Verdict — critère de succès explicite (identique à run_etape_d.py)

Succès = réduction du MDD >25% (relatif) **et** rendement annualisé conservé ≥80% de Buy & Hold. Vérifié, pas supposé :

| Jeu de données | Variante | ΔMDD relatif | Rdt ann. / BuyHold | Calmar (overlay vs BH) | Critère |
|---|---|---|---|---|---|
| Composite (5 ans) | VolTarget-Défensif20 | +18.2% | 97.0% | +0.32 vs +0.26 | NON |
| Composite (5 ans) | VolTarget-Défensif20+Diversification | +10.6% | 91.8% | +0.28 vs +0.26 | NON |
| Composite (5 ans) | VolTarget-Défensif15+Diversification | +17.1% | 78.9% | +0.26 vs +0.26 | NON |
| NDX (40 ans) | VolTarget-Défensif20 | +29.4% | 93.4% | +0.15 vs +0.08 | OUI |
| NDX (40 ans) | VolTarget-Défensif20+Diversification | +38.6% | 101.7% | +0.19 vs +0.08 | OUI |
| NDX (40 ans) | VolTarget-Défensif15+Diversification | +54.3% | 91.8% | +0.26 vs +0.08 | OUI |
| S&P 500 | VolTarget-Défensif20 | +9.4% | 93.7% | +0.10 vs +0.09 | NON |
| S&P 500 | VolTarget-Défensif20+Diversification | +11.8% | 101.0% | +0.12 vs +0.09 | NON |
| S&P 500 | VolTarget-Défensif15+Diversification | +20.8% | 98.2% | +0.13 vs +0.09 | NON |
| Russell 2000 | VolTarget-Défensif20 | +22.6% | 87.8% | +0.11 vs +0.08 | NON |
| Russell 2000 | VolTarget-Défensif20+Diversification | +28.0% | 98.3% | +0.13 vs +0.08 | OUI |
| Russell 2000 | VolTarget-Défensif15+Diversification | +44.7% | 88.8% | +0.16 vs +0.08 | OUI |

**Verdict honnête** : le critère de succès Étape D est atteint pour au moins une combinaison jeu de données/variante ci-dessus. Sur NDX, la variante cible 15% (#149) obtient le MEILLEUR résultat des deux (MDD relatif et Sharpe supérieurs à la variante cible 20%, #134) — cohérent avec le résultat déjà documenté dans le backlog non-ML. Rappel important (cf. backlog non-ML, cycle #142) : la décomposition du gain de la diversification obligataire montre que 86-89% de l'amélioration vient du simple PORTAGE (taux positif au lieu de 0% cash pendant les phases dé-risquées), pas principalement d'un effet de couverture actions/obligations authentique ('flight to quality') — à documenter honnêtement si ce résultat est repris dans un rapport exécutif. Rappel Règle 9 (backlog non-ML) : les deux mécanismes (#134 ET #149) atteignent 4/5 sur la batterie renforcée (coûts/crise/stabilité OK) mais échouent SPA et DSR à n_trials=backlog (~150) — PAS un PASS RENFORCÉ au sens strict de cette batterie plus sévère.