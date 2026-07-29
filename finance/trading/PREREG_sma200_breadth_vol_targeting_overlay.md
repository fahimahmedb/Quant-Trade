# Pré-enregistrement — Overlay vol-targeting gaté par la breadth SMA200

**Committé AVANT tout calcul.** Cycle #96 du backlog non-ML.

## Hypothèse

Indicateur classique de largeur de marché en analyse technique : la
fraction de titres cotant AU-DESSUS de leur propre moyenne mobile 200j
(SMA200). Distinct de la breadth de NIVEAU EXTRÊME (#77 : proximité au
plus haut, #89 : proximité au plus bas — bornes de l'historique 252j)
et de la breadth de momentum 12-1 mois (#94 : signe d'un rendement
cumulé décalé) : la breadth SMA200 mesure la largeur de la TENDANCE DE
MOYEN TERME titre par titre, avec le même filtre que celui validé au
niveau indice dans ce backlog (#29, SMA200, PASS 5/5, meilleur résultat
initial du backlog). Une large majorité de titres au-dessus de leur
propre SMA200 signale une tendance haussière large et structurelle,
motivant une amplification via le mécanisme hiérarchique déjà validé
sur 5 autres types de porte (tendance #47, calendrier #54, breadth de
niveau #57, dispersion #78, breadth de momentum #94).

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #77/#78/#89/#94.
- SMA200 par titre : moyenne mobile simple 200j du prix de clôture,
  calcul causal (identique au #29 mais appliqué titre par titre).
- Breadth SMA200(t) = fraction des titres COTÉS ce jour-là avec SMA200
  calculable (historique ≥200j) dont `close(t) > SMA200(t)`
  (dénominateur = titres cotés avec SMA200 calculable, même convention
  que #77/#78/#89/#94).
- Porte active si Breadth SMA200(t) ≥ `BREADTH_THRESHOLD=0.50` (majorité
  du panier au-dessus de sa propre SMA200 — même seuil que le
  #77/#89/#94, aucun retuning).
- Échantillon restreint à la période où la breadth est réellement
  disponible (leçon du #77, appliquée dès le départ).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90/#94.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1 (tous les
paramètres repris identiques au #29/#46/#47/#57/#77/#89/#90/#94, aucune
grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78/#94.

## Anti-cheat

Ce fichier committé avant
`nonml_sma200_breadth_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
sma200_breadth_vol_targeting_overlay`.
