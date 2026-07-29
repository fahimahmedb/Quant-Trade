# Pré-enregistrement — Double porte AND : breadth SMA200 ET breadth de momentum

**Committé AVANT tout calcul.** Cycle #98 du backlog non-ML.

## Hypothèse

Combine deux portes de breadth DIFFÉRENTES, chacune individuellement
PASS : breadth SMA200 (#96, fraction des titres au-dessus de leur
propre moyenne mobile 200j) ET breadth de momentum 12-1 mois (#94,
fraction des titres à momentum positif). Teste si combiner deux portes
qui fonctionnent CHACUNE séparément préserve un edge net positif
(comme observé au #81 : dispersion #78 ET tendance #47, toutes deux
PASS individuellement, combinaison PASS) plutôt que de le diluer
(comme observé au #61 : un signal directionnel combiné à un signal
NON-directionnel FAIL dilue l'edge). Ici, contrairement au #81 (deux
signaux de nature différente : dispersion cross-sectionnelle + tendance
indicielle), les deux portes sont de même famille (breadth stock-level)
mais avec des définitions distinctes (niveau vs prix vs signe du
momentum) — teste si la redondance partielle entre deux breadth
diluent la fenêtre active sans gain, ou si la conjonction identifie un
régime encore plus fiable.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #94/#96.
- Breadth SMA200 : IDENTIQUE au #96 (`SMA_WINDOW=200`,
  `BREADTH_THRESHOLD=0.50`).
- Breadth de momentum 12-1 mois : IDENTIQUE au #94 (`LOOKBACK=252,
  SKIP=21`, `BREADTH_THRESHOLD=0.50`).
- Porte combinée active si **breadth SMA200(t) ≥ 0.50 ET breadth de
  momentum(t) ≥ 0.50** SIMULTANÉMENT (AND strict, aucun seuil retouché).
- Échantillon restreint à la période où les DEUX breadth sont
  réellement disponibles (leçon du #77, appliquée dès le départ, comme
  au #81).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte combinée est active, **1.0x** sinon —
  mécanisme identique au #46/#47/#57/#78/#81/#94/#96/#97.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1 (tous les
paramètres repris identiques aux #94/#96, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78/#81/#94/#96.

## Anti-cheat

Ce fichier committé avant
`nonml_sma200_momentum_breadth_and_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py sma200_momentum_breadth_and_overlay`.
