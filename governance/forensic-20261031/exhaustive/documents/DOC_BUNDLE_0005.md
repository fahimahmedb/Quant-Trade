===== DOCUMENT 001 =====
BLOB: b85b4d261353a10d097e2fd77eb633352c9519f6
REPRESENTATIVE_PATH: DEPLOYMENT_GUIDE.md
PATH_COUNT: 1
PATHS: DEPLOYMENT_GUIDE.md
BYTES: 6180
ENCODING_STATUS: UTF8
SHA256_CONTENT: 515ddf36766c67b86dbbfcf19384b82a0ec382c39889c26a9185d27212205d08
----- CONTENT START -----
# Quant-Trade: Validated Strategy & Deployment Guide

**Status:** Production-ready  
**Date:** July 26, 2026  
**Methodology:** Strict anti-data-snooping, walk-forward validation, SPA/DSR tested

---

## The Validated Baseline

After rigorous multi-stage testing with proper causal validation and statistical corrections, the project has identified and tested three approaches:

### Phase A: Market Structure
- **Finding:** NDX shows weak mean-reversion (VR 0.889, z*=−2.68, p=0.007); ARCH effects massive
- **Conclusion:** Market is trending with high volatility persistence; suitable for vol-based overlays

### Phase B: Directional Signals  
- **Testing:** N=4+7 signals (BuyHold, Momentum, LogitL2, HistGB, plus 7 alternatives)
- **Result:** **BuyHold is unbeaten** (NDX Sharpe +0.52, DSR 0.842); no active signal passes DSR > 0.95
- **Best alternative:** S5 (EMA 50>200) Sharpe +0.63, but below DSR threshold
- **Key lesson:** Directional signals are exceptionally hard to beat passive indexing

### Phase C: Volatility Forecasting (✅ ROBUST, SPA-validated)
- **Model:** GJR-GARCH(1,1)-t
- **Validation:** Walk-forward on 9522 NDX OOS observations, 454 refits
- **Result:** Superior to EWMA/GARCH-n benchmark (DM p=0.000, SPA p=0.0000)
- **Deployment:** Daily volatility forecasts for position sizing & risk management

### Phase D: Optimal Overlay (✅ WORKING, criterion-met)
- **Strategy:** Vol-targeting on BuyHold (no shorting) + extreme volatility cut
- **Performance:**
  - **NDX (40 years):** Sharpe +0.68 (vs BH +0.52), MDD −57.2% (vs BH −82.9%)
  - **Composite (5 years indep.):** Sharpe +0.56, MDD −20.1%
  - **Advantage:** +31% MDD reduction while keeping 112% of BH returns
- **Mechanism:** 
  1. Forecast vol(t+1) from GJR-GARCH
  2. Scale position to target 15% vol (or unwind if vol > 95th pct)
  3. Hold; rebalance daily

---

## The Real Numbers (Causal, No Lookahead)

| Metric | Value | Notes |
|--------|-------|-------|
| **Baseline (BuyHold)** | Sharpe +0.52 / MDD −83% | NDX 40 years |
| **Best achievable (Phase D)** | Sharpe +0.68 / MDD −57% | Vol-targeting overlay |
| **Edge** | +0.16 Sharpe / +31% MDD | Modest but real |
| **Cross-market** | Composite 0.56 Sharpe | Consistent |

**Cost:** ~5 bps roundtrip (daily rebalancing)  
**Leverage:** Capped at 1.5× (no margin)  
**Turnover:** ~0.30/day (vol adjustments)

---

## What NOT to Deploy

🚫 **The S5-OV 0.875 Sharpe claim** — This was a lookahead artifact:
- Momentum calculation included the current return being traded
- Vol quantiles drawn from full sample (unknowable in real-time)
- When corrected for causality, S5-OV drops to 0.574 Sharpe (worse than BH)
- **Lesson:** Always verify causal alignment in feature computation

🚫 **The ML momentum filter (4.27 → 0.701 Sharpe)** — Same lookahead bug
- Filter read tomorrow's return and only went long when positive
- All Sharpe figures 3.3–5.3 in prior reports are artifacts
- Strict rebuild shows it loses to BuyHold by 0.46 Sharpe

---

## Deployment Checklist

### Step 1: Verify Canonical Code
```bash
# All canonical Phase A/B/C/D code is in:
ls -la finance/trading/scripts/run_etape_*.py
python3 finance/trading/scripts/run_etape_a.py data/nasdaq100_daily.txt
python3 finance/trading/scripts/run_etape_b.py data/nasdaq100_daily.txt
python3 finance/trading/scripts/run_etape_c.py data/nasdaq100_daily.txt
python3 finance/trading/scripts/run_etape_d_combined.py data/nasdaq100_daily.txt
```

### Step 2: Paper-Trade Phase D
- Use `run_etape_d_combined.py` output
- Daily 15:55 rebalance (pre-close)
- Monitor: Sharpe (target +0.65), MDD (target <−30%), turnover (actual vs 0.30)

### Step 3: Live Deployment (6+ months of paper first)
- Only move to live after 6 months consistent 0.60+ Sharpe on paper
- Start with 10% of AUM, scale after 3 months
- Kill-switch: If 3-month rolling Sharpe < 0.40, stop and revert to BH

### Step 4: Quarterly Review
- Refit GJR-GARCH on last 12 months data
- Check if vol regime has shifted (percentiles drifting)
- Verify causality (feature alignment, no lookahead)

---

## Support Files

**Data:**
- `data/nasdaq100_daily.txt` — NDX 1985-2026 (40 years)
- Format: tab-separated [date, open, high, low, close, volume, currency]

**Canonical Code:**
- `finance/trading/src/data_loader.py` — OHLC loading, causal returns
- `finance/trading/src/prediction.py` — Signals (B), backtest, metrics
- `finance/trading/src/volatility.py` — GJR-GARCH, forecasting (C)
- `finance/trading/scripts/run_etape_d_combined.py` — Production overlay (D)

**Validation:**
- `scripts/phase_b_strict_rebuild.py` — Strict walk-forward validation (no lookahead)
- `results/phase_b_strict_rebuild.json` — OOS metrics from strict rebuild

---

## Key Principles

1. **Causality first:** Features must use only data available at decision time
2. **Walk-forward always:** Never optimize on test data
3. **Embargo strictly:** 21-day embargo prevents lookahead contamination
4. **Cross-market:** Validate on independent data (different market/period)
5. **Statistical guards:** DSR > 0.95, SPA p-value tested, FDR controlled
6. **Realistic costs:** 5 bps roundtrip, no magic slippage

---

## Historical Lessons

| Mistake | Impact | Prevention |
|---------|--------|-----------|
| Momentum includes r[t] | −3.75 Sharpe | Use `r.iloc[i-w : i]` not `i+1` |
| Vol quantiles on full sample | False amplification | Refit quantiles on train data only |
| No embargo period | Lookahead bias | Purge/embargo = 21 days minimum |
| Multiple testing, no correction | Spurious findings | Declare N, apply Bonferroni/DSR |

---

## Next Steps

1. **Immediate:** Run all four `run_etape_*.py` scripts to verify baseline
2. **Week 1-2:** Paper-trade Phase D on live data
3. **Month 1-3:** Monitor paper performance, collect live fills/slippage
4. **Month 3:** Decide: live deployment or retest on different market
5. **Month 6+:** Review leverage, costs, regime shifts

---

**Questions?** Review the code in `finance/trading/` — it is the source of truth.

**Validation:** All claims reproducible via walk-forward with embargo. No curves fit, no data snooping.

---

*End of Deployment Guide*

----- CONTENT END -----
===== END DOCUMENT 001 =====

===== DOCUMENT 002 =====
BLOB: 22584a7d402df0fdf64ce7e566e14bb11b910ef9
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 4217
ENCODING_STATUS: UTF8
SHA256_CONTENT: 32566f9d69d0f3339ff17e1ceebb4ce0dd1124cd022b769998e1ef7c93b17cdf
----- CONTENT START -----
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
   - (a) Collecteur H-001 (KPI : CLV contre la juste valeur Pinnacle de clôture, marge retirée ; le P&L confirme) : cotes Pinnacle via la variable d'environnement `ODDS_API_KEY` (500 req/mois) et quotes PM/Kalshi, relevées dans le même run.
   - (b) H-006, foot Pinnacle (football-data) contre Polymarket : pré-enregistré, 4 essais. À ramener à 1 expression (power, 0,02) selon la règle 2 avant exécution, ou à marquer UNDERPOWERED.
   - (c) H-009, adjudications du Trésor : **UNDERPOWERED**, 0 essai. Avec N=5 (article) et un effet réduit de moitié à 7,5 bp sur ≈153 adjudications à 10 ans, expected_t = 0,99 contre 1,96, et 1,39 au mieux en ajoutant les 2 et 5 ans. Candidat SHADOW_DIRECT si Blue l'adopte. Funding HL contre Binance/Bybit : H-008, UNDERPOWERED, forward seulement.
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
- Ne pas tester (preuve externe négative) : juste valeur météo Kalshi (arXiv 2609.23969), Kalshi CPI contre nowcast, longshot Kalshi, catégorie Finance de Kalshi.

## Actions propriétaire en attente
- Secret GitHub `ODDS_API_KEY`, pour la collecte quotidienne par le relais.
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.

----- CONTENT END -----
===== END DOCUMENT 002 =====

===== DOCUMENT 003 =====
BLOB: 3af77189c207078fa9efc889b81a7ec01e07ef58
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 3844
ENCODING_STATUS: UTF8
SHA256_CONTENT: 1271878fcb8434fbb158e66e218e40be2d6ec5accafc09dc41f248c2c442ad47
----- CONTENT START -----
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

----- CONTENT END -----
===== END DOCUMENT 003 =====

===== DOCUMENT 004 =====
BLOB: 4fcf85d24047af25c5a85e88fa783cd4374c0b8e
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 2
PATHS: FAST_RAIL_STATE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/4fcf85d24047af25c5a85e88fa783cd4374c0b8e.txt
BYTES: 2612
ENCODING_STATUS: UTF8
SHA256_CONTENT: 8dc0c22c8a46b6b514e174899513da80c6926f70cb6ca6e801e6281f73c7bf33
----- CONTENT START -----
# Fast Rail State — itération 1 (en cours) — 2026-09-27

## REPRISE (lire en premier après une coupure)
- Branche : `claude/new-session-3ujgeu` (= rail rapide ; base prototype + adoption Blue bd19712 vérifiée).
- Étape en cours : **it.1, étape B** (vague parallèle). Les 4 agents de la vague 1 (H-002, H-004, H-006, Données) ont été tués par la limite de session le 2026-09-25 **avant tout commit** : aucun essai consommé, rien à récupérer.
- Prochaine action : relancer la vague 1 avec **2 agents max** (H-006 puis H-002), chacun commit + push WIP sur `fast-wip/<H-id>` toutes les ~30 min.
- Registre : `research/fast_rail/registry.jsonl` (déclarations H-001..H-006 faites avant données).

## Budget : itérations 1/10, essais 0/200 consommés (14 déclarés : H-002 6, H-004 2, H-006 6)

## En SHADOW
| stratégie | depuis | forward | note |
|---|---|---|---|
| calendar_fomc_overnight (SPY MOC→MOO) | pristine_after 2026-09-11 | 1 événement (2026-09-16, +0,26 %) | laisser accumuler ; ne pas re-tester |

## Verdicts de cette itération
| H-id | niveau | motif |
|---|---|---|
| H-001 Pinnacle vs PM/Kalshi sport | BLOCKED(data) | secret `ODDS_API_KEY` absent du relais |
| H-002 HL vs dYdX funding (hystérésis) | IDEA | agent interrompu, 0 essai |
| H-004 Kalshi météo, P&L maker à règlement | IDEA | agent interrompu, 0 essai |
| H-006 fade des listings HL | IDEA | agent interrompu, 0 essai |

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

----- CONTENT END -----
===== END DOCUMENT 004 =====

===== DOCUMENT 005 =====
BLOB: 509c06a2ce2c0bd1fdf7c748703f273cb3e26f0f
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 3943
ENCODING_STATUS: UTF8
SHA256_CONTENT: 94a55eb0fa0ef62c5666f18cd8b4fc2791f3e36428666b8470645c6bd57ccfa9
----- CONTENT START -----
# Fast Rail State — itération 1 (vague 1 : 4/5 tranchées) — 2026-09-25
## Budget : itérations 1/10, essais 16 consommés / 22 déclarés / 200 max
Branche : `claude/new-session-0ydmkg`. Prompt source : `prompts/2_BUILDER_RAIL_RAPIDE.md`. Registre : `research/fast_rail/registry.jsonl`.
Le sandbox a un accès direct aux API publiques : HL, dYdX, OKX (seulement 3 mois de funding), Polymarket, Kalshi, football-data.co.uk. Yahoo répond 429. EDGAR répond 403 sans UA de contact.

## REPRISE (nouvelle session, peu de tokens)
1. `git checkout claude/new-session-0ydmkg && PYTHONPATH=src python3 -m unittest discover -s tests -q`
2. Finir H-002 : `git apply research/fast_rail/h002/WIP_2026-09-25.patch`. Le patch contient le signal avec hystérésis, la lane, `--market`, le script builder et les tests, sans état vérifié. Ensuite :
   - `python3 scripts/build_perp_funding_hl_dydx.py`, qui refait le fetch (cache brut ≈ 95 Mo, à ne pas committer) ;
   - lancer `run_lane` sur la lane HL-dYdX ;
   - vérifier que le suite de tests passe ;
   - noter le verdict au registre.
   Grille fixe, 6 essais. Un relancement de la grille compte 6 de plus.
3. Red team de la vague (économique + runtime) sur H-002 si CANDIDATE, puis `status_artifacts.py --write`, puis commit `fast-rail: iteration 1 — ...`.
4. Vague 2 : pré-enregistrer dans le registre AVANT de toucher les données (voir le backlog).

## En SHADOW
| stratégie | depuis | forward | P&L éval. | t-SPRT | ETA |
|---|---|---|---|---|---|
| calendar_fomc_overnight (SPY_ON) | 2026-09-11 | 1 événement | +0,26 % | CONTINUE | années |

## Verdicts de l'itération 1
| H | niveau | chiffres nets (validation) | motif |
|---|---|---|---|
| H-001 | DÉBLOQUÉE (forward uniquement) | — | clé fournie, offre gratuite de 500 req/mois, sans historique ; lire la variable d'environnement `ODDS_API_KEY` |
| H-002 | EN COURS | — | patch WIP sauvegardé ; dataset non construit |
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

----- CONTENT END -----
===== END DOCUMENT 005 =====

===== DOCUMENT 006 =====
BLOB: 7337a7f477bec394da319c780a9de9e427c4c62a
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 4735
ENCODING_STATUS: UTF8
SHA256_CONTENT: 887647e908ead450eff53cf395f1b79a9a0dd6ac44ddfaecbebc7faae94f7eec
----- CONTENT START -----
# Fast Rail State — itération 2 (autonomie, prompt 11) — 2026-09-29
Branche unique : `claude/new-session-0ydmkg`. Ordre de travail : `prompts/11_BUILDER_REPRISE_AUTONOME.md`, jusqu'au point d'étape du **2026-10-05**.
Gouvernance fusionnée depuis `z4pdlx` : SHADOW_DIRECT (`b883031`) et §9 (`5a527b8`). SPAC et merger arb sont retirés (ordre 10).
Portée : phase de test, TOUT en papier/shadow, toutes venues. Aucun capital ni ordre réel. Les σ déclarés ne peuvent qu'être relevés.
## Budget : itérations 2/10 ; essais consommés 31/200, 34 engagés avec H-010 (3) ; SHADOW_DIRECT ouvertes 1/5 (k utilisé : 1)
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

----- CONTENT END -----
===== END DOCUMENT 006 =====

===== DOCUMENT 007 =====
BLOB: 78c8d85461557708a7130e704bbbf70e6cc1f3ea
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 2
PATHS: FAST_RAIL_STATE.md | audit/owner-recovery/20261026/pass-01/evidence/blobs/78c8d85461557708a7130e704bbbf70e6cc1f3ea.txt
BYTES: 3195
ENCODING_STATUS: UTF8
SHA256_CONTENT: 48a52f2974b12f052afe3c942a1d157693b1a78c64a0c8da3d4ca5e6dcfdda53
----- CONTENT START -----
# Fast Rail State — itération 1 (en cours) — 2026-09-27

## REPRISE (lire en premier après une coupure)
- Branche : `claude/new-session-3ujgeu` (= rail rapide ; base prototype + adoption Blue bd19712 vérifiée).
- Étape en cours : **it.1, étape B** (vague parallèle). Les 4 agents de la vague 1 (H-002, H-004, H-006, Données) ont été tués par la limite de session le 2026-09-25 **avant tout commit** : aucun essai consommé, rien à récupérer.
- H-006 terminé et fusionné (REJECT). H-004 lancé en remplacement (WIP `-wip-h004`).
- Vague 1 relancée le 2026-09-27 02:22Z avec 2 agents (H-006, H-002). WIP poussé sur `claude/new-session-3ujgeu-wip-h006` / `-wip-h002` (+ `research/fast_rail/wip_h00x.md` = prochaine étape exacte). Après coupure : fetch ces branches, reprendre depuis leur wip_*.md, puis étape C (red team) et D.
- Watchdog : routine horaire (xx:27 UTC) « Fast rail hourly resume » ; la supprimer quand le rail s'arrête (§9).
- Registre : `research/fast_rail/registry.jsonl` (déclarations H-001..H-006 faites avant données).

## Budget : itérations 1/10, essais 6/200 consommés (14 déclarés : H-002 6, H-004 2, H-006 6)

## En SHADOW
| stratégie | depuis | forward | note |
|---|---|---|---|
| calendar_fomc_overnight (SPY MOC→MOO) | pristine_after 2026-09-11 | 1 événement (2026-09-16, +0,26 %) | laisser accumuler ; ne pas re-tester |

## Verdicts de cette itération
| H-id | niveau | motif |
|---|---|---|
| H-001 Pinnacle vs PM/Kalshi sport | BLOCKED(data) | secret `ODDS_API_KEY` absent du relais |
| H-002 HL vs dYdX funding (hystérésis) | IDEA | agent interrompu, 0 essai |
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

----- CONTENT END -----
===== END DOCUMENT 007 =====

===== DOCUMENT 008 =====
BLOB: 7c0eef13b061e208122f10c1d4b26ffe736fa6e5
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 3701
ENCODING_STATUS: UTF8
SHA256_CONTENT: fc65fa8d7d07a4c4a0f6788b3123099b3fe15dd2b22082fe9fca0a8f1c73b533
----- CONTENT START -----
# Fast Rail State — itération 1 (vague 1 : 4/5 tranchées) — 2026-09-25
## Budget : itérations 1/10, essais 16 consommés / 22 déclarés / 200 max
Branche : `claude/new-session-0ydmkg`. Prompt source : `prompts/2_BUILDER_RAIL_RAPIDE.md`. Registre : `research/fast_rail/registry.jsonl`.
Le sandbox a un accès direct aux API publiques : HL, dYdX, OKX (seulement 3 mois de funding), Polymarket, Kalshi, football-data.co.uk. Yahoo répond 429. EDGAR répond 403 sans UA de contact.

## REPRISE (nouvelle session, peu de tokens)
1. `git checkout claude/new-session-0ydmkg && PYTHONPATH=src python3 -m unittest discover -s tests -q`
2. Finir H-002 : `git apply research/fast_rail/h002/WIP_2026-09-25.patch`. Le patch contient le signal avec hystérésis, la lane, `--market`, le script builder et les tests, sans état vérifié. Ensuite :
   - `python3 scripts/build_perp_funding_hl_dydx.py`, qui refait le fetch (cache brut ≈ 95 Mo, à ne pas committer) ;
   - lancer `run_lane` sur la lane HL-dYdX ;
   - vérifier que le suite de tests passe ;
   - noter le verdict au registre.
   Grille fixe, 6 essais. Un relancement de la grille compte 6 de plus.
3. Red team de la vague (économique + runtime) sur H-002 si CANDIDATE, puis `status_artifacts.py --write`, puis commit `fast-rail: iteration 1 — ...`.
4. Vague 2 : pré-enregistrer dans le registre AVANT de toucher les données (voir le backlog).

## En SHADOW
| stratégie | depuis | forward | P&L éval. | t-SPRT | ETA |
|---|---|---|---|---|---|
| calendar_fomc_overnight (SPY_ON) | 2026-09-11 | 1 événement | +0,26 % | CONTINUE | années |

## Verdicts de l'itération 1
| H | niveau | chiffres nets (validation) | motif |
|---|---|---|---|
| H-001 | BLOCKED | — | données : `ODDS_API_KEY` absente |
| H-002 | EN COURS | — | patch WIP sauvegardé ; dataset non construit |
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
- H-001 : clé Odds API ;
- SPAC / merger arb : UA de contact EDGAR ;
- déblocages de tokens : aucun calendrier point-in-time gratuit.

## Actions propriétaire en attente
- Clé The Odds API.
- UA de contact pour EDGAR.

## Leçon de l'itération
Les edges « faciles » des marchés de prédiction disparaissent en validation (sélection adverse, biais longshot non significatif). Un t élevé sans aucune perte est un artefact : exiger un test binomial pour les paris à gain asymétrique.

----- CONTENT END -----
===== END DOCUMENT 008 =====

===== DOCUMENT 009 =====
BLOB: 831230c7bc664d04d7efe00e75bc74a686dc7195
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 2851
ENCODING_STATUS: UTF8
SHA256_CONTENT: c6c3c93c62c0235a3040d8f9d3c43c14c6e238ba9b5772015b83480b7c866b07
----- CONTENT START -----
# Fast Rail State — itération 1 (en cours) — 2026-09-27

## REPRISE (lire en premier après une coupure)
- Branche : `claude/new-session-3ujgeu` (= rail rapide ; base prototype + adoption Blue bd19712 vérifiée).
- Étape en cours : **it.1, étape B** (vague parallèle). Les 4 agents de la vague 1 (H-002, H-004, H-006, Données) ont été tués par la limite de session le 2026-09-25 **avant tout commit** : aucun essai consommé, rien à récupérer.
- Vague 1 relancée le 2026-09-27 02:22Z avec 2 agents (H-006, H-002). WIP poussé sur `claude/new-session-3ujgeu-wip-h006` / `-wip-h002` (+ `research/fast_rail/wip_h00x.md` = prochaine étape exacte). Après coupure : fetch ces branches, reprendre depuis leur wip_*.md, puis étape C (red team) et D.
- Watchdog : `send_later` programmé à 07:22Z (re-programmer +5 h à chaque reprise).
- Registre : `research/fast_rail/registry.jsonl` (déclarations H-001..H-006 faites avant données).

## Budget : itérations 1/10, essais 0/200 consommés (14 déclarés : H-002 6, H-004 2, H-006 6)

## En SHADOW
| stratégie | depuis | forward | note |
|---|---|---|---|
| calendar_fomc_overnight (SPY MOC→MOO) | pristine_after 2026-09-11 | 1 événement (2026-09-16, +0,26 %) | laisser accumuler ; ne pas re-tester |

## Verdicts de cette itération
| H-id | niveau | motif |
|---|---|---|
| H-001 Pinnacle vs PM/Kalshi sport | BLOCKED(data) | secret `ODDS_API_KEY` absent du relais |
| H-002 HL vs dYdX funding (hystérésis) | IDEA | agent interrompu, 0 essai |
| H-004 Kalshi météo, P&L maker à règlement | IDEA | agent interrompu, 0 essai |
| H-006 fade des listings HL | IDEA | agent interrompu, 0 essai |

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

----- CONTENT END -----
===== END DOCUMENT 009 =====

===== DOCUMENT 010 =====
BLOB: 88cc782561ab3cf4c1a253b7d7ce5a4a61c17963
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 3319
ENCODING_STATUS: UTF8
SHA256_CONTENT: 6e0dd879a222974071e8beb7a6605c1a372600c3bc83a4f86ce4b441344db564
----- CONTENT START -----
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

----- CONTENT END -----
===== END DOCUMENT 010 =====

===== DOCUMENT 011 =====
BLOB: 8970b151602f0ea50e072aa683e04b587d5cfb9b
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 7496
ENCODING_STATUS: UTF8
SHA256_CONTENT: 3f739963b73a986770b369bbe4e0ca95f1a05ab03c645b81f7ea07925e64ed63
----- CONTENT START -----
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
     - H-010 = R1, rente maker Kalshi par catégorie : **INTERROMPU** par la limite hebdomadaire.
       - Code complet et testé (29 tests). Patch : `wip/agent-ac9a307db8faaf614.patch`.
       - Scan des métadonnées arrêté à 337 pages (67 400 événements ; retenus : Sports 36 517, Entertainment 702, World 1). Index et curseur sauvés dans `wip/h010_index/`.
       - Pour reprendre : `git apply` du patch ; copier `wip/h010_index/*` (index décompressé) dans `data/fast_rail/h010/raw/` ; `python3 research/fast_rail/h010/sample.py index` jusqu'à épuisement du curseur ; puis `sample.py detail`, `sample.py build`, `fetch.py`, `analysis.py`, verdicts au registre.
       - World ≈ 1 marché : la catégorie tombera en REJECT(POWER).
     - H-011 = R2, maker papier sur le sport de niche contre la clôture Pinnacle : forward seulement, t ≈ 1,96 après ≈ 306 marchés.
     - H-012 = R3, combos RFQ Kalshi : **BLOCKED (accès)**, car les RFQ exigent un compte Kalshi (401).
     - H-013 = R4, récompenses de liquidité (Kalshi LIP et Polymarket, endpoints publics) : forward seulement, en ligne séparée.
     - Collecteur R2/R4 : **INTERROMPU**. 2 commits : ligues de niche dans le planner et balayage des trades après le coup d'envoi. Travail non committé : snapshots récompenses/carnets, évaluateurs, 24 tests. Patch : `wip/agent-ae1e43ef74c5516a4.patch`. À finir, tester, puis fusionner dans la branche de données.
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
- FAIT : secret `ODDS_API_KEY` ajouté. Vérifié : le run du 29/09 09:07 renvoie odds_api OK, et le flux `data/feeds/odds/pinnacle_h2h` existe. La CLV H-001 s'accumule.
- Compte Kalshi et clé API en lecture pour H-012 (flux RFQ).
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.

----- CONTENT END -----
===== END DOCUMENT 011 =====

===== DOCUMENT 012 =====
BLOB: 8c6d7ca127aac0d2defb37172a3dee66397ecf78
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 6445
ENCODING_STATUS: UTF8
SHA256_CONTENT: 931f52e3c08143bbfb6d7e5567d948b994977bce18bf1b2aa429ece3f3ac8554
----- CONTENT START -----
# Fast Rail State — itération 1 (unifiée) — 2026-09-27
Unifié avec `claude/new-session-3ujgeu` (arrêté, SHA final `5255ba2`) le 2026-09-27. Adoption Blue `bd19712` intégrée (via `kfwf1b`).
Branche unique : `claude/new-session-0ydmkg`. Règles : `prompts/2_BUILDER_RAIL_RAPIDE.md` (corrigé) + `prompts/5_ECONOMIE_DES_ESSAIS.md`.
## Budget : itérations 1/10, essais consommés 30/200 (0ydmkg 16 + 3ujgeu 14) ; engagés en cours : H-006 (1) et H-010 (3), soit 34/200
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
   - (b) H-006, foot Pinnacle (football-data) contre Polymarket : pré-enregistré, 4 essais. À ramener à 1 expression (power, 0,02) selon la règle 2 avant exécution, ou à marquer UNDERPOWERED.
   - (c) H-009, adjudications du Trésor : **UNDERPOWERED**, 0 essai. Avec N=5 (article) et un effet réduit de moitié à 7,5 bp sur ≈153 adjudications à 10 ans, expected_t = 0,99 contre 1,96, et 1,39 au mieux en ajoutant les 2 et 5 ans. Candidat SHADOW_DIRECT si Blue l'adopte. Funding HL contre Binance/Bybit : H-008, UNDERPOWERED, forward seulement.
   - (d) Construire le jeu HL-dYdX pour le forward seulement : `python3 scripts/build_perp_funding_hl_dydx.py --offline --end <date>`. Le cache brut est local (non versionné). Aucun `run_lane` historique.
   - (e) Pistes de l'étude praticiens (déclarées au registre avant toute donnée) :
     - H-010 = R1, rente maker Kalshi par catégorie (Sports, Entertainment, World ; fenêtre 2026-04-17 → 09-26 ; 3 essais ; KPI markout +1h) : **EN COURS**.
     - H-011 = R2, maker papier sur le sport de niche contre la clôture Pinnacle : forward seulement, t ≈ 1,96 après ≈ 306 marchés.
     - H-012 = R3, combos RFQ Kalshi : **BLOCKED (accès)**, car les RFQ exigent un compte Kalshi (401).
     - H-013 = R4, récompenses de liquidité (Kalshi LIP et Polymarket, endpoints publics) : forward seulement, en ligne séparée.
     - Collecteur R2/R4 : à lancer dès que H-006 rend. Il ajoute les ligues de niche au plan Odds API, les snapshots de carnets et de récompenses, et la récupération après coup des trades pour les fills « trade-through ».
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
- **CRITIQUE pour tout le forward** : fusionner `.github/workflows/data-feeds.yml` sur la branche par défaut. Sans ça, aucun run planifié : la collecte ne tourne qu'à chaque push sur la branche de données.
- Compte Kalshi et clé API en lecture pour H-012 (flux RFQ).
- Secret GitHub `ODDS_API_KEY`, pour la collecte quotidienne par le relais.
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.

----- CONTENT END -----
===== END DOCUMENT 012 =====

===== DOCUMENT 013 =====
BLOB: 9fa45b105fc003b9bcbce3149e08f89a9afca8f4
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 6594
ENCODING_STATUS: UTF8
SHA256_CONTENT: 13d0f70bc9df1b3fb4b845240889f1c622fd984f11921604e266366721228a70
----- CONTENT START -----
# Fast Rail State — itération 1 (unifiée) — 2026-09-27
Unifié avec `claude/new-session-3ujgeu` (arrêté, SHA final `5255ba2`) le 2026-09-27. Adoption Blue `bd19712` intégrée (via `kfwf1b`).
Branche unique : `claude/new-session-0ydmkg`. Règles : `prompts/2_BUILDER_RAIL_RAPIDE.md` (corrigé) + `prompts/5_ECONOMIE_DES_ESSAIS.md`.
## Budget : itérations 1/10, essais consommés 30/200 (0ydmkg 16 + 3ujgeu 14) ; engagés en cours : H-006 (1) et H-010 (3), soit 34/200
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
   - (b) H-006, foot Pinnacle (football-data) contre Polymarket : pré-enregistré, 4 essais. À ramener à 1 expression (power, 0,02) selon la règle 2 avant exécution, ou à marquer UNDERPOWERED.
   - (c) H-009, adjudications du Trésor : **UNDERPOWERED**, 0 essai. Avec N=5 (article) et un effet réduit de moitié à 7,5 bp sur ≈153 adjudications à 10 ans, expected_t = 0,99 contre 1,96, et 1,39 au mieux en ajoutant les 2 et 5 ans. Candidat SHADOW_DIRECT si Blue l'adopte. Funding HL contre Binance/Bybit : H-008, UNDERPOWERED, forward seulement.
   - (d) Construire le jeu HL-dYdX pour le forward seulement : `python3 scripts/build_perp_funding_hl_dydx.py --offline --end <date>`. Le cache brut est local (non versionné). Aucun `run_lane` historique.
   - (e) Pistes de l'étude praticiens (déclarées au registre avant toute donnée) :
     - H-010 = R1, rente maker Kalshi par catégorie (Sports, Entertainment, World ; fenêtre 2026-04-17 → 09-26 ; 3 essais ; KPI markout +1h) : **EN COURS**.
     - H-011 = R2, maker papier sur le sport de niche contre la clôture Pinnacle : forward seulement, t ≈ 1,96 après ≈ 306 marchés.
     - H-012 = R3, combos RFQ Kalshi : **BLOCKED (accès)**, car les RFQ exigent un compte Kalshi (401).
     - H-013 = R4, récompenses de liquidité (Kalshi LIP et Polymarket, endpoints publics) : forward seulement, en ligne séparée.
     - Collecteur R2/R4 : à lancer dès que H-006 rend. Il ajoute les ligues de niche au plan Odds API, les snapshots de carnets et de récompenses, et la récupération après coup des trades pour les fills « trade-through ».
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

----- CONTENT END -----
===== END DOCUMENT 013 =====

===== DOCUMENT 014 =====
BLOB: be2b67282863af6fca722891b39729645818aac2
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 4934
ENCODING_STATUS: UTF8
SHA256_CONTENT: 62ae13f4789ceb85842bcea14f26ba552a1a654d51e4a3761e54fc1ca7f5d7e6
----- CONTENT START -----
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
   - (a) Collecteur H-001 **EN PLACE** : mergé dans `claude/data-feeds-6vr22g` (b4b80a7). Budget d'environ 250 req/mois (plafonds : 14 par jour, 430 par mois). Premier relevé réel : 20 matchs EPL, 9 appariés sur Kalshi, 0 sur Polymarket (pas encore listés). KPI : CLV contre la clôture Pinnacle (`research/fast_rail/h001/clv.py`). Le planning horaire ne se déclenche que depuis la branche par défaut (action propriétaire) ; sinon, un push sur la branche de données déclenche une collecte.
   - (b) H-006, foot Pinnacle (football-data) contre Polymarket : pré-enregistré, 4 essais. À ramener à 1 expression (power, 0,02) selon la règle 2 avant exécution, ou à marquer UNDERPOWERED.
   - (c) H-009, adjudications du Trésor : **UNDERPOWERED**, 0 essai. Avec N=5 (article) et un effet réduit de moitié à 7,5 bp sur ≈153 adjudications à 10 ans, expected_t = 0,99 contre 1,96, et 1,39 au mieux en ajoutant les 2 et 5 ans. Candidat SHADOW_DIRECT si Blue l'adopte. Funding HL contre Binance/Bybit : H-008, UNDERPOWERED, forward seulement.
   - (d) Construire le jeu HL-dYdX pour le forward seulement : `python3 scripts/build_perp_funding_hl_dydx.py --offline --end <date>`. Le cache brut est local (non versionné). Aucun `run_lane` historique.
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
- Secret GitHub `ODDS_API_KEY`, pour la collecte quotidienne par le relais.
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.

----- CONTENT END -----
===== END DOCUMENT 014 =====

