# Simulation — 300 EUR, overlay vol-targeting gaté par la statistique de Ljung-Box glissante (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Fenêtre Q/médiane 252j/252j (Q(maxlag=22)), vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay Ljung-Box gaté** | **353.65 EUR** | **+17.9%** | -9.0% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte est active 45.2% du temps (position moyenne 1.11x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul DAX échoue) et de la robustesse (plateau relativement fragile : grille CAP 3-4/5 avec un seul point à 4/5, grille fenêtre de vol 2-4/5 avec la valeur pré-enregistrée isolée).

**Coïncidence numérique récurrente** : ce résultat (353,65€, MDD -9,0%, Sharpe +2,63) est à nouveau identique aux simulations déjà publiées pour #219, #237 et #240 sur cette même fenêtre. Vérifié : la porte Ljung-Box est elle aussi triviale sur ces 63 séances (active 63/63). C'est désormais un schéma compris (4e occurrence) plutôt qu'une coïncidence isolée : sur cette période calme récente de NDX, la plupart des portes « calme=amplifier » basées sur des statistiques de queue/clustering restent actives en continu, et la position se réduit alors à la seule contrainte de vol réalisée du mécanisme #46 sous-jacent — sans rapport avec le verdict statistique du backtest complet où les portes se différencient nettement.
