# Quantification — cash-and-carry funding rate crypto (données réelles OKX)

Données publiques OKX (`funding-rate-history`), pas les chiffres marketing trouvés en ligne. P&L approximé = funding rate collecté (long spot / short perpétuel, delta ~0) — hors frais d'emprunt spot et slippage d'entrée/sortie (limite assumée, signalée).

| Symbole | N périodes | Historique | Funding moy./période | Rendement ann. | Vol ann. | Sharpe ann. | % périodes négatives |
|---|---|---|---|---|---|---|---|
| BTC-USDT-SWAP | 273 | 2026-04-28 → 2026-07-28 | 0.0027% | 2.9% | 0.1% | +19.98 | 26.0% |
| ETH-USDT-SWAP | 273 | 2026-04-28 → 2026-07-28 | 0.0024% | 2.6% | 0.2% | +16.12 | 29.3% |

## Limite critique du Sharpe affiché ci-dessus — NE PAS le prendre au pied de la lettre

Deux problèmes qui font que le Sharpe annualisé ci-dessus est probablement **très surestimé** :

1. **Fenêtre courte** : l'endpoint public OKX ne conserve que ~90 jours d'historique de funding réglé (aucune option pour remonter plus loin sans source payante) — 3 mois est bien trop court pour juger d'un edge annualisé, surtout sur un actif dont le régime de funding change fortement d'un cycle à l'autre (funding négatif 20-25% du temps en 2022-2023 selon des sources indépendantes, contre 26-29% ici sur une fenêtre récente différente).

2. **La volatilité mesurée ici n'est PAS la vraie volatilité de la position couverte** : ce calcul utilise seulement la variance du taux de funding lui-même, qui est mécaniquement très lisse. La vraie position (long spot / short perpétuel) a une volatilité de P&L bien plus élevée en pratique à cause du risque de base (l'écart spot-perp peut bouger de 300-500 bps en quelques secondes lors d'un choc de marché) et du slippage d'exécution — aucun des deux n'est capturé ici. Un Sharpe annualisé proche de +20 est un signal que la mesure est incomplète, pas que la stratégie est extraordinaire (cf. avertissement général du projet : un Sharpe >3 doit éveiller la suspicion d'une erreur de méthode, pas d'une découverte).

## Comparaison honnête avec Étape C (volatilité GJR-t, validée SPA)

Étape C n'est PAS une stratégie de rendement — c'est un edge de PRÉVISION (la volatilité future réalisée), validé statistiquement sur 9522 observations OOS avec un test SPA rigoureux (p=0,0000), cross-marché. Le funding rate arbitrage ci-dessus n'a PAS encore ce niveau de preuve : seulement ~90 jours de données, une mesure de volatilité incomplète, et aucune validation cross-marché (un seul cycle de marché crypto observé). Le rendement moyen collecté (2,6-2,9% annualisé sur cette fenêtre) est plausible et cohérent avec la littérature indépendante (10-30%/an selon le cycle), mais ce chantier n'est PAS encore au même niveau de rigueur qu'Étape C — il faudrait soit une source de données payante avec plus d'historique, soit reconstruire le P&L réel (spot + perp + frais), avant de considérer ce résultat comme validé.

**Limites non modélisées ici, à ne pas ignorer avant tout capital réel** : frais d'emprunt/staking du spot, slippage d'entrée/sortie, risque de contrepartie de l'exchange (ex. FTX 2022), risque de base spot-perp en cas de mouvement violent (300-500 bps en quelques secondes lors de chocs de marché), et funding qui peut rester négatif pendant de longues périodes (20-25% du temps en 2022-2023 selon les données historiques BTC).
