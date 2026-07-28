# Pré-enregistrement — Leaders 52-semaines + overlay levé filtre de tendance SMA200

**Committé AVANT tout calcul.** Cycle #33 du backlog non-ML. Combine le
meilleur résultat individuel du backlog (#29, SMA200, PASS 5/5) avec le
portefeuille momentum déjà validé (#4, PASS) — même esprit que #11/#23
(combinaisons Leaders + overlay), signal de tendance calculé sur
l'INDICE NDX-100 lui-même (pas sur chaque titre), appliqué comme
multiplicateur d'exposition globale au portefeuille Leaders.

## Hypothèse

Le filtre de tendance SMA200 capture un régime de marché favorable au
niveau indice ; appliqué comme levier au portefeuille Leaders (déjà
sélectionné sur le momentum individuel des titres), il pourrait combiner
un edge de sélection (stock-picking) et un edge de timing (régime de
marché), potentiellement plus robuste que #11/#23 (qui combinaient
Leaders avec des signaux calendaires).

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Leaders 52-semaines, IDENTIQUE au cycle #4.
- Signal de tendance = indice NDX-100 (`data/nasdaq100_daily.txt`) au-
  dessus de sa SMA200 (identique au #29), appliqué comme régime GLOBAL
  au portefeuille (pas par titre).
- Overlay = position de base **× CAP=2.0x** durant les jours où l'indice
  NDX-100 est au-dessus de sa SMA200, position de base ×1.0 sinon.
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Leaders 1.0x (cycle #4), PAS Buy&Hold —
  même convention que #11/#16/#18/#20/#23.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Leaders de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant `nonml_sma200_leaders_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py sma200_leaders_overlay`.
