# Ordre 13 — AGENT 3 « RECETTE ET REÇU » — état

- statut: EN_COURS
- trigger_id: trig_017Mo7PhDqQRfCP3LgkPM57m (cron horaire, self-bind)
- branche: claude/exciting-edison-w68tos
- REAL_CAPITAL_AUTHORIZED = FALSE

## Sources consultées
- github warproxxx/poly-maker (README Jan 2026: « not profitable »; réécrit Jul 2026)
- arXiv 2508.03474 (arb Polymarket Apr24–Apr25, ~39,6 M$, top compte 2,0 M$)
- pineanalytics fee rollout; docs frais Polymarket V2 (30/03/2026)
- kacho.io x3, github kachence/polymm, API Polymarket wallet 0x1c55…84ce
- suislanchez weather bot (paper only → rejeté)
- stats-data.hyperliquid.xyz/Mainnet/vaults (9476 vaults) + vaultDetails top-TVL >1 an ; Growi HF (méthode vague: mean-reversion), Systemic, Long HYPE/Short Garbage; descriptions de 112 vaults TVL>30k: aucune méthode reproductible liée
- data-api leaderboard category=WEATHER + activity type REWARD/MAKER_REBATE (lisibles publiquement)
- polytrading.app/market-makers (RN1 reward 43,9k/30j)

## Fiches terminées
- F1 polymm/@b00k13 (vérifié, edge mort/marginal)
- F2 vaults HL L/S émission (reçu vérifié, edge = bêta)
- F3 météo Polymarket (probable, survivant)
- F4 subventions maker Polymarket (subventions vérifiées, net inconnu)
- F5 arb rééquilibrage Polymarket (reçu 2024-25, fermé en grande partie)

## Prochaine étape
Prochaine: négatifs utiles + classement + statut DONE + delete_trigger. (ancien: négatifs, classement, DONE. Autres idées: arbitrage NegRisk Polymarket récent (géopolitique sans frais); liquidations; météo Polymarket avec wallet+méthode; rewards Polymarket.

## (ancienne) Repérage rapide (≤20 candidats) : bots OSS avec P&L relié à une adresse, vaults Hyperliquid documentés, bilans de market makers petite taille, dashboards building in public.
