# Pré-enregistrement — Cycle #162 : ré-exécution du #38 sur historique étendu

**Committé AVANT tout calcul (et avant le fetch réseau).** Cycle #162 du
backlog non-ML, motivé directement par le #161.

## Contexte

Le #161 (batterie Règle 9 sur le #38, `PREREG_leaders_index52w_high_overlay_pass_validation_battery.md`)
a obtenu le meilleur score jamais atteint (4/5, SPA p=0,0000, DSR=0,730)
sur un échantillon utilisable de ~4,5 ans (2022-01-03 → 2026-07-27),
lui-même limité par une borne ARTIFICIELLE (`PRICE_PERIOD1 = 2021-01-01`
dans `pead_fetch_data.py`, choisie pour l'ancien protocole PEAD, pas une
limite de la source Yahoo Finance elle-même).

## Hypothèse (fixée ici, avant tout résultat)

Un historique plus long (jusqu'à l'IPO de chaque titre pour les données
disponibles via Yahoo, vérifié par smoke-test : AAPL remonte à 1980)
réduit l'incertitude d'estimation du Sharpe, ce qui **devrait** rapprocher
le DSR de son seuil si l'edge du #38 est réel et pas un artefact de la
fenêtre 2022-2026. **Cette hypothèse peut être RÉFUTÉE** : si le DSR se
dégrade ou reste stable, cela indiquerait que 2022-2026 était une fenêtre
favorable par chance plutôt qu'un edge robuste sur longue période — un
résultat honnête et informatif dans les deux cas.

## Définition (fixée ici)

- **Aucun paramètre du #38 ne change** : même TERCILE (1/3), même
  LOOKBACK (252j), même REBAL_EVERY (21j), même CAP (2.0x), même
  INDEX_LOOKBACK/THRESHOLD (252j/95%), mêmes coûts (5 bps). Seul
  l'historique de prix change.
- Nouvelle source de prix : `data/pead/prices_extended/*.json`, mêmes
  ~103 tickers NDX-100, récupérés via `fetch_ndx100_extended_history.py`
  (Yahoo Finance chart API, period1=0 = tout l'historique disponible).
  Fichier **séparé** de `data/pead/prices/` (jamais modifié — Règle 6).
- Signal de tendance indice : `data/nasdaq100_daily.txt` (déjà 1985-2026,
  inchangé).
- Le portefeuille ne peut détenir que les titres ayant un historique
  suffisant à chaque date de rebalancement (comme dans le #38 original,
  `elig = np.where(np.isfinite(r))[0]` — aucun changement de cette
  logique). Les titres plus jeunes (IPO récente, ex. ABNB 2020) entrent
  naturellement dans l'univers dès qu'ils ont assez d'historique, exactement
  comme dans le mécanisme déjà validé.

## Critère de succès (identique au #161, Règle 9, n_trials=1 pour CE cycle)

Ré-exécuter EXACTEMENT la même batterie Règle 9 (5 contrôles a-e) sur le
nouvel historique. Rapporté tel quel, PASS RENFORCÉ ou non — aucun
retuning si le résultat déçoit, aucune deuxième tentative avec des
paramètres différents.

## Anti-cheat

Ce fichier committé avant le lancement du fetch réseau
(`fetch_ndx100_extended_history.py`, tâche de fond) et avant tout calcul.
Script de backtest : nouvelle variante paramétrée par le dossier de prix
(réutilise `build_weights()` déjà committé, Règle 7).
