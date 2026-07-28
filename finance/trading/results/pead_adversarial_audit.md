# Audit adversarial — stratégie PEAD

## 1. Recalcul indépendant (event-time, méthode différente du backtest principal)

Méthode event-time (moyenne simple du rendement total sur H=60j par événement, PAS le portefeuille calendar-time du backtest principal) :

- Rendement moyen long (597 événements) : +3.43% sur 60j
- Rendement moyen court (598 événements) : +1.43% sur 60j
- Spread long−court : +2.00% sur 60j

**Cohérence avec le backtest principal (calendar-time)** : le signe du spread doit être positif dans les deux méthodes pour exclure un bug de construction — à comparer manuellement avec `results/pead_backtest_result.md`.

## 2. Fuite mesurée des terciles "pleine période" (vs terciles causaux)

Sur 1762 événements comparables (après 30 événements de warmup), **5.2%** changeraient de panier (long/court/ignoré) si on utilisait des terciles causaux (fenêtre expansive, ne connaissant que le passé) au lieu des terciles pleine-période utilisés dans le backtest principal. C'est une fuite MINEURE, le résultat principal est probablement robuste à ce choix.

## 3. Concentration de l'échantillon

Panier long : 92 tickers distincts sur 597 événements. Top 5 : {'FTNT': 19, 'TTWO': 16, 'DDOG': 16, 'AMZN': 14, 'ABNB': 14} (13.2% du panier).

Panier court : 97 tickers distincts sur 598 événements. Top 5 : {'ROP': 15, 'MPWR': 14, 'PAYX': 14, 'LIN': 12, 'ORLY': 12} (11.2% du panier).

Concentration jugée acceptable (aucun groupe de 5 titres ne domine >30% d'un panier).
