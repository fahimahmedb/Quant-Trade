# Pré-enregistrement — Overlay vol-targeting gaté par la breadth NETTE (hauts − bas)

**Committé AVANT tout calcul.** Cycle #97 du backlog non-ML. Dernière
hypothèse en file avant renouvellement du backlog.

## Hypothèse

Combine les deux pôles de breadth de NIVEAU déjà testés séparément :
force (#77, majorité proche du plus haut 52-semaines, FAIL) et
faiblesse (#89, majorité proche du plus bas 52-semaines, PASS
techniquement mais NON INFORMATIF — porte quasi jamais active). Ce
cycle teste si la version NETTE (nombre de titres proches de leur plus
haut MOINS nombre de titres proches de leur plus bas, rapporté au
nombre de titres cotés) porte davantage d'information qu'un seuil de
majorité absolue sur chaque pôle isolément — analogue à l'indicateur
classique "nouveaux plus hauts moins nouveaux plus bas" utilisé en
analyse technique de largeur de marché.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #77/#78/#89/#94/#96.
- Proximité au plus haut : `close(t) ≥ 0.95 × max_glissant_252j(t)`
  (IDENTIQUE au #37/#77, historique complet 252j requis).
- Proximité au plus bas : `close(t) ≤ 1.05 × min_glissant_252j(t)`
  (IDENTIQUE au #89, historique complet 252j requis).
- Breadth nette(t) = `(n_proche_haut(t) − n_proche_bas(t)) / n_cotés(t)`
  (dénominateur = titres cotés ce jour-là, même convention que
  #77/#78/#89/#94/#96).
- Porte active si Breadth nette(t) **> 0** (STRICTEMENT plus de titres
  proches de leur haut que de leur bas — seuil naturel de zéro, PAS un
  seuil de majorité absolue arbitraire comme le 50% du #77/#89, choisi
  ici a priori car c'est le seul seuil non-arbitraire pour une
  différence signée).
- Échantillon restreint à la période où la breadth est réellement
  disponible (leçon du #77, appliquée dès le départ).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90/#94/#96.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1 (seuils de
proximité 0.95/1.05 repris identiques au #37/#77/#89, seuil de porte
fixé au zéro naturel de la différence signée, aucune grille testée
avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78/#94/#96.

## Anti-cheat

Ce fichier committé avant
`nonml_net_breadth_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py net_breadth_vol_targeting_overlay`.
