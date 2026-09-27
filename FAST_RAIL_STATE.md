# Fast Rail State — itération 1 (unifiée) — 2026-09-27
Unifié avec `claude/new-session-3ujgeu` (arrêté, SHA final `5255ba2`) le 2026-09-27. Adoption Blue `bd19712` intégrée (via `kfwf1b`).
Branche unique : `claude/new-session-0ydmkg`. Règles : `prompts/2_BUILDER_RAIL_RAPIDE.md` (corrigé) + `prompts/5_ECONOMIE_DES_ESSAIS.md`.
## Budget : itérations 1/10, essais consommés 30/200 (0ydmkg 16 + 3ujgeu 14)
| jeu de données | essais cumulés | required_t |
|---|---|---|
| perp_funding_hl_dydx_daily | 50 → **BRÛLÉ** (historique interdit) | 3,29 |
| HL listings (H-005 + ex-3ujgeu H-006) | 12 | 2,87 |
| Kalshi météo, carnet de trades (H-004 + H-007) | 6 | — |
| Kalshi settled + candles (H-003) | 6 | 2,64 |

## REPRISE
0. `bash scripts/fast_rail_checkpoint.sh`. Des hooks Stop, SubagentStop et PreCompact le lancent automatiquement. Au plus 2 agents par vague, avec un commit par sous-étape.
1. Calcul de puissance AVANT toute déclaration : `expected_t` contre `required_t`. Si c'est insuffisant : UNDERPOWERED, sans consommer d'essai. Grille : 1 expression par défaut, 3 au plus.
2. Ordre de reprise :
   - (a) Collecteur H-001 : cotes Pinnacle via la variable d'environnement `ODDS_API_KEY` (500 req/mois) et quotes PM/Kalshi, relevées dans le même run.
   - (b) H-006, foot Pinnacle (football-data) contre Polymarket : pré-enregistré, 4 essais. À ramener à 1 expression (power, 0,02) selon la règle 2 avant exécution, ou à marquer UNDERPOWERED.
   - (c) Funding HL contre Binance/Bybit sur les archives publiques (`data.binance.vision`, `public.bybit.com`) : nouveau jeu de données, plus de 4 ans.
   - (d) Construire le jeu HL-dYdX pour le forward seulement : `python3 scripts/build_perp_funding_hl_dydx.py --offline --end <date>`. Le cache brut est local (non versionné). Aucun `run_lane` historique.
3. EDGAR : l'UA de contact est approuvé par le propriétaire (dans le scratchpad, jamais versionné). Le SPAC / merger arb est débloqué ; module hors `sec/`.

## En SHADOW
| stratégie | depuis | forward | P&L éval. | t-SPRT | ETA |
|---|---|---|---|---|---|
| calendar_fomc_overnight (SPY_ON) | 2026-09-11 | 1 événement | +0,26 % | CONTINUE | années |

## Verdicts (cause)
| H | niveau | chiffres nets | cause |
|---|---|---|---|
| H-001 | DÉBLOQUÉE, forward seulement | — | clé fournie ; sans historique |
| H-002 | REJECT (importé de 3ujgeu) | SR −0,03, t −0,03 contre 3,29, 70 jours actifs | SIGNAL + COÛTS ; la grille de 0ydmkg est retirée sans avoir tourné |
| H-003 | REJECT | t 7,15 dégénéré, binomial p = 0,71 | SIGNAL (0 perte sur 48 contrats) |
| H-004 | REJECT | −0,10 c/contrat, t −0,55 | SIGNAL (sélection adverse ≈ 94 %) |
| H-005 | REJECT | ici t 0,86 ; 3ujgeu SR 1,52, t 1,82 contre 2,87 (12 essais) | PUISSANCE (3ujgeu) / CONCENTRATION (ici) |
| H-007 | REJECT (importé : ex-3ujgeu H-004) | +0,46 c/contrat, t clusterisé 1,34 | CONCENTRATION |
**À reprendre en forward seulement (REJECT PUISSANCE)** : fade des listings HL (H-005). Aucun nouvel essai historique.

## Constats red team : HIGH ouverts 0
Invariants 9 et 10 vérifiés sur la lane HL-dYdX : chemin Desk inchangé, manchon par stratégie, RISK sur le portefeuille final. Le red team de la vague reste à faire sur les prochains CANDIDATE.

## Backlog et BLOCKED
- Voir REPRISE §2.
- BLOCKED : déblocages de tokens (DefiLlama payant, 402).
- Kalshi CPI contre nowcast de la Cleveland Fed : le point-in-time reste à vérifier.

## Actions propriétaire en attente
- Secret GitHub `ODDS_API_KEY`, pour la collecte quotidienne par le relais.
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.
