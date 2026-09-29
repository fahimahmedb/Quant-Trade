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

---

## F3 — Marchés météo Polymarket (température max journalière par ville) : prévision d'ensemble vs prix des tranches

| Champ | Contenu |
|---|---|
| ID | F3 |
| Titre | Spécialistes « météo » Polymarket : acheter les tranches de température mal pricées vs prévisions d'ensemble et observations du jour |
| Type | information |
| Mécanisme : qui paie | Parieurs récréatifs sur des marchés journaliers « Highest temperature in <ville> on <date> » (tranches de 1–2 °). Ils pricent à l'intuition ; les prévisions d'ensemble (GFS 31 membres, ECMWF 51) et les observations METAR du jour sont publiques et gratuites. Ils ne s'arrêtent pas : nouveau marché chaque jour, dans des dizaines de villes. |
| RECETTE | Méthode publique générique : proba par tranche = part des membres d'ensemble (Open-Meteo) dans la tranche, trade si écart ≥ 8 % (ex. code https://github.com/suislanchez/polymarket-kalshi-weather-bot — **simulation seulement, aucun reçu**). Aucun gagnant n'a publié son code. Styles déduits du carnet d'ordres public (calcul de l'agent, 500 derniers trades) : 0x13f9… achète des queues (prix médian 0,02 $) ; 0x9c95… prix médian 0,21 $ ; Bilberry prix médian 0,40 $ ; HighTempTation ≥ 0,90 $ (favoris confirmés par l'observation du jour). |
| REÇU | Classement public par catégorie : `data-api.polymarket.com/v1/leaderboard?category=WEATHER&timePeriod=MONTH` ; portefeuilles : Bilberry `0xbf13934a1fec7d3211fc15c138d84ac2a691b91a`, `0x9c95da0c1ec3394330998296582c2739cfa752db`, `0x13f995ad154da3e078ac2a1dd923bf2b265dd352`, TunSahur `0x95d381e71dba6f1c3199fd9bc040383d6fae6eff`, HighTempTation `0x6011655c4afb76f36dd1b08a137a1ba73466b31e`, gopfan2 `0xf2f6af4f27ec2dcf4072095ab804016e14cd5817`. |
| Période / dernière date gagnante | API 2026-09-29 : top 50 météo sur 30 j = +427 k$ pour 15,6 M$ de volume (+2,7 %) ; sur 7 j +159 k$. Dernière date gagnante : semaine du 2026-09-22. |
| Ampleur | 30 j : Bilberry +46,7 k$ (volume 1,53 M$, valeur des positions 27,7 k$, 0 $ de rebate → preneur, paie les frais) ; 0x9c95 +30,8 k$ ; 0x13f9 +25,7 k$ ; HighTempTation +16,0 k$. Tout temps top 20 météo ≈ +2,2 M$ pour ~95 M$ de volume. **Persistance faible** : Bilberry actif depuis 2025-12-29 mais cumul tout temps (+43,1 k$) < 30 j (+46,7 k$), donc négatif avant ; 0x9c95 et 0x13f9 ont < 6 semaines. Parmi les 20 meilleurs tout temps, le dernier mois est mitigé (gopfan2 +10,8 k$, opopv +10,0 k$, Poligarch −32,3 k$, russell −2,0 k$, plusieurs ≈ 0). |
| Frais 2026 inclus ? | Oui : P&L Polymarket après frais preneur « weather » (taux 0,05 depuis le 2026-03-30 ; frais quasi nuls près de 0 ou 1). Les récompenses de liquidité et rebates sont faibles pour ces portefeuilles (0–1,3 k$/30 j), donc le gain vient bien du trading. |
| Pour reproduire | Capital 1–30 k$ (le capital tourne chaque jour) ; prévisions d'ensemble gratuites (Open-Meteo) + METAR/Weather Underground (source de résolution) ; automatisation 24 h/24 sur des dizaines de villes et fuseaux horaires ; latence : minutes, pas millisecondes. Colle bien à nos atouts (lecture, automatisation, petite taille). |
| Pourquoi pas encore fermé | Marchés petits et nombreux (profondeur de quelques k$ par tranche) → pas assez gros pour les fonds ; création quotidienne ; frais faibles aux extrêmes. Mais la concurrence de bots météo croît vite (nombreux bots publics depuis 2026). |
| Risque extrême caché | Biais du survivant : on ne voit que les gagnants (le classement ne liste pas les perdants). Risque de résolution : la station et l'arrondi de Weather Underground peuvent différer du modèle ; correction ou retard de données ; faible profondeur → le prix bouge contre soi. |
| Venues / accès | Polymarket international : US bloqué, **France bloquée (ANJ)** ; Kalshi (séries KXHIGH) : US, international à vérifier, France inconnu. |
| Vérif 1 jour données publiques | Oui : télécharger trades et résolutions des marchés météo des 60 derniers jours (data-api), prévisions archivées Open-Meteo (Previous Runs / Historical Forecast API), simuler la règle d'ensemble aux prix de l'époque avec les frais V2 ; en parallèle, P&L de TOUS les portefeuilles actifs (pas seulement le top) pour mesurer le biais du survivant. |
| Plafond petite taille | Estimation : **0–1 500 €/mois** (le 30ᵉ du top 50 fait ~5 k$/mois ; profondeur limitée ; edge non démontré hors top). |
| Confiance | **probable** que ces marchés paient des spécialistes après frais ; lien recette ↔ reçu **non vérifié** (aucun gagnant ne publie sa méthode). Sous-type « favoris ≥ 0,90 $ » (HighTempTation) : reçu récent, mais c'est une information d'observation, pas un biais des favoris ; le rejet « favoris > 90 ¢ » tient en général. |

---

## F4 — Subventions maker Polymarket : récompenses de liquidité + rebates maker (2026)

| Champ | Contenu |
|---|---|
| ID | F4 |
| Titre | Coter des deux côtés pour toucher les récompenses quotidiennes de liquidité et la part des frais preneur reversée aux makers |
| Type | maker |
| Mécanisme : qui paie | (1) Polymarket, via un budget de récompenses de liquidité (formule quadratique selon la distance au milieu, payée chaque jour à 00:00 UTC, minimum 1 $/jour) ; (2) les preneurs, via les frais V2 (depuis le 2026-03-30), dont 25 % sont reversés aux makers (20 % crypto, 15 % sports depuis juillet 2026). Les preneurs ne s'arrêtent pas (flux récréatif) ; Polymarket peut couper le budget à tout moment. |
| RECETTE | Règles officielles : https://docs.polymarket.com/market-makers/liquidity-rewards , https://help.polymarket.com/en/articles/13364471-maker-rebates-program . Code : https://github.com/warproxxx/poly-maker (réécrit 2026-07 pour CLOB V2 : classe les marchés politiques par « reward + rebate income vs volatility/spread risk », ordres post-only, coupe-circuit). Code d'origine : https://github.com/Polymarket/poly-market-maker . |
| REÇU | Chaque paiement est public : `data-api.polymarket.com/activity?user=<adresse>&type=REWARD` et `type=MAKER_REBATE`. Relevé de l'agent (30 j au 2026-09-29, 40 plus gros volumes du mois) : RN1 `0x2005d16a84ceefa912d4e380cd32e7ff827875ea` récompenses 43,9 k$ + rebates 166,6 k$ pour 183 M$ de volume ; `0xb27bc932bf8110d8f78e55da7d5f0497a18b5b82` 14,9 k$ + 117,0 k$ pour 29,4 M$ (0,45 % du volume) ; CrouchPrediction `0x21f4c1a1be34a39a7bc20985df4b7e5a39fb691d` 0 + 43,3 k$ pour 27,0 M$. Médiane du panel ≈ **0,10 % du volume** en subvention. Petite taille : @b00k13 (F1) = 5 $ de rebates sur 30 j. |
| Période / dernière date gagnante | Subventions payées chaque jour jusqu'au 2026-09-29 (vérifié). Le P&L net (subvention + trading) des makers n'est **pas** lisible de façon fiable : pour les gros portefeuilles, le P&L 30 j de `lb-api` est incohérent (ex. `0xfe787d…0319` : −58,6 M$ sur 30 j mais +1,19 M$ tout temps, avec 0,21 M$ de positions), probablement à cause de la comptabilité split/merge. |
| Ampleur | Subvention ≈ 0,05–0,45 % du volume maker. Pour 5 k$ de capital qui tournent ~40× par mois (200 k$ de volume), cela fait ~200 $/mois de subvention **avant** sélection adverse. |
| Frais 2026 inclus ? | Oui : les makers ne paient pas de frais ; les rebates existent précisément grâce aux frais 2026. |
| Pour reproduire | 2–20 k$ ; bot post-only (poly-maker V2) ; VPS ; latence de l'ordre de la seconde pour retirer les ordres sur nouvelle (le « heartbeat » du CLOB aide) ; choisir des marchés de niche à récompense élevée par dollar. |
| Pourquoi pas encore fermé | Il est fermé en grande partie pour le trading lui-même : l'auteur de poly-maker écrivait en janvier 2026 « In today's market, this bot is not profitable and will lose money… increased competition » (historique git du README). Les récompenses restent parce que Polymarket achète de la liquidité ; la subvention est partagée au prorata, donc diluée par chaque nouveau bot. |
| Risque extrême caché | Sélection adverse sur une nouvelle (le maker est pris juste avant un saut à 0 ou 1) ; changement unilatéral des barèmes (déjà modifiés en mars et en juillet 2026) ; risque de résolution UMA. |
| Venues / accès | Polymarket international : US bloqué, **France bloquée (ANJ)**. Polymarket US (CFTC) : autre carnet, autres règles. |
| Vérif 1 jour données publiques | Oui : pour 200 portefeuilles, sommer REWARD + MAKER_REBATE par jour, recalculer le P&L de trading à partir des TRADE/REDEEM/MERGE (sans passer par `lb-api`), en déduire la distribution de « subvention − sélection adverse » par taille de portefeuille. |
| Plafond petite taille | Subvention brute ~50–300 €/mois pour 5–10 k$ ; net après sélection adverse : **inconnu, probablement ≤ 0**. |
| Confiance | subventions **vérifiées** ; rentabilité nette à petite taille **non vérifiée** (seul témoignage direct : négatif). |
