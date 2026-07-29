# Pré-enregistrement — Overlay vol-targeting gaté par la breadth de FAIBLESSE

**Committé AVANT tout calcul.** Cycle #89 du backlog non-ML. Pôle
opposé du #77 (breadth INTERNE de force, majorité des titres proches de
leur haut) : ici on mesure la breadth de FAIBLESSE (fraction des titres
NDX-100 proches de leur propre plus bas 52-semaines), distincte de la
dispersion cross-sectionnelle du #78 (qui mesure l'amplitude des écarts
de rendement DU JOUR, pas un comptage de titres proches d'un extrême).

## Hypothèse

Un pic de "capitulation" — une large fraction des titres du panier
simultanément proches de leur plus bas annuel — pourrait signaler un
point bas de marché (washout), motivant une exposition accrue plutôt
qu'une réduction, contrairement aux chocs de prix ponctuels déjà testés
(#13/#22/#24, tous FAIL, qui mesuraient un rebond après une baisse
BRUTALE mais localisée, pas une breadth de faiblesse généralisée).
Le mécanisme testé applique le même vol-targeting hiérarchique déjà
validé sur 7 autres types de porte (tendance #47/#68, calendrier
#54/#72, breadth de force #57, dispersion #78, annuelle #80,
double-AND #81), mais gaté par cette nouvelle porte de FAIBLESSE
généralisée.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #77/#78.
- Un titre est "proche de son plus bas" au jour t si
  `close(t) <= 1.05 × min_glissant_252j(t)` (symétrique du seuil ≥95%
  du #37/#77 pour la proximité au plus haut), nécessite un historique
  complet de 252j (comme #77).
- Breadth de faiblesse(t) = fraction des titres COTÉS ce jour-là
  proches de leur plus bas (dénominateur = titres cotés, identique à la
  correction de bug du #77).
- Porte active si Breadth de faiblesse(t) ≥ `BREADTH_THRESHOLD=0.50`
  (majorité du panier proche de son plus bas — même seuil que le #77,
  aucun retuning, juste appliqué à la breadth opposée).
- Échantillon restreint à la période où la breadth est réellement
  disponible (leçon du #77, appliquée dès le départ comme aux #78/#81) :
  `start = max(first_valid, INDEX_LOOKBACK=252, VOL_WINDOW=20)`.
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`),
  identique au #77/#78.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1 (tous les
paramètres repris identiques au #46/#47/#57/#77/#78, seul le seuil de
proximité au plus bas — 1.05 au lieu de 0.95, symétrie géométrique
directe — est nouveau et fixé ici, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78.

## Anti-cheat

Ce fichier committé avant
`nonml_weakness_breadth_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
weakness_breadth_vol_targeting_overlay`.
