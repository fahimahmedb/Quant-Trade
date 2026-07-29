# Étape D — Overlay défensif (vol-targeting GJR-GARCH(1,1)-t) vs Buy & Hold

Contexte : Étape B — aucun signal directionnel ne bat Buy & Hold net de coûts et déflaté. Étape C — GJR-GARCH(1,1)-t est le modèle de volatilité le plus robuste (SPA validé sur l'historique long). Ici on ne prédit aucune direction : on reste essentiellement investi (Buy & Hold) et on pilote l'EXPOSITION via la volatilité prévue.

**Protocole figé** : fenêtre initiale 750 obs, expansive ; coûts 5 bps aller-retour sur le turnover de l'exposition ; cap de levier 1.5× ; coupe extrême au 95e percentile in-sample (fraction résiduelle 0.0) ; univers de 3 variantes (N=3 pour le DSR), figé avant évaluation.

## Composite (5 ans)

- OOS : 11/07/2024 → 10/07/2026 (500 obs, ~2.0 ans), ré-estimation GJR-t tous les 5 j.
- Exposition VolTarget : moy. 1.17×, min 0.46×, max 1.50× (cap 1.5×).
- Coupe extrême déclenchée 16/500 j (3.2%) — exposition moy. VolTarget+Cut 1.15×.

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.78 | +1.03 | +0.62 | -24.3 | +18.9 | 1.15 | 0.832 |
| VolTarget | +0.59 | +0.74 | +0.50 | -23.5 | +14.3 | 1.11 | 0.752 |
| VolTarget+Cut | +0.56 | +0.68 | +0.55 | -20.1 | +13.1 | 1.10 | 0.737 |

- **VolTarget vs BuyHold** : réduction MDD relative = +3.2% (seuil >25%), rendement ann. conservé = 75.7% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget+Cut vs BuyHold** : réduction MDD relative = +17.4% (seuil >25%), rendement ann. conservé = 69.1% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**

## NDX (40 ans)

- OOS : 20/09/1988 → 13/07/2026 (9522 obs, ~37.8 ans), ré-estimation GJR-t tous les 21 j.
- Exposition VolTarget : moy. 1.16×, min 0.21×, max 1.50× (cap 1.5×).
- Coupe extrême déclenchée 616/9522 j (6.5%) — exposition moy. VolTarget+Cut 1.13×.

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.69 | +0.08 | -82.9 | +14.5 | 1.10 | 0.997 |
| VolTarget | +0.69 | +0.98 | +0.15 | -66.4 | +17.1 | 1.12 | 1.000 |
| VolTarget+Cut | +0.67 | +0.92 | +0.18 | -57.2 | +16.1 | 1.12 | 1.000 |

- **VolTarget vs BuyHold** : réduction MDD relative = +19.9% (seuil >25%), rendement ann. conservé = 118.0% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget+Cut vs BuyHold** : réduction MDD relative = +31.0% (seuil >25%), rendement ann. conservé = 111.2% du BuyHold (seuil ≥80%) → **critère de succès atteint**

## Verdict — critère de succès explicite

Succès = réduction du MDD >25% (relatif) **et** rendement annualisé conservé ≥80% de Buy & Hold. Vérifié, pas supposé :

| Jeu de données | Variante | ΔMDD relatif | Rdt ann. / BuyHold | Calmar (overlay vs BH) | Critère |
|---|---|---|---|---|---|
| Composite (5 ans) | VolTarget | +3.2% | 75.7% | +0.50 vs +0.62 | NON |
| Composite (5 ans) | VolTarget+Cut | +17.4% | 69.1% | +0.55 vs +0.62 | NON |
| NDX (40 ans) | VolTarget | +19.9% | 118.0% | +0.15 vs +0.08 | NON |
| NDX (40 ans) | VolTarget+Cut | +31.0% | 111.2% | +0.18 vs +0.08 | OUI |

**Verdict honnête** : le critère de succès est atteint pour au moins une combinaison jeu de données/variante ci-dessus (détail dans le tableau) — l'overlay apporte un bénéfice matériel de réduction du drawdown dans ce(s) cas, sans sacrifier l'essentiel du rendement. Il ne l'est PAS partout : ne pas généraliser au-delà de ce qui est montré dans le tableau.