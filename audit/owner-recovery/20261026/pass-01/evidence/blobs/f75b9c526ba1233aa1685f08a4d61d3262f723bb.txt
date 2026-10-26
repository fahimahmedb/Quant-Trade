# ARRÊTÉ (STOP_OWNER) — unifié dans claude/new-session-0ydmkg

Essais consommés par ce builder : **14** (tous sur `claude/new-session-3ujgeu`, registre `research/fast_rail/registry.jsonl`).
| H-id | verdict | essais | travail |
|---|---|---|---|
| H-001 Pinnacle vs sport PM | BLOCKED(data) ici | 0 | registre seulement |
| H-002 HL vs dYdX funding (hystérésis) | REJECT (val t −0,03 < 3,29) | 6 (+44 prior) | fusionné ; origine `claude/new-session-3ujgeu-wip-h002` @1903aed ; `scripts/build_hl_dydx_funding_dataset.py`, `research/fast_rail/run_h002.py`, `h002_result.json`, `tests/test_fast_rail_h002.py` |
| H-004 Kalshi météo, P&L maker | REJECT (t 1,34 / 0,86 < 2,24 ; concentration) | 2 | fusionné ; origine `-wip-h004` @fd1d2e1 ; `src/quant/factory/kalshi_maker.py`, `scripts/{build_kalshi_weather_trades,evaluate_h004}.py`, `data/fast_rail/kalshi_weather_trades.*`, `h004_result.json` |
| H-006 fade listings HL | REJECT (val t 1,82 < 2,64) | 6 | fusionné ; origine `-wip-h006` @bc9974d ; `scripts/{build_hl_listings_dataset,evaluate_h006}.py`, `h006_result.json`, `tests/test_fast_rail_h006.py` |
Note : les numéros H-00x de ce registre ne correspondent pas à ceux de 0ydmkg (renuméroter à l'unification). Descriptif non compté (H-004) : KXBTCD maker +2,77 ¢/contrat, t 4,02 sur 12 événements — idée à pré-enregistrer.
Dernière vérif. complète : 470 tests OK avant la fusion H-004 ; après fusion H-004, suite complète non relancée (arrêt propriétaire) — `status_artifacts --write` OK, 485 tests découverts. `kalshi_weather_trades` déplacé de `data/datasets/` vers `data/fast_rail/` (ce n'est pas un PricePanel : cassait `register_committed_snapshots`).

---

# Fast Rail State — itération 1 (en cours) — 2026-09-27

## REPRISE (lire en premier après une coupure)
- Branche : `claude/new-session-3ujgeu` (= rail rapide ; base prototype + adoption Blue bd19712 vérifiée).
- Étape en cours : **it.1, étape B** (vague parallèle). Les 4 agents de la vague 1 (H-002, H-004, H-006, Données) ont été tués par la limite de session le 2026-09-25 **avant tout commit** : aucun essai consommé, rien à récupérer.
- H-006 et H-002 terminés et fusionnés (REJECT tous deux). H-004 lancé en remplacement (WIP `-wip-h004`).
- Vague 1 relancée le 2026-09-27 02:22Z avec 2 agents (H-006, H-002). WIP poussé sur `claude/new-session-3ujgeu-wip-h006` / `-wip-h002` (+ `research/fast_rail/wip_h00x.md` = prochaine étape exacte). Après coupure : fetch ces branches, reprendre depuis leur wip_*.md, puis étape C (red team) et D.
- Watchdog : routine horaire (xx:27 UTC) « Fast rail hourly resume » ; la supprimer quand le rail s'arrête (§9).
- Registre : `research/fast_rail/registry.jsonl` (déclarations H-001..H-006 faites avant données).

## Budget : itérations 1/10, essais 12/200 consommés (14 déclarés : H-002 6, H-004 2, H-006 6)

## En SHADOW
| stratégie | depuis | forward | note |
|---|---|---|---|
| calendar_fomc_overnight (SPY MOC→MOO) | pristine_after 2026-09-11 | 1 événement (2026-09-16, +0,26 %) | laisser accumuler ; ne pas re-tester |

## Verdicts de cette itération
| H-id | niveau | motif |
|---|---|---|
| H-001 Pinnacle vs PM/Kalshi sport | BLOCKED(data) | secret `ODDS_API_KEY` absent du relais |
| H-002 HL vs dYdX funding (hystérésis) | REJECT(signal+coûts) | validation SR −0,03, t −0,03 < 3,29 (50 essais), brut 0,08 % < coûts, 70 jours actifs ; 5 coins seulement |
| H-004 Kalshi météo, P&L maker à règlement | IDEA | agent interrompu, 0 essai |
| H-006 fade des listings HL | REJECT(signal) | meilleure : n30 couverte BTC ; validation SR 1,52, t 1,82 < 2,64 (6 essais), β −0,06, 42 listings, +18 %/événement ; discovery portée par peu d'événements. Fenêtre de validation épuisée : seul le forward (30 listings) peut rouvrir |

## Constats red team : ouverts HIGH 0 | reportés : aucun (pas encore de résultat)

## Faits d'environnement (vérifiés 2026-09-25)
- Réseau sortant ouvert depuis le sandbox : Hyperliquid (POST info), dYdX indexer, OKX, Polymarket, FRED, Kalshi (429 si trop rapide). EDGAR efts : 403. → l'historique se récupère directement, le relais sert au forward.

## Backlog (suivants, classés)
1. H-006 fade listings HL (léger, données accessibles)
2. H-002 HL vs dYdX funding (moyen)
3. H-004 Kalshi météo maker (mesure)
4. Kalshi macro CPI/NFP vs nowcasts (consensus PIT à vérifier)
5. SPAC trust arb (EDGAR hors `sec/`, efts 403 → tester www.sec.gov)
BLOCKED : H-001 (ODDS_API_KEY).

## Actions propriétaire en attente
- Ajouter `ODDS_API_KEY` en **secret GitHub Actions** du repo (relais) et, si besoin en sandbox, en variable d'environnement de l'environnement Claude Code. Ne jamais la coller dans le chat ni dans un fichier commité.

## Leçon de l'itération
4 agents Opus en parallèle ont épuisé la limite de session en < 1 h et les worktrees non commités ont été perdus. Désormais : ≤ 2 agents, push WIP fréquent, checkpoint d'état avant chaque vague.
