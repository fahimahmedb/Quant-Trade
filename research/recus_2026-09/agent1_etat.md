# Ordre 13 — AGENT 1 « REGISTRES PUBLICS » — fichier d'état

- Statut : DONE
- trigger_id : trig_01V9PXek4Q8R9FQuLXPcotnR (cron horaire, minute 17, session courante)
- Branche : claude/dazzling-dirac-foklrv
- Livrable : research/recus_2026-09/agent1_registres.md

## Décisions
- Branche absente sur origin : créée localement depuis le HEAD cloné (09ba64b).
- Classificateur auto-mode instable au démarrage : Routine créé au 7e essai.

## Sources consultées
- WebSearch : Solidus Labs (rapport Polymarket 29/04/2026), doc frais Polymarket (frais taker globaux depuis 25/09/2026, rebates maker 15–25 %), arXiv 2508.03474 (arbitrage Polymarket), vaultvision (vaults HL).

## Notes factuelles (repérage)
- Réseau OK : data-api.polymarket.com, user-pnl-api.polymarket.com, clob.polymarket.com, gamma-api, api.hyperliquid.xyz, stats-data.hyperliquid.xyz. Python urllib exige un User-Agent (sinon 403) et SSL_CERT_FILE=/root/.ccr/ca-bundle.crt.
- Leaderboard Polymarket : les P&L fenêtre MONTH sont incohérents avec ALL (ex. Lucerys MONTH −732 k$, ALL −3,8 k$, même volume). On ne s'en sert pas comme reçu ; on utilise closed-positions (realizedPnl net de frais) et user-pnl.
- Frais Polymarket (doc officielle + gamma feeSchedule vérifié) : fee = C × rate × p(1−p), rates 0,04–0,07, geopolitics 0 ; rebate maker 15 % (sports) à 25 %. Rollout : crypto 05/01/2026, sports 18/02/2026, autres catégories 30/03/2026 (Pine Analytics).
- Pool de récompenses de liquidité (clob /rewards/markets/current, vérifié) : 16 179 marchés, 129 514 $/jour (~3,9 M$/30 j), la plupart 1–5 $/jour/marché, min 20–200 parts, spread max 2,5–6,5 ¢.
- activity?type=REWARD|MAKER_REBATE : reçus on-chain par portefeuille (tx hash). swisstony : 111 k$ de REWARD sur 12 mois.
- France : Polymarket en « close-only » (doc geoblock officielle) + blocage FAI ordonné par l'ANJ le 16/07/2026.
- Hyperliquid vaults (stats-data /Mainnet/vaults, vérifié) : 9 476 vaults, 2 159/8 037 avec P&L non nul sont gagnants (27 %).
- Hyperliquid leaderboard (vérifié) : 46 863 comptes ; 198 comptes « MM » (vol > 1 Md$, |pnl|/vol < 2 pb) : 104 gagnants, 0,2–1,9 pb/vol ; mois : 47/108 gagnants.
- Arbitrage Polymarket (arXiv 2508.03474) : 01/04/2024–01/04/2025, ~40 M$ réalisés (10,6 M$ single-condition, 28,9 M$ NegRisk rebalancing, 95 k$ combinatoire), top adresse 2,0 M$, zéro frais à l'époque.
- Uniswap v3 : ~49,5 % des positions à rendement négatif (source secondaire) ; LVR > frais sur les grands pools (arXiv 2404.05803).

## Décisions de finalisation (ordre du propriétaire : MODE FINALISATION)
- cat_pnl.py (météo, non borné) arrêté après ~50 min sans sortie ; remplacé par wx_bounded.py : top 10 par P&L + 20 portefeuilles échantillonnés, 30 pages max, tronqués signalés.
- maker.py (1 159 portefeuilles) arrêté à ~200/1 159 sans sortie exploitable ; part de makers perdants = « inconnu » dans R2 et R3.
- Livrable écrit en un seul commit (toutes les données étaient déjà collectées) au lieu d'un commit par fiche.
- R7 DEX-LP réduit à une ligne des « Négatifs utiles » (pas de vérification directe).

## Fiches terminées
R1 PM-METEO · R2 PM-MAKER-RECOMPENSES · R3 PM-SPORTS-MM · R4 HL-MM · R5 PM-ARB · R6 HL-VAULTS · Négatifs utiles.

## Prochaine étape
Aucune. Statut DONE : au réveil, supprimer le Routine trig_01V9PXek4Q8R9FQuLXPcotnR s'il existe encore, sans rien faire d'autre.
