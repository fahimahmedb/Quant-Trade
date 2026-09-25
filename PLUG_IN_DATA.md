# Brancher les données externes

Ce document décrit la couche de données du prototype : connecteurs, relais GitHub Actions et ingestion forward. Tout est paper/shadow, sans aucune autorité sur du capital réel.

## 1. Architecture

```text
API publiques ──> scripts/fetch_feeds.py ──> data/feeds/*.jsonl (append-only, dédupliqués)
   (sur un runner GitHub Actions : internet ouvert)       │  commit sur la branche claude/data-feeds-6vr22g
                                                          ▼
Quant (sandbox) ── git fetch ──> quant.py sync-feeds ──> datasets (séances ajoutées après la dernière date)
                                                          ▼
                    quant.py run --market {etf, calendar, perp-funding, futures, futures-broad}
```

- Le sandbox n'a pas d'accès internet général. Les runners GitHub en ont un. **Git sert de canal de données.**
- `sync-feeds` **ajoute uniquement** des séances après la dernière date d'un dataset. L'historique des cohortes figées n'est jamais réécrit. Les séances ajoutées sont postérieures à la date `pristine_after` : ce sont les seules données qui peuvent faire bouger le cycle de vie des stratégies.

## 2. Connecteurs (`src/quant/dataplane/connectors.py`)

Statuts vérifiés en réel par le workflow le 2026-09-25 :

| Connecteur | Données | CGU | Statut réel |
|---|---|---|---|
| `yahoo_chart` | Barres quotidiennes ETF et proxys de futures continus (`ES=F`…) | **grise** : JSON public non documenté, usage personnel | OK. 156 barres recoupées avec le repo : 0 écart de clôture |
| `stooq` | CSV quotidien | grise | Vide (le service demande désormais une clé) |
| `fred` | Taux : DGS3MO (seuil de rendement minimum), DGS2, DGS10 | documentée | OK |
| `fomc_calendar` | Dates de décision des réunions programmées | documentée (page de la Fed) | OK : correspond exactement à `data/calendars/fomc_scheduled.csv` sur 2021-2026 ; ajoute 2027 |
| `hyperliquid` | Univers, prix mark, volumes, funding horaire | documentée | OK |
| `bybit`, `binance_futures` | Funding | documentée | **Bloqués depuis les US** (403/451) : à faire tourner depuis l'UE, ou utiliser OKX/dYdX |
| `okx`, `dydx` | Funding | documentée | Ajoutés, statut à confirmer au prochain run |
| `polymarket` | Marchés (règles de résolution incluses) et carnets CLOB | documentée | OK |
| `kalshi` | Marchés (règles incluses), prix | documentée | OK (1 000 marchés par run) |
| `odds_api` | Cotes h2h, Pinnacle compris | clé requise | Voir §4 |

**Hors périmètre, volontairement** :
- scraping derrière un login ;
- rotation d'identités ou d'adresses IP ;
- contournement de limites de débit ;
- extraction de clés d'API embarquées dans un site (par exemple l'API « guest » de Pinnacle).

## 3. Ce qui est déjà branché et tourne

| Instance | Dataset | Mise à jour forward | Démontré |
|---|---|---|---|
| `calendar` : veille de FOMC, fin de mois | `us_calendar_legs_daily`, dérivé de l'ETF | Oui (Yahoo, puis dérivation) | **Premier trade papier sur donnée nouvelle** : jambe overnight SPY, MOC du 2026-09-15 → MOO du 2026-09-16 (jour de FOMC), +0,26 % |
| `etf` | `us_sector_etf_daily` | Oui (Yahoo, ajustement re-chaîné à la jointure) | 72 barres (2026-09-14 → 09-21) ajoutées sur une copie |
| `perp-funding` | `perp_funding_pairs_daily` (HL vs BY, 2023-06 → 2025-05) | Hyperliquid oui. Bybit uniquement si le collecteur tourne hors US | Accrual du funding vérifié : +481 $ encaissés en shadow |
| `futures`, `futures-broad` | pysystemtrade (jusqu'en 2024-03) | Non : il faut une source de futures back-adjustés (voir §4) | — |

## 4. Ce qu'il te reste à faire, par ordre de priorité

1. **Activer le planning** : fusionner `.github/workflows/data-feeds.yml` sur la branche par défaut. GitHub ne déclenche les `schedule` que depuis la branche par défaut. D'ici là, tout push sur `claude/data-feeds-*` déclenche une collecte.
2. **Clé The Odds API** (offre gratuite ou payante) : l'ajouter en secret `ODDS_API_KEY` dans les réglages du repo. Cela active la lane « cote sharp vs marchés de prédiction sport ».
3. **Funding de Bybit ou Binance** : faire tourner `python3 scripts/fetch_feeds.py collect` depuis une machine UE, ou un runner self-hosted, puis committer `data/feeds`. Sinon, déclarer une nouvelle lane HL-vs-OKX sur données forward, puisque la lane actuelle est HL-vs-BY.
4. **Futures forward** : les continus Yahoo (`ES=F`…) ont des trous au roll et ne remplacent pas le back-adjusted. Options : Norgate, CSI Data, Databento (payants).
5. **Mise à jour quotidienne dans le sandbox** :
   ```bash
   PYTHONPATH=src python3 scripts/quant.py sync-feeds        # git fetch de la branche de données + ajout
   PYTHONPATH=src python3 scripts/quant.py run --market calendar
   PYTHONPATH=src python3 scripts/status_artifacts.py --write   # si le dataset ETF a changé
   ```

## 5. Garanties et limites

- **Point-in-time** :
  - une barre du jour n'est enregistrée qu'après la clôture US (plus une marge) ;
  - la première observation d'une valeur est conservée, et une valeur révisée est ajoutée comme `restatement` sans jamais l'écraser ;
  - l'ajout forward utilise la dernière base d'ajustement, rebasée à la jointure pour préserver exactement les rendements.
- **Aucun trou comblé** : une séance incomplète pour l'un des symboles attendus arrête l'ajout, et une jointure absente n'ajoute rien.
- Le calendrier FOMC du repo est recoupé avec la page de la Fed à chaque synchronisation. En cas de contradiction, l'ajout est refusé.
- Capacité : le volume est modélisé pour ETF et perps, mais pas pour les futures pysystemtrade.
- Une capture forward existe sur `parallel/claude-forward-data-2026-09-20` (registre de couverture, admissibilité). **Il faut fusionner les deux approches**, pas en maintenir deux.
