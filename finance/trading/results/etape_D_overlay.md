# Étape D — Overlay défensif (vol-targeting GJR-GARCH(1,1)-t) vs Buy & Hold

Contexte : Étape B — aucun signal directionnel ne bat Buy & Hold net de coûts et déflaté. Étape C — GJR-GARCH(1,1)-t est le modèle de volatilité le plus robuste (SPA validé sur l'historique long). Ici on ne prédit aucune direction : on reste essentiellement investi (Buy & Hold) et on pilote l'EXPOSITION via la volatilité prévue.

**Protocole figé** : fenêtre initiale 750 obs, expansive ; coûts 5 bps aller-retour sur le turnover de l'exposition ; cap de levier 1.5× ; coupe extrême au 95e percentile in-sample (fraction résiduelle 0.0) ; univers de 3 variantes (N=3 pour le DSR), figé avant évaluation.

## Composite (5 ans)

- OOS : 11/07/2024 → 10/07/2026 (500 obs, ~2.0 ans), ré-estimation GJR-t tous les 5 j.
- Exposition VolTarget : moy. 1.17×, min 0.46×, max 1.50× (cap 1.5×).
- Coupe extrême déclenchée 16/500 j (3.2%) — exposition moy. VolTarget+Cut 1.15×.

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.78 | +1.03 | +0.62 | -24.3 | +18.9 | 1.15 | 0.836 |
| VolTarget | +0.62 | +0.77 | +0.52 | -23.3 | +14.9 | 1.11 | 0.767 |
| VolTarget+Cut | +0.58 | +0.71 | +0.57 | -19.9 | +13.6 | 1.10 | 0.751 |

- **VolTarget vs BuyHold** : réduction MDD relative = +4.1% (seuil >25%), rendement ann. conservé = 79.0% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget+Cut vs BuyHold** : réduction MDD relative = +18.3% (seuil >25%), rendement ann. conservé = 71.9% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**

## NDX (40 ans)

- OOS : 20/09/1988 → 13/07/2026 (9522 obs, ~37.8 ans), ré-estimation GJR-t tous les 21 j.
- Exposition VolTarget : moy. 1.19×, min 0.23×, max 1.50× (cap 1.5×).
- Coupe extrême déclenchée 616/9522 j (6.5%) — exposition moy. VolTarget+Cut 1.16×.

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.69 | +0.08 | -82.9 | +14.5 | 1.10 | 0.997 |
| VolTarget | +0.66 | +0.94 | +0.12 | -71.7 | +17.1 | 1.11 | 1.000 |
| VolTarget+Cut | +0.66 | +0.90 | +0.15 | -63.3 | +16.4 | 1.12 | 1.000 |

- **VolTarget vs BuyHold** : réduction MDD relative = +13.5% (seuil >25%), rendement ann. conservé = 117.8% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget+Cut vs BuyHold** : réduction MDD relative = +23.7% (seuil >25%), rendement ann. conservé = 112.7% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**

## Verdict — critère de succès explicite

Succès = réduction du MDD >25% (relatif) **et** rendement annualisé conservé ≥80% de Buy & Hold. Vérifié, pas supposé :

| Jeu de données | Variante | ΔMDD relatif | Rdt ann. / BuyHold | Calmar (overlay vs BH) | Critère |
|---|---|---|---|---|---|
| Composite (5 ans) | VolTarget | +4.1% | 79.0% | +0.52 vs +0.62 | NON |
| Composite (5 ans) | VolTarget+Cut | +18.3% | 71.9% | +0.57 vs +0.62 | NON |
| NDX (40 ans) | VolTarget | +13.5% | 117.8% | +0.12 vs +0.08 | NON |
| NDX (40 ans) | VolTarget+Cut | +23.7% | 112.7% | +0.15 vs +0.08 | NON |

**Verdict honnête : le critère de succès N'EST ATTEINT nulle part.** Aucune variante d'overlay ne réduit le MDD de plus de 25% (relatif) tout en conservant ≥80% du rendement annualisé de Buy & Hold, sur aucun des deux jeux de données. L'overlay tel que construit (vol-targeting ± coupe extrême sur GJR-GARCH(1,1)-t) ne remplit pas l'objectif de l'Étape D — ce résultat est rapporté tel quel, sans le présenter comme un succès.