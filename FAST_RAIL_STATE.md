# Fast Rail State — itération 2 (autonomie, prompt 11) — 2026-09-29
Branche unique : `claude/new-session-0ydmkg`. Ordre de travail : `prompts/11_BUILDER_REPRISE_AUTONOME.md`, jusqu'au point d'étape du **2026-10-05**.
Gouvernance fusionnée depuis `z4pdlx` : SHADOW_DIRECT (`b883031`) et §9 (`5a527b8`). SPAC et merger arb sont retirés (ordre 10).
Portée : phase de test, TOUT en papier/shadow, toutes venues. Aucun capital ni ordre réel. Les σ déclarés ne peuvent qu'être relevés.
## Budget : itérations 2/10 ; essais consommés 32/200 (dont B6 : 1, session recherche), 34 engagés avec H-010 (3) ; SHADOW_DIRECT ouvertes 1/5 (k utilisé : 1)
| jeu de données | essais | required_t |
|---|---|---|
| perp HL-dYdX | 50, **BRÛLÉ** | 3,29 |
| HL listings | 12 | 2,87 |
| Kalshi météo (trades) | 6, gelé | — |
| Kalshi settled + candles | 6 | 2,64 |
| foot football-data × PM (H-006) | 1 | 1,96 |
| Kalshi trades par catégorie (H-010) | 3, en cours | 2,39 |

## REPRISE
0. `bash scripts/fast_rail_checkpoint.sh` avant toute tâche longue. Hooks Stop, SubagentStop et PreCompact actifs. Au plus 2 agents par vague, en Sonnet. Un commit par sous-étape.
1. **Red team H-001 faite**, 3 HIGH corrigés (RT-2026-09-29-02). Statistique amendée avant tout forward : CLV mesurée sur le prix de la venue elle-même (Pinnacle ne fait que sélectionner). H1 0,095σ, ≈ 806 matchs, horizon 1 500. MED encore ouverts : profondeur Kalshi, workflow `if: always()`, taille des shards.
2. **H-010 (R1)** : le scan d'index tourne dans `.claude/worktrees/agent-ac9a307db8faaf614` (≈ 140 000 événements ; Sports 79 289, Entertainment 970, World 2).
   - Si le conteneur est perdu : `git apply research/fast_rail/wip/agent-ac9a307db8faaf614.patch`, puis décompresser `wip/h010_index/events_index.jsonl.gz` et copier `index_checkpoint.json` dans `data/fast_rail/h010/raw/`.
   - Ensuite : `python3 research/fast_rail/h010/sample.py index` jusqu'à épuisement du curseur, puis `detail`, `build`, `fetch.py`, `analysis.py`, et les verdicts au registre.
   - World (2 marchés) ira en REJECT(POWER).
3. **Micro-test maker** : chiffrer après les markouts de H-010. C'est une proposition au propriétaire pour le 10-05, pas une autorisation.
4. **FOMC** : collecte à coût nul, rien d'autre.

## En SHADOW / SHADOW_DIRECT
| stratégie | k / α | statistique | depuis | N forward | état |
|---|---|---|---|---|---|
| H-001 corrigée (Pinnacle vs Kalshi/PM) | 1 / 0,025 | CLV nette de frais mesurée sur la venue, par match ; proxy P&L > 0 (≥ 30 paris réglés, figé à l'arrêt) | 2026-09-29T14:00Z | 0 | CONTINUE ; ≈ 806 matchs attendus si H1 est vraie |
| calendar_fomc_overnight | — | P&L | 2026-09-25 | 0 | CONTINUE (des années) |
L'évaluation H-001 tourne toute seule : collecte complète GitHub Actions (toutes les 6 h), puis `research/fast_rail/h001/forward.py`, qui écrit `data/feeds/eval/h001_shadow_direct.json`.

## Verdicts
| H | niveau | chiffres | cause |
|---|---|---|---|
| H-002 | REJECT | SR −0,03 | SIGNAL + COÛTS (dataset brûlé) |
| H-003 | REJECT | t dégénéré, binomial p = 0,71 | SIGNAL |
| H-004 / H-007 | REJECT | −0,10 c ; t 1,34 | SIGNAL / CONCENTRATION (météo gelée) |
| H-005 | REJECT | t 0,86 / 1,82 contre 2,87 | PUISSANCE ; forward seulement |
| H-006 | REJECT | 3 paris en validation | PUISSANCE + CONCENTRATION |
| H-008 | NON ENTRÉE | — | carry, sur la liste « ne pas tester » |
| H-009 | NON ENTRÉE | ≈ 1 500 adjudications pour conclure | aucun verdict atteignable |
| H-012 | BLOCKED | RFQ 401 | compte Kalshi |
| H-013 | FILTERED | — | LIP comme edge : ne pas tester |
| H-014 (B6, crypto horaire above-K vs DVOL) | UNDERPOWERED, NON ENTRÉE | expected_t 0,36 | aucun effet sourcé ; voir 10-05 |

## Constats red team
- RT-2026-09-27-01 (invariant 6, `pristine_after`) : CORRIGÉ.
- RT-2026-09-29-01 (t-SPRT, pertes rares : 12 % de fausses acceptations à α 2,5 %) : CORRIGÉ par un plancher de σ déclaré.
- RT-2026-09-29-02 (H-001) : 3 HIGH corrigés ; MED ouverts listés au registre.

## Collecte (GitHub Actions, branche de données, `ae51f91`)
- Pinnacle EPL et NBA, avec quotes Kalshi et PM au même instant.
- Ligues de niche (K-League, Liga MX, NCAAF) : cotes Pinnacle seulement. Aucun appariement de venue n'est encore défini.
- Trades après le coup d'envoi (diagnostic maker H-011).
- Récompenses LIP : retirées.

## Pour le 2026-10-05
- H-014 : accepter ou non un H1 dérivé du mécanisme (statistique d'écart à T−5 min : décision possible en ≈ 3-4 mois).
- Micro-test maker : chiffrage.
- Juridiction d'exécution.

## Leçon
Le goulot est le forward, pas les idées. Les tests à faible variance (CLV, markouts) ne valent qu'avec un σ déclaré conservateur.
