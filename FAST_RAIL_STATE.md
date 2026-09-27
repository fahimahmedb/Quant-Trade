# Fast Rail State — itération 1 (unifiée) — 2026-09-27
Unifié avec `claude/new-session-3ujgeu` (arrêté, SHA final `5255ba2`) le 2026-09-27. Adoption Blue `bd19712` intégrée (via `kfwf1b`).
Branche unique : `claude/new-session-0ydmkg`. Règles : `prompts/2_BUILDER_RAIL_RAPIDE.md` (corrigé) + `prompts/5_ECONOMIE_DES_ESSAIS.md`.
## Budget : itérations 1/10, essais consommés 31/200 (0ydmkg 17 + 3ujgeu 14) ; engagés en cours : H-010 (3), soit 34/200
**Portée (propriétaire, 2026-09-27)** : phase de test. On teste TOUT en papier/shadow, sur toutes les venues, sans se limiter à ce qui est déployable. Restent en vigueur : invariants du §3, économie des essais, aucun capital et aucun ordre réels. Les σ sont des hypothèses, à calibrer après 2 semaines de forward.
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
   - (a) Collecteur H-001 **EN PLACE** : mergé dans `claude/data-feeds-6vr22g` (b4b80a7). Budget d'environ 250 req/mois (plafonds : 14 par jour, 430 par mois). Premier relevé réel : 20 matchs EPL, 9 appariés sur Kalshi, 0 sur Polymarket (pas encore listés). KPI : CLV contre la clôture Pinnacle (`research/fast_rail/h001/clv.py`). Le planning horaire ne se déclenche que depuis la branche par défaut (action propriétaire) ; sinon, un push sur la branche de données déclenche une collecte.
   - (b) H-006, foot Pinnacle contre Polymarket : **REJECT** (PUISSANCE et CONCENTRATION). 1 essai.
   - (c) H-009, adjudications du Trésor : **UNDERPOWERED**, 0 essai. Avec N=5 (article) et un effet réduit de moitié à 7,5 bp sur ≈153 adjudications à 10 ans, expected_t = 0,99 contre 1,96, et 1,39 au mieux en ajoutant les 2 et 5 ans. Candidat SHADOW_DIRECT si Blue l'adopte. Funding HL contre Binance/Bybit : H-008, UNDERPOWERED, forward seulement.
   - (d) Construire le jeu HL-dYdX pour le forward seulement : `python3 scripts/build_perp_funding_hl_dydx.py --offline --end <date>`. Le cache brut est local (non versionné). Aucun `run_lane` historique.
   - (e) Pistes de l'étude praticiens (déclarées au registre avant toute donnée) :
     - H-010 = R1, rente maker Kalshi par catégorie (Sports, Entertainment, World ; fenêtre 2026-04-17 → 09-26 ; 3 essais ; KPI markout +1h) : **EN COURS** (relancé en Sonnet après la coupure à la limite de session).
     - H-011 = R2, maker papier sur le sport de niche contre la clôture Pinnacle : forward seulement, t ≈ 1,96 après ≈ 306 marchés.
     - H-012 = R3, combos RFQ Kalshi : **BLOCKED (accès)**, car les RFQ exigent un compte Kalshi (401).
     - H-013 = R4, récompenses de liquidité (Kalshi LIP et Polymarket, endpoints publics) : forward seulement, en ligne séparée.
     - Collecteur R2/R4 : **EN COURS** (Sonnet). Il ajoute les ligues de niche (K-League, Liga MX, NCAAF) au plan Odds API, les snapshots de carnets et de récompenses, la récupération des trades après le coup d'envoi, et des évaluateurs purs (maker trade-through et récompenses).
3. EDGAR : l'UA de contact est approuvé par le propriétaire (dans le scratchpad, jamais versionné). Le SPAC / merger arb est débloqué ; module hors `sec/`.

## En SHADOW
| stratégie | depuis | forward | P&L éval. | t-SPRT | ETA |
|---|---|---|---|---|---|
| calendar_fomc_overnight (SPY_ON) | 2026-09-25 | 0 événement (le 16/09 est exclu : antérieur au commit de la lane) | — | CONTINUE (0 session pristine) | années |

## Verdicts (cause)
| H | niveau | chiffres nets | cause |
|---|---|---|---|
| H-001 | DÉBLOQUÉE, forward seulement | — | clé fournie ; sans historique |
| H-002 | REJECT (importé de 3ujgeu) | SR −0,03, t −0,03 contre 3,29, 70 jours actifs | SIGNAL + COÛTS ; la grille de 0ydmkg est retirée sans avoir tourné |
| H-003 | REJECT | t 7,15 dégénéré, binomial p = 0,71 | SIGNAL (0 perte sur 48 contrats) |
| H-004 | REJECT | −0,10 c/contrat, t −0,55 | SIGNAL (sélection adverse ≈ 94 %) |
| H-005 | REJECT | ici t 0,86 ; 3ujgeu SR 1,52, t 1,82 contre 2,87 (12 essais) | PUISSANCE (3ujgeu) / CONCENTRATION (ici) |
| H-006 | REJECT | validation : 3 paris sur 378 matchs, CLV +2,2 % (t 2,51, dégénéré) ; P&L −5,5 % ; à 2x coûts, t 0,75 | PUISSANCE + CONCENTRATION (Liga 66 %). En discovery, CLV +8,6 % (t 3,5) mais P&L t 0,1 : prix Polymarket anciens et peu liquides. football-data n'a plus Pinnacle depuis janvier 2026 ; le test passe par H-001 en forward |
| H-007 | REJECT (importé : ex-3ujgeu H-004) | +0,46 c/contrat, t clusterisé 1,34 | CONCENTRATION |
**À reprendre en forward seulement (REJECT PUISSANCE)** : fade des listings HL (H-005). Aucun nouvel essai historique.

## Constats red team : HIGH ouverts 0
- RT-2026-09-27-01 (invariant 6) CORRIGÉ : `pristine_after` était antérieur au 1er commit sur 4 familles de lanes (calendaires, perp HL-BY, futures, HL-dYdX), et les lanes ETF n'en avaient pas. Désormais `pristine_after` ≥ date du 1er commit (`LANE_DECLARED_ON`), le cycle de vie prend max(date stockée, date déclarée) et échoue fermé sans date, avec un test de non-régression.
Invariants 9 et 10 vérifiés sur la lane HL-dYdX : chemin Desk inchangé, manchon par stratégie, RISK sur le portefeuille final. Le red team de la vague reste à faire sur les prochains CANDIDATE.

## Backlog et BLOCKED
- Voir REPRISE §2.
- BLOCKED : déblocages de tokens (DefiLlama payant, 402).
- Ne pas tester (preuve externe négative) : juste valeur météo Kalshi (arXiv 2609.23969), Kalshi CPI contre nowcast, longshot Kalshi, catégorie Finance de Kalshi.

## Actions propriétaire en attente
- FAIT (2026-09-27, `09ba64b` sur `blue/master-v2-2026-09-20`, fichier du workflow seul) : le planning des données est actif. Collecte complète toutes les 6 h (:17), relevé Pinnacle toutes les heures (:47). Dépôt public : minutes Actions gratuites.
- **Secret GitHub `ODDS_API_KEY` toujours absent** : le run du 27/09 03:58 répond « ODDS_API_KEY is not configured ». Sans lui, H-001, H-011 et H-013 n'ont pas de cotes Pinnacle.
- Compte Kalshi et clé API en lecture pour H-012 (flux RFQ).
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.