===== DOCUMENT 015 =====
BLOB: c394fc3ce86fa1af86dcfba80a38dfa6d4a50f1a
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 7827
ENCODING_STATUS: UTF8
SHA256_CONTENT: ee21071af4ab29c04dca44bcd43a1e258d1ebffe6f9c27ecf59c65c5dccbf849
----- CONTENT START -----
# Fast Rail State — itération 2 (autonomie, prompt 11) — 2026-09-29
Prompt 11 appliqué : gouvernance z4pdlx fusionnée (SHADOW_DIRECT `b883031`, §9 `5a527b8`). SPAC et merger arb sont RETIRÉS (l'ordre 10 prime). Point d'étape le 2026-10-05.
**Étape 1 FAITE** : `event_sequential_test` (H1 par observation, sans borne ; alpha ; horizon → INCONCLUSIVE), `shadow_direct_alpha(k)`, `binary_payoff_sigma`. Constat HIGH RT-2026-09-29-01 corrigé : un plancher de σ déclaré est obligatoire (8 tests).
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
     - H-010 = R1, rente maker Kalshi par catégorie : **INTERROMPU** par la limite hebdomadaire.
       - Code complet et testé (29 tests). Patch : `wip/agent-ac9a307db8faaf614.patch`.
       - Scan des métadonnées arrêté à 337 pages (67 400 événements ; retenus : Sports 36 517, Entertainment 702, World 1). Index et curseur sauvés dans `wip/h010_index/`.
       - Pour reprendre : `git apply` du patch ; copier `wip/h010_index/*` (index décompressé) dans `data/fast_rail/h010/raw/` ; `python3 research/fast_rail/h010/sample.py index` jusqu'à épuisement du curseur ; puis `sample.py detail`, `sample.py build`, `fetch.py`, `analysis.py`, verdicts au registre.
       - World ≈ 1 marché : la catégorie tombera en REJECT(POWER).
     - H-011 = R2, maker papier sur le sport de niche contre la clôture Pinnacle : forward seulement, t ≈ 1,96 après ≈ 306 marchés.
     - H-012 = R3, combos RFQ Kalshi : **BLOCKED (accès)**, car les RFQ exigent un compte Kalshi (401).
     - H-013 = R4, récompenses de liquidité (Kalshi LIP et Polymarket, endpoints publics) : forward seulement, en ligne séparée.
     - Collecteur R2/R4 : **INTERROMPU**. 2 commits : ligues de niche dans le planner et balayage des trades après le coup d'envoi. Travail non committé : snapshots récompenses/carnets, évaluateurs, 24 tests. Patch : `wip/agent-ae1e43ef74c5516a4.patch`. À finir, tester, puis fusionner dans la branche de données.
3. SPAC / merger arb : RETIRÉS (ordre 10).

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
- FAIT : secret `ODDS_API_KEY` ajouté. Vérifié : le run du 29/09 09:07 renvoie odds_api OK, et le flux `data/feeds/odds/pinnacle_h2h` existe. La CLV H-001 s'accumule.
- Compte Kalshi et clé API en lecture pour H-012 (flux RFQ).
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.

----- CONTENT END -----
===== END DOCUMENT 015 =====

===== DOCUMENT 016 =====
BLOB: c5f903e3884392944ac0b55d6b190423bbe14e75
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 849
ENCODING_STATUS: UTF8
SHA256_CONTENT: e683a1cbde7b44c5ae1f311289e353f91bf7ef74f1f73f880a52cee87c6460ae
----- CONTENT START -----
# Fast Rail State — itération 1 (en cours) — 2026-09-25
## Budget : itérations 1/10, essais déclarés 22/200
Branche : `claude/new-session-0ydmkg` (imposée par la session). Base : prototype futures + two-speed-cleanup. 446 tests OK.
Accès réseau direct depuis le sandbox : HL, OKX (3 mois de funding), dYdX, Polymarket, Kalshi. Yahoo 429 ; EDGAR 403 sans UA.
## En SHADOW
| stratégie | depuis | forward | P&L éval. | t-SPRT | ETA |
|---|---|---|---|---|---|
| calendar_fomc_overnight (SPY_ON) | 2026-09-11 | 1 événement | +0,26 % | CONTINUE | années |
## Vague 1 (pré-enregistrée, en cours) : H-002 funding HL-dYdX, H-003 longshot Kalshi, H-004 maker météo Kalshi, H-005 fade listings HL
## BLOCKED
- H-001 sport Pinnacle vs PM : clé `ODDS_API_KEY` absente (401).
## Actions propriétaire en attente
- Clé The Odds API (H-001).

----- CONTENT END -----
===== END DOCUMENT 016 =====

===== DOCUMENT 017 =====
BLOB: d5d59966309beb0708d3f6ca6a12a61205ee511d
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 4547
ENCODING_STATUS: UTF8
SHA256_CONTENT: 468a01e5f44a222230524f67e631e12d9dc44889d3bd72e215b7e5be06fc2a50
----- CONTENT START -----
# Fast Rail State — itération 2 (autonomie, prompt 11) — 2026-09-29
Branche unique : `claude/new-session-0ydmkg`. Ordre de travail : `prompts/11_BUILDER_REPRISE_AUTONOME.md`, jusqu'au point d'étape du **2026-10-05**.
Gouvernance fusionnée depuis `z4pdlx` : SHADOW_DIRECT (`b883031`) et §9 (`5a527b8`). SPAC et merger arb sont retirés (ordre 10).
Portée : phase de test, TOUT en papier/shadow, toutes venues. Aucun capital ni ordre réel. Les σ déclarés ne peuvent qu'être relevés.
## Budget : itérations 2/10 ; essais consommés 31/200, 34 engagés avec H-010 (3) ; SHADOW_DIRECT ouvertes 1/5 (k utilisé : 1)
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
1. **Red team H-001 SHADOW_DIRECT** : 2 agents en cours (économie, runtime). Tout HIGH doit être corrigé avant le 1er pari forward, vers le 3 octobre (EPL le 10/10, prix relevés à J-7).
2. **H-010 (R1)** : le scan d'index tourne dans `.claude/worktrees/agent-ac9a307db8faaf614` (≈ 140 000 événements ; Sports 79 289, Entertainment 970, World 2).
   - Si le conteneur est perdu : `git apply research/fast_rail/wip/agent-ac9a307db8faaf614.patch`, puis décompresser `wip/h010_index/events_index.jsonl.gz` et copier `index_checkpoint.json` dans `data/fast_rail/h010/raw/`.
   - Ensuite : `python3 research/fast_rail/h010/sample.py index` jusqu'à épuisement du curseur, puis `detail`, `build`, `fetch.py`, `analysis.py`, et les verdicts au registre.
   - World (2 marchés) ira en REJECT(POWER).
3. **Micro-test maker** : chiffrer après les markouts de H-010. C'est une proposition au propriétaire pour le 10-05, pas une autorisation.
4. **FOMC** : collecte à coût nul, rien d'autre.

## En SHADOW / SHADOW_DIRECT
| stratégie | k / α | statistique | depuis | N forward | état |
|---|---|---|---|---|---|
| H-001 corrigée (Pinnacle vs Kalshi/PM) | 1 / 0,025 | CLV nette de frais par match ; proxy P&L > 0 | 2026-09-29T12:00Z | 0 (prochain match EPL le 10/10) | CONTINUE ; ≈ 202 matchs attendus si H1 est vraie ; horizon 1 000 |
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
- Red team H-001 SHADOW_DIRECT : en cours.

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

----- CONTENT END -----
===== END DOCUMENT 017 =====

===== DOCUMENT 018 =====
BLOB: df4d80a3c8198dfe5235a940f8b105e47a9331fd
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 4120
ENCODING_STATUS: UTF8
SHA256_CONTENT: 26dd20aae417a48220d8edb138824eb09897b94ee9b22dab5d2d493b160fd4b9
----- CONTENT START -----
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
   - (a) Collecteur H-001 (KPI : CLV contre la juste valeur Pinnacle de clôture, marge retirée ; le P&L confirme) : cotes Pinnacle via la variable d'environnement `ODDS_API_KEY` (500 req/mois) et quotes PM/Kalshi, relevées dans le même run.
   - (b) H-006, foot Pinnacle (football-data) contre Polymarket : pré-enregistré, 4 essais. À ramener à 1 expression (power, 0,02) selon la règle 2 avant exécution, ou à marquer UNDERPOWERED.
   - (c) Cycle des adjudications du Trésor (Lou, Yan, Zhang 2013), H-009. Une seule expression, avec N tiré de l'article. Validation 2014 → aujourd'hui. Calcul de puissance d'abord. Funding HL contre Binance/Bybit : H-008, UNDERPOWERED, forward seulement.
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
- Ne pas tester (preuve externe négative) : juste valeur météo Kalshi (arXiv 2609.23969), Kalshi CPI contre nowcast, longshot Kalshi, catégorie Finance de Kalshi.

## Actions propriétaire en attente
- Secret GitHub `ODDS_API_KEY`, pour la collecte quotidienne par le relais.
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.

----- CONTENT END -----
===== END DOCUMENT 018 =====

===== DOCUMENT 019 =====
BLOB: e58c51cd8a02c8df14acd08ae3956a0ba90c7f68
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 4472
ENCODING_STATUS: UTF8
SHA256_CONTENT: 65104b8aae95b5739f7b65d18c4c155da5c5512bbf92575471f62057e68a7eea
----- CONTENT START -----
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
   - (a) Collecteur H-001 **EN PLACE** : mergé dans `claude/data-feeds-6vr22g` (b4b80a7). Budget d'environ 250 req/mois (plafonds : 14 par jour, 430 par mois). Premier relevé réel : 20 matchs EPL, 9 appariés sur Kalshi, 0 sur Polymarket (pas encore listés). KPI : CLV contre la clôture Pinnacle (`research/fast_rail/h001/clv.py`). Le planning horaire ne se déclenche que depuis la branche par défaut (action propriétaire) ; sinon, un push sur la branche de données déclenche une collecte.
   - (b) H-006, foot Pinnacle (football-data) contre Polymarket : pré-enregistré, 4 essais. À ramener à 1 expression (power, 0,02) selon la règle 2 avant exécution, ou à marquer UNDERPOWERED.
   - (c) H-009, adjudications du Trésor : **UNDERPOWERED**, 0 essai. Avec N=5 (article) et un effet réduit de moitié à 7,5 bp sur ≈153 adjudications à 10 ans, expected_t = 0,99 contre 1,96, et 1,39 au mieux en ajoutant les 2 et 5 ans. Candidat SHADOW_DIRECT si Blue l'adopte. Funding HL contre Binance/Bybit : H-008, UNDERPOWERED, forward seulement.
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
- Ne pas tester (preuve externe négative) : juste valeur météo Kalshi (arXiv 2609.23969), Kalshi CPI contre nowcast, longshot Kalshi, catégorie Finance de Kalshi.

## Actions propriétaire en attente
- Secret GitHub `ODDS_API_KEY`, pour la collecte quotidienne par le relais.
- Décision Blue sur la voie `SHADOW_DIRECT` (`prompts/5`).

## Leçon
Le goulot est la puissance du test, pas le nombre d'essais. Deux builders en parallèle sur le même jeu de données en ont brûlé l'historique : un seul builder désormais.

----- CONTENT END -----
===== END DOCUMENT 019 =====

===== DOCUMENT 020 =====
BLOB: ecfaafc22e6551ac7321ab482b74423708b2e3d1
REPRESENTATIVE_PATH: FAST_RAIL_STATE.md
PATH_COUNT: 1
PATHS: FAST_RAIL_STATE.md
BYTES: 5048
ENCODING_STATUS: UTF8
SHA256_CONTENT: f3bc5dc99d7a8183a6ec85ffe3bada86e419e0345c9095b6f7db76741a03fa0e
----- CONTENT START -----
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

----- CONTENT END -----
===== END DOCUMENT 020 =====
