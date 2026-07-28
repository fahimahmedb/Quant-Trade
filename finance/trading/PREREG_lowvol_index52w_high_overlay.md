# Pré-enregistrement — Low-Volatility Tilt + overlay levé proximité plus haut 52-semaines (indice)

**Committé AVANT tout calcul.** Cycle #39 du backlog non-ML. Variante du
cycle #35 (Low-Vol + overlay SMA200, PASS, MDD quasi inchangé) : même
portefeuille de base (#15), mais avec le signal de tendance du cycle
#37 (proximité au plus haut 52-semaines de l'INDICE NDX-100), qui a
montré au #38 (combiné à Leaders) un résultat exceptionnel avec un MDD
quasi inchangé.

## Hypothèse

Le signal "proximité du plus haut 52-semaines" a déjà surperformé SMA200
en combinaison avec le portefeuille momentum (#38 vs #33) tout en
préservant mieux le MDD — teste ici s'il produit le même bénéfice
supplémentaire sur le portefeuille défensif low-vol (#39 vs #35).

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Low-Volatility Tilt, IDENTIQUE au cycle #15
  (tercile inférieur de volatilité réalisée 60j, rebalancement 21j,
  univers NDX-100 dynamique).
- Signal de tendance = indice NDX-100 (`data/nasdaq100_daily.txt`) dont
  la clôture est **≥ 95%** de son plus haut glissant sur 252 séances
  (paramètres identiques au #37/#38), appliqué comme régime GLOBAL au
  portefeuille (alignement causal par ffill, même méthode qu'au #35/#38).
- Overlay = position de base **× CAP=2.0x** durant les jours où le
  signal est actif, position de base ×1.0 sinon.
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Low-Vol 1.0x (cycle #15), PAS Buy&Hold —
  même convention que #11/#23/#28/#33/#35/#38.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Low-Vol de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x, fenêtre 252j et seuil 95% cohérents
avec le #37/#38, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_lowvol_index52w_high_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py lowvol_index52w_high_overlay`.
