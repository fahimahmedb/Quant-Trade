# Fast Rail State — itération 1 (vague 1 : 4/5 tranchées) — 2026-09-25
## Budget : itérations 1/10, essais 16 consommés / 22 déclarés / 200 max
Branche : `claude/new-session-0ydmkg`. Prompt source : `prompts/2_BUILDER_RAIL_RAPIDE.md`. Registre : `research/fast_rail/registry.jsonl`.
Le sandbox a un accès direct aux API publiques : HL, dYdX, OKX (seulement 3 mois de funding), Polymarket, Kalshi, football-data.co.uk. Yahoo répond 429. EDGAR répond 403 sans UA de contact.

## REPRISE (nouvelle session, peu de tokens)
0. RÈGLE DE CHECKPOINT : lancer `bash scripts/fast_rail_checkpoint.sh` après chaque étape et avant de lancer des agents. Le script sauvegarde le travail de chaque worktree d'agent en patch dans `research/fast_rail/wip/`, puis commit et push. Au plus 2 agents par vague, et chaque agent doit committer après chaque sous-étape.
1. `git checkout claude/new-session-0ydmkg && PYTHONPATH=src python3 -m unittest discover -s tests -q`
2. H-002 (funding HL-dYdX) : `git apply research/fast_rail/wip/agent-a3193714a9c100166.patch`, qui contient le signal avec hystérésis, la lane, `--market`, le builder et les tests (non vérifiés). Ensuite :
   - `python3 scripts/build_perp_funding_hl_dydx.py` (refait le fetch, environ 110 Mo bruts, jamais committés) ;
   - lancer `run_lane` ;
   - faire passer les tests ;
   - noter le verdict au registre.
   Grille fixe, 6 essais.
3. H-006 (foot Pinnacle vs Polymarket) : pré-enregistrée, 4 essais, rien d'exécuté. Relancer l'agent avec le mandat du registre.
4. Collecteur H-001 : l'agent est mort avant d'écrire du code. Il faut étendre `scripts/fetch_feeds.py` avec les cotes Pinnacle (clé en variable d'environnement `ODDS_API_KEY`, 500 req/mois) et les cotes PM/Kalshi du même run.
5. Red team de la vague, puis `status_artifacts.py --write`, puis commit.

## Sources de données trouvées (2026-09-27)
- `data.binance.vision` (archives publiques du funding Binance USDⓈ-M) : 200 depuis le sandbox. Débloque HL vs Binance en historique.
- `public.bybit.com` (archives publiques Bybit) : 200.
- Cleveland Fed inflation nowcasting : page accessible, point-in-time à vérifier pour Kalshi CPI.
- football-data.co.uk (Pinnacle pré-match) et `fixtures.csv` (forward) : OK.
- Toujours bloqués :
  - EDGAR : il faut un User-Agent avec un e-mail de contact (décision du propriétaire) ;
  - DefiLlama emissions : payant (402) ;
  - Yahoo : 429 depuis le sandbox, donc passer par le relais GitHub.

## En SHADOW
| stratégie | depuis | forward | P&L éval. | t-SPRT | ETA |
|---|---|---|---|---|---|
| calendar_fomc_overnight (SPY_ON) | 2026-09-11 | 1 événement | +0,26 % | CONTINUE | années |

## Verdicts de l'itération 1
| H | niveau | chiffres nets (validation) | motif |
|---|---|---|---|
| H-001 | DÉBLOQUÉE (forward uniquement) | — | clé fournie, offre gratuite de 500 req/mois, sans historique ; lire la variable d'environnement `ODDS_API_KEY` |
| H-002 | INTERROMPU (limite de session) | — | patch `wip/agent-a3193714…` ; dataset non construit |
| H-003 | REJECT | +1,09 %/évt, t 7,15 (dégénéré), seuil 2,64, N=34 | 0 perte sur 48 contrats : test binomial p=0,71 ; ≈0 à 2x frais ; quotes jusqu'à 24h périmées |
| H-004 | REJECT | −0,10 c/contrat, t −0,55, seuil 2,50, N=105 | la sélection adverse mange ~94 % du demi-spread |
| H-005 | REJECT | +6,4 %/évt, t clusterisé 0,86, seuil 2,64, N=69 | moitiés −2,7/+15,2 % ; top 10 % = 98 % ; squeeze (GRASS −262 %) |
Les 15 % les plus récents de chaque jeu H-003/4/5 sont intacts : réutilisables pour une variante nouvelle et pré-enregistrée.

## Constats red team : ouverts HIGH 0 (red team de la vague pas encore lancée) | reportés : aucun

## Backlog (5 suivants, classés)
1. H-006 : cote Pinnacle pré-match (football-data.co.uk, colonnes PSH/PSD/PSA, relevées avant les matchs) contre les prix des matchs EPL sur Polymarket (slugs `epl-xxx-yyy-date`, CLOB `prices-history`). Forward possible via `fixtures.csv`, sans clé.
2. H-007 : fourchettes quotidiennes S&P de Kalshi (KXINX) contre une lognormale implicite du VIX (FRED VIXCLS, clôture de la veille).
3. HL vs OKX funding, en forward uniquement (selon H-002).
4. H-005bis : fade des listings avec stop anti-squeeze (uniquement sur les 15 % intacts, pré-enregistré).
5. Kalshi macro (CPI/NFP) contre nowcast : vérifier d'abord le point-in-time du consensus.
BLOCKED :
- SPAC / merger arb : UA de contact EDGAR ;
- déblocages de tokens : aucun calendrier point-in-time gratuit.

## Actions propriétaire en attente
- Mettre la clé Odds API en variable d'environnement `ODDS_API_KEY` (réglages de l'environnement) ET en secret GitHub `ODDS_API_KEY` (relais `data-feeds.yml`). Ne jamais la committer.
- UA de contact pour EDGAR.

## Leçon de l'itération
Les edges « faciles » des marchés de prédiction disparaissent en validation (sélection adverse, biais longshot non significatif). Un t élevé sans aucune perte est un artefact : exiger un test binomial pour les paris à gain asymétrique.
