# Ordre 13 — AGENT 3 « RECETTE ET REÇU » — livrable

Date : 2026-09-29. Recherche externe seulement. REAL_CAPITAL_AUTHORIZED = FALSE.
Règle de lecture : un « reçu » = P&L lisible par un tiers sur une adresse/un vault public.
Les chiffres marqués « API » ont été relus par l'agent le 2026-09-29 sur les API publiques
(`lb-api.polymarket.com/profit`, `data-api.polymarket.com`, `api.hyperliquid.xyz/info`).
Aucune tentative d'identifier les personnes derrière les adresses.

Classement final en fin de document.

---

## F1 — Maker « sportsbook dévigé → Polymarket esports » (polymm / @b00k13)

| Champ | Contenu |
|---|---|
| ID | F1 |
| Titre | Market making Polymarket esports avec juste prix tiré des cotes de bookmakers dévigées, puis couverture de l'autre issue |
| Type | maker (+ arbitrage « paire YES+NO < 1 $ ») |
| Mécanisme : qui paie | Les preneurs Polymarket qui frappent des cotes esports en retard sur les bookmakers (lignes qui bougent, ordres limites oubliés). Ils ne s'arrêtent pas parce que ce sont des parieurs récréatifs ; mais d'autres bots makers se font concurrence pour le même flux. |
| RECETTE | Code MIT : https://github.com/kachence/polymm (init 2026-07-19 ; `src/bots/spread_bot.py`, `src/monitoring/hedge_seeker.py`, `src/core/config.py` : `min_profit` 0,10 $ après frais). Méthode : cotes bookmakers → dévig → proba juste ; ordre limite 1 ¢ au-dessus du meilleur bid si edge ≥ 5–7 % ; quand une jambe est remplie, poster l'autre issue ; si somme < 1 $ → gain verrouillé. Blog : https://kacho.io/polymarket-arbitrage-real-numbers , https://kacho.io/why-my-polymarket-arbitrage-bot-lost-money |
| REÇU | Portefeuille Polymarket `0x1c5575dc20e4ea54d1bb09ccda72ccf8a3b684ce` (profil public @b00k13, bio : « I run my sports market-making/arbitrage bot here… bot… freely available on GitHub (polymm) »). Lien code ↔ adresse déclaré par l'auteur, cohérent avec l'activité (marchés esports MLBB/CS2/LoL). |
| Période / dernière date gagnante | 2026-01-06 → 2026-04-28 (phase 1), redémarré mi-juin 2026 avec ~300 $. Dernier mois gagnant significatif : février 2026. API 2026-09-29 : profit cumulé +5 668,83 $ ; 30 j +130,05 $ ; 7 j +9,91 $ ; valeur des positions 430 $. |
| Ampleur | Auteur : 3 858 paris, 95 830 $ de volume, +4 973 $ net (Jan–Avr). Détail : arbitrages verrouillés +8 293 $ ; jambes non couvertes −3 185 $. Par mois : Jan +1 898, Fév +2 506, Mar +390, Avr +180. Capital : inconnu (positions jusqu'à ~3 k$). |
| Frais 2026 inclus ? | Oui en partie : P&L on-chain net des frais preneur, mais la phase rentable (Jan–Fév) précède l'extension des frais aux autres catégories (sports 18/02/2026, reste 30/03/2026). Le bot est maker (frais 0 + rebates), donc les frais pèsent surtout sur la couverture si elle est prise en taker. Coûts d'infra de cotes : ~3 $/jour (auteur). |
| Pour reproduire | Capital 300–3 000 $ ; flux de cotes bookmakers (scraping/API) rafraîchi en secondes, pas en 30 min ; ~10 processus async + Supabase ; latence : secondes, mais la concurrence gagne sur la vitesse de requote. |
| Pourquoi pas encore fermé | Il EST en train de se fermer : taux de remplissage 37 % (Jan) → 15 % → 5 % → 1 % (Avr) ; arbitrage verrouillé 4 158 $ (Fév) → 17 $ (Avr). Reste une niche d'esports mineurs (MLBB, HoK) à faible liquidité où peu de bots cotent. |
| Risque extrême caché | Sélection adverse : cotes vieilles de 30 min → lignes qui bougent de ≥ 5 pts dans 31–60 % des matchs ; jambe non couverte = pari directionnel ; matchs annulés (remboursement 50 ¢) ; risque de règle de résolution Polymarket ≠ bookmaker. |
| Venues / accès | Polymarket international : US bloqué (Polymarket US = autre venue), **France bloquée (ANJ)**, reste UE : selon pays. Bookmakers utilisés seulement comme source de prix. |
| Vérif 1 jour données publiques | Oui : `data-api.polymarket.com/activity?user=<adresse>` + `lb-api…/profit?window=30d` ; rejouer les fills vs cotes historiques des bookmakers (si archivées) ; mesurer le taux de remplissage des deux jambes. |
| Plafond petite taille | Observé : ~2 500 $/mois au pic (Fév 2026), ~0–130 $/mois depuis mars. Estimation actuelle : **0–150 €/mois**. |
| Confiance | **vérifié** (reçu et code), edge actuel **mort ou marginal** |

---

## F2 — Vaults Hyperliquid « long faible émission / short forte émission » (Long HYPE & BTC | Short Garbage ; Systemic L/S Grids)

| Champ | Contenu |
|---|---|
| ID | F2 |
| Titre | Vaults publics qui déclarent un long/short structurel selon l'émission des tokens (≠ short timé avant déblocage, rejeté) |
| Type | autre (facteur directionnel long/short) |
| Mécanisme : qui paie | Thèse : les détenteurs de tokens à forte émission (équipes/VC qui débloquent) vendent en continu, sans pouvoir s'arrêter tant que le vesting dure ; le short capte cette pression vendeuse. En pratique (voir « risque »), le P&L mesuré vient surtout du long HYPE. |
| RECETTE | Descriptions de vault on-chain (API `vaultDetails`) : (a) `0xac26cf5f3c46b5e102048c65b977d2551b72a9c7` « 70% HYPE 30% BTC long ; short basket of at least 10+ high FDV high emission coins ; short ≈ 60% of notional » ; (b) `0x07fd993f0fa3a185f7207adccd29f7a87404689d` « Grid longing low inflation/unlocks, grid shorting high inflation/unlocks ». Pas de code ; les positions sont publiques et copiables en lecture seule. |
| REÇU | Mêmes adresses, historique de P&L du vault sur `api.hyperliquid.xyz/info` (`vaultDetails`, `clearinghouseState`, `userFillsByTime`, `userFunding`). |
| Période / dernière date gagnante | API 2026-09-29, fenêtre 2025-09-29 → 2026-09-29. (a) P&L 12 m +2,62 M$ ; 6 m +1,38 M$ ; 3 m +0,12 M$ (gagnant mais ralenti). (b) 12 m +0,57 M$ ; 3 m +0,62 M$. |
| Ampleur | (a) Valeur du compte 1,78 M$ il y a 1 an → 2,56 M$ ; notionnel 5,9 M$. Décomposition 12 m (calcul de l'agent) : jambe longue HYPE/BTC réalisé net de frais +337 k$, funding −182 k$, latent actuel +1,84 M$ ; jambe short réalisé +890 k$, funding ≈ 0, latent actuel −286 k$ (ETH, SOL, ZEC dans la jambe short, pas seulement des tokens « poubelle »). (b) Valeur du compte 3,9 M$ → 10,7 M$ (apports inclus), notionnel 35 M$ (~3,3×), réalisé 12 m −261 k$ : le gain est surtout latent et vient du funding. |
| Frais 2026 inclus ? | Oui : P&L on-chain net des frais Hyperliquid et du funding ; 10 % de commission du leader en plus pour un déposant. |
| Pour reproduire | Capital ≥ 5–10 k$ pour diversifier ≥ 10 shorts ; un compte Hyperliquid ; données d'émission et de déblocage (publiques) ; rééquilibrage quotidien ; aucune vitesse requise. |
| Pourquoi pas encore fermé | Non démontré. La jambe short a coïncidé avec un marché baissier des altcoins (2025-10 → 2026) ; aucun reçu ne montre un rendement neutre au marché. |
| Risque extrême caché | Squeeze sur un short de petite capitalisation (listing, rachat, rumeur) ; concentration sur HYPE (long 3,3 M$ pour 2,56 M$ de valeur de compte) ; ADL/liquidation sur Hyperliquid. |
| Venues / accès | Hyperliquid : pas de KYC, bloqué pour les US selon les CGU ; France/UE : accessible techniquement, cadre MiCA et fiscal à vérifier ; inconnu juridiquement. |
| Vérif 1 jour données publiques | Oui : rejouer 12 mois de fills et de funding par jambe (script de l'agent : `vaultDetails` + `userFillsByTime` + `userFunding`), puis régresser la jambe short sur un indice altcoin équipondéré. |
| Plafond petite taille | Inconnu. Sans preuve d'alpha, l'espérance de la jambe short au-delà du bêta est **~0 €/mois démontré**. |
| Confiance | reçu **vérifié** ; edge = **non vérifié** (gain dominé par le bêta HYPE et par la baisse des altcoins). Ne contredit PAS le rejet « short avant déblocage ». |
