# Pré-enregistrement — Low-Volatility Tilt + overlay levé union ToM∪Halloween

**Committé AVANT tout calcul.** Cycle #28 du backlog non-ML. Teste si
l'overlay union ToM∪Halloween (#21, PASS sur Buy&Hold ; #23, PASS sur
Leaders) aide aussi un portefeuille défensif construit sur la
volatilité (#15, low-vol tilt, FAIL en stock-picking pur mais MDD
nettement meilleur) — question ouverte car les combinaisons testées
jusqu'ici (#11, #23 avec Leaders) portaient toutes sur un portefeuille
momentum, jamais sur un portefeuille low-vol.

## Hypothèse

Le portefeuille low-vol (#15) sacrifie du rendement pour un bien
meilleur MDD ; un overlay calendaire qui ajoute de l'exposition
temporaire pendant les fenêtres statistiquement favorables (ToM∪Halloween)
pourrait combler une partie de l'écart de rendement sans sacrifier
l'avantage de MDD du low-vol de base.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Low-Volatility Tilt, IDENTIQUE au cycle #15
  (tercile inférieur de volatilité réalisée 60j, rebalancement 21j,
  univers NDX-100 dynamique).
- Overlay = position de base **× CAP=2.0x** durant les jours où la
  fenêtre ToM **OU** Halloween est active (union, définitions identiques
  aux cycles #8/#17/#21/#23), position de base ×1.0 sinon.
- **Coûts** : 5 bps par unité de turnover (rebalancement ET
  changements de l'overlay).
- **Référence** : portefeuille Low-Vol 1.0x (cycle #15), PAS Buy&Hold —
  même convention que #11/#16/#18/#20/#23.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), univers dynamique
(union des dates de cotation, cf. cycle #4).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Low-Vol de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant
`nonml_lowvol_tom_halloween_union_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py lowvol_tom_halloween_union_overlay`.
