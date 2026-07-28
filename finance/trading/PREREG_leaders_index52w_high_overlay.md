# Pré-enregistrement — Leaders 52-semaines + overlay levé proximité plus haut 52-semaines (indice)

**Committé AVANT tout calcul.** Cycle #38 du backlog non-ML. Variante du
cycle #33 (Leaders + overlay SMA200, PASS, meilleur ratio gain/MDD à ce
stade) : même portefeuille de base (#4), mais avec le signal de tendance
du cycle #37 (proximité au plus haut 52-semaines de l'INDICE NDX-100),
qui a montré une meilleure préservation du MDD que SMA200 en solo.

## Hypothèse

Le signal "proximité du plus haut 52-semaines" coupe le levier plus tôt
qu'une simple comparaison à la SMA200 (dès -5% du sommet, sans attendre
un croisement de moyenne) — appliqué au portefeuille Leaders, il
pourrait offrir un ratio gain/MDD encore meilleur que le #33.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Leaders 52-semaines, IDENTIQUE au cycle #4.
- Signal de tendance = indice NDX-100 (`data/nasdaq100_daily.txt`) dont
  la clôture est **≥ 95%** de son plus haut glissant sur 252 séances
  (paramètres identiques au #37 : fenêtre 252j, seuil 95%), appliqué
  comme régime GLOBAL au portefeuille (alignement causal par ffill,
  même méthode qu'au #33).
- Overlay = position de base **× CAP=2.0x** durant les jours où le
  signal est actif, position de base ×1.0 sinon.
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Leaders 1.0x (cycle #4), PAS Buy&Hold —
  même convention que #11/#23/#33/#35.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Leaders de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x, fenêtre 252j et seuil 95% cohérents
avec le #37, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_leaders_index52w_high_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py leaders_index52w_high_overlay`.
