# Ordre 13 — AGENT 1 « REGISTRES PUBLICS » — modèles économiques gagnants avec reçu

Date des mesures : 29/09/2026. Recherche externe uniquement : aucune stratégie codée, aucun ordre.
REAL_CAPITAL_AUTHORIZED = FALSE.

## Accès (mis à jour le 29/09/2026 après déclaration du propriétaire)

**Le propriétaire déclare avoir accès à Polymarket depuis sa localisation.** Les plafonds des fiches R1 à R3 sont donc exprimés sans la contrainte « France : 0 € » de la première version.
- Polymarket décide de l'accès selon la **localisation au moment de l'ordre**, pas selon la nationalité. Les ordres venant d'une zone restreinte sont rejetés.
- Pays en « close-only » selon la doc officielle : ouverture interdite, clôture seulement ([docs.polymarket.com/api-reference/geoblock](https://docs.polymarket.com/api-reference/geoblock)). La liste comprend notamment les États-Unis, la France, l'Allemagne, l'Italie, la Belgique, la Pologne et le Royaume-Uni. Pour la France, l'ANJ a en outre ordonné le blocage par les FAI le 16/07/2026 (source secondaire).
- Contrôle à faire depuis le poste réel avant tout usage : `GET https://polymarket.com/api/geoblock` doit répondre `blocked: false`. Ce contrôle n'a pas été fait ici : le conteneur de recherche n'est pas à la localisation du propriétaire.
- Passer par un VPN depuis une zone restreinte violerait les CGU et exposerait à un gel des fonds. Cette voie est exclue.

## Méthode et vérifications directes

Dans chaque fiche, les chiffres marqués (V) ont été obtenus par requête directe le 29/09/2026 :
1. (V) Hyperliquid, registre des vaults : `GET https://stats-data.hyperliquid.xyz/Mainnet/vaults` (9 476 vaults).
2. (V) Hyperliquid, classement public : `GET https://stats-data.hyperliquid.xyz/Mainnet/leaderboard` (46 863 comptes, fenêtres day/week/month/allTime).
3. (V) Frais Polymarket en production : `GET https://gamma-api.polymarket.com/markets?...`.
   - Le champ `feeSchedule` d'un marché sports actif donne `{rate: 0.05, rebateRate: 0.15, takerOnly: true}`.
   - Cela concorde avec la doc officielle : fee = C × rate × p × (1−p).
4. (V) Pool de récompenses Polymarket : `GET https://clob.polymarket.com/rewards/markets/current` (16 179 marchés).
5. (V) P&L par portefeuille Polymarket, via trois sources :
   - `GET https://user-pnl-api.polymarket.com/user-pnl?user_address=<addr>&interval=all&fidelity=1d` (série valorisée au prix de marché) ;
   - `GET https://data-api.polymarket.com/closed-positions?user=<addr>` (realizedPnl net de frais, champ `entryFeesUsdc`) ;
   - `GET https://data-api.polymarket.com/activity?user=<addr>&type=REWARD|MAKER_REBATE` (paiements on-chain avec hash de transaction).
6. (V) Classement Polymarket : `GET https://data-api.polymarket.com/v1/leaderboard?category=<CAT>&timePeriod=ALL&orderBy=VOL&limit=50&offset=0..1000`.
   - Trier par VOLUME et non par P&L donne 1 050 portefeuilles actifs, gagnants **et** perdants. C'est notre mesure du biais du survivant.

**Défaut constaté** : les P&L de fenêtre « MONTH » du classement Polymarket sont incohérents.
- Exemple : Lucerys `0x1387d145…55f8`, volume identique de 1,46 M$ : −731 796 $ en MONTH, −3 756 $ en ALL. Sur la même période, user-pnl affiche +522 k$.
- Ces fenêtres ne sont **pas** des reçus. Seuls ALL, user-pnl et closed-positions ont été utilisés.

Aucune identité n'a été recherchée derrière les adresses. Les pseudonymes cités sont ceux affichés par l'API publique.

---

## R1 — Météo Polymarket : trading informationnel sur prévisions publiques

| Champ | Contenu |
|---|---|
| ID | R1 PM-METEO |
| Titre | Tranches de température par ville et par jour sur Polymarket, tradées contre les prévisions numériques publiques |
| Type | information |
| Mécanisme : qui paie | Parieurs occasionnels qui fixent les tranches à l'intuition, et makers naïfs dont des gagnants ramassent les ordres. Les modèles publics (NWS/GFS, mises à jour toutes les 6 h) donnent une meilleure distribution que le prix affiché (explication secondaire : laikalabs, tradetheoutcome). **Rien ne force les payeurs à continuer** : c'est un flux récréatif renouvelé chaque jour par de nouveaux marchés, donc fragile. |
| REÇU | Séries user-pnl et closed-positions (requêtes 5 ci-dessus) pour 3 portefeuilles : `0x331bf91c132af9d921e1908ca0979363fc47193f` (BeefSlayer), `0x118689b24aead1d6e9507b8068d056b2ec4f051b` (russell110320) et `0x6011655c4afb76f36dd1b08a137a1ba73466b31e` (HighTempTation, premier point P&L le 06/03/2026). Classement : `leaderboard?category=WEATHER&timePeriod=ALL`. |
| Période couverte / dernière date gagnante | 29/09/2025 → 29/09/2026. Les 3 portefeuilles ont un mois gagnant en **septembre 2026** (V). |
| Ampleur | **Toutes catégories, user-pnl (V)** : +87 k$, +96 k$ et +93 k$ sur 12 mois ; +38 k$, +41 k$ et +93 k$ depuis le 30/03/2026 (entrée en vigueur des frais). **Météo seule, P&L réalisé borné à 1 500 positions par portefeuille (V)** : +56 k$ (tronqué), +49 k$ et +16 k$ (tronqué). **Positions perdantes non réclamées exclues** : faibles, −1,9 k$ et −1,7 k$ pour les deux premiers. Capital engagé : inconnu. Rendement : inconnu. |
| Frais 2026 inclus ? | **Oui.** Taker weather rate 0,05 × p(1−p) depuis le 30/03/2026 (Pine Analytics, doc officielle). Le realizedPnl de l'API est net de `entryFeesUsdc`, et les P&L post-30/03 restent positifs. Les makers paient 0 et touchent 25 % des frais en rebate. |
| Perdants du même modèle | **Top 1 050 par volume (ALL, V)** : 380 perdants, soit 36 % ; gains +6,47 M$ contre pertes −2,91 M$. **Échantillon systématique de 20 portefeuilles sur toute la plage de volume, météo 12 mois (V)** : 17 actifs, dont 4 perdants (24 %) ; P&L médian +264 $ ; quartile supérieur 4 k$ à 12 k$. **Longue traîne sous le top 1 050** : inconnu, probablement pire. **Les stars publiées déclinent (V)** : gopfan2 (+317 k$ ALL) ne fait que +495 $ depuis avril 2026 ; aenews2 (+285 k$ ALL) −31 $ ; ColdMath (+134 k$ ALL) +155 $ sur 12 mois, sur 2 positions. |
| Dépend de la vitesse ? | Modérément. Il faut réagir aux runs de modèles, pas à la milliseconde. En revanche, la concurrence de bots est publique depuis 2026 (guides et « skills » de bots météo). |
| Capital minimum | Faible techniquement (quelques dizaines de $). La profondeur par marché est limitée ; capacité exacte inconnue. |
| Risque extrême caché | Règle de résolution sur une station précise (Weather Underground, arrondis) ; litige UMA ; erreur de donnée de station ; corrélation (un même front touche plusieurs villes) ; décroissance rapide par publicité ; risque juridique ou de compte en pays restreint. |
| Venues et accès | Polymarket international. **Accessible pour le propriétaire (déclaratif ; à confirmer par `/api/geoblock`).** Close-only notamment aux US, en France, en Allemagne, en Italie, en Belgique, en Pologne et au Royaume-Uni. |
| Vérification possible en 1 jour | **Oui** pour les reçus (API publiques, calcul reproduit ici). Un backtest avec archives de prévisions publiques n'est pas vérifié ici. |
| Plafond estimé à petite taille | Ordre de grandeur déduit de l'échantillon : médiane ≈ 20 $/mois, quartile supérieur ≈ 300 à 1 000 $/mois, meilleurs ≈ 6 à 15 k$/mois après frais. Non démontré pour nous. |
| Confiance | **Vérifié** pour l'existence d'un reçu récent après frais ; **probable** pour la survie de l'edge (décroissance visible chez les pionniers). |

## R2 — Récompenses de liquidité et rebates makers sur la longue traîne Polymarket

| Champ | Contenu |
|---|---|
| ID | R2 PM-MAKER-RECOMPENSES |
| Titre | Coter des deux côtés dans des marchés peu disputés pour capter la subvention de liquidité quotidienne et les rebates |
| Type | maker (subvention) |
| Mécanisme : qui paie | (1) La plateforme, qui subventionne la liquidité : 129 514 $/jour (V). (2) Les takers, via 15 à 25 % des frais redistribués aux makers. **La plateforme peut arrêter à tout moment** : la subvention est discrétionnaire ; par exemple, le programme crypto TWAP d'août 2026 est terminé (doc officielle). |
| REÇU | Pool : `clob.polymarket.com/rewards/markets/current` (V). 16 179 marchés, médiane 2 $/jour par marché, taille minimale 20 à 200 parts, spread maximal 2,5 à 6,5 ¢. Jeton de récompense `0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB` (nature non vérifiée). Paiements individuels on-chain : `data-api.polymarket.com/activity?type=REWARD` et `type=MAKER_REBATE`. Exemple : `0x204f72f35326db932158cba6adff0b9a1da95e14` (swisstony) a reçu **240 paiements REWARD pour 111 255 $ sur 12 mois (V)**, observés au moins jusqu'au 24/08/2026 ; 177 paiements MAKER_REBATE observés au moins du 26/02 au 27/08/2026 (somme non calculée). |
| Période couverte / dernière date gagnante | Pool : instantané du 29/09/2026. Paiements individuels : au moins jusqu'au 27/08/2026 pour un seul portefeuille. |
| Ampleur | Pool ≈ 3,9 M$/30 jours (V). **Instantané de 246 marchés tirés au hasard (V, calcul modèle)** : 82 n'ont aucune cotation qualifiante. Dans les 131 marchés à carnet serré (≤ 5 ¢), un ordre marginal de 100 $/côté à 1 ¢ du mid capterait **≈ 0,82 $/jour médian (brut ≈ 150 %/an sur 200 $)**. Ce calcul est statique, fait avant sélection adverse et avant perte d'inventaire. **Ce n'est pas un reçu.** |
| Frais 2026 inclus ? | Oui : makers à 0 frais, rebate compris. La sélection adverse n'est pas mesurée. |
| Perdants du même modèle | **Inconnu.** L'échantillonnage REWARD/MAKER_REBATE et P&L sur 1 159 portefeuilles a été arrêté à environ 200 portefeuilles, sans résultat exploitable. Solidus (source secondaire, politique, déc. 2025 à fév. 2026) : 0,55 % des makers gagnants captent 50 % des gains (≈ 8 M$ sur 16 M$). La part des makers perdants n'est pas publiée. |
| Dépend de la vitesse ? | Moyennement. Il faut retirer les cotes avant une nouvelle, un run météo ou la résolution. Sinon les traders informés de R1 ramassent les ordres. |
| Capital minimum | ≈ 10 à 200 $ par marché (taille minimale qualifiante). Une diversification sur 50 marchés demande ≈ 10 k$. |
| Risque extrême caché | Sélection adverse par des traders informés (météo, « Trump dira X ») ; perte binaire d'inventaire à la résolution ; subvention réduite ou supprimée ; marchés périmés encore récompensés ; lavage de volume (≈ 15 % du volume de certains marchés selon Solidus). |
| Venues et accès | Identiques à R1 (accessible pour le propriétaire, déclaratif). |
| Vérification possible en 1 jour | Partielle. Les récompenses et rebates par portefeuille sont publics. Le P&L net « maker seulement » demande le flag maker/taker au niveau des fills (subgraph) : plus d'un jour probablement. |
| Plafond estimé à petite taille | Borne haute brute théorique ≈ 50 marchés × 0,8 $/jour ≈ 1 200 $/mois, avant sélection adverse. Net inconnu. |
| Confiance | Pool **vérifié** ; rentabilité nette à petite taille **non vérifiée**. |

## R3 — Tenue de marché sports Polymarket à grande échelle

| Champ | Contenu |
|---|---|
| ID | R3 PM-SPORTS-MM |
| Titre | Makers sports à volume milliardaire (spread, rebates 15 %, récompenses) |
| Type | maker |
| Mécanisme : qui paie | Les parieurs sportifs takers paient le spread et 0,05 × p(1−p) de frais. Ils ne s'arrêtent pas : le volume sports est passé de 100–150 M$/jour à 150–250 M$/jour après l'introduction des frais le 18/02/2026 (Pine Analytics, secondaire). |
| REÇU | `leaderboard?category=SPORTS&timePeriod=ALL` (V) : `0x204f72f3…9e14` +18,42 M$ pour 1,85 Md$ de volume (≈ 1,0 %) ; `0x2005d16a…75ea` +11,93 M$ pour 1,21 Md$ (≈ 1,0 %). Activité maker prouvée pour le premier : REWARD 111 k$ sur 12 mois et MAKER_REBATE (V). |
| Période couverte / dernière date gagnante | P&L ALL (historique complet). **P&L sur 12 mois : inconnu** (non calculé ; fenêtre MONTH inutilisable). Paiements maker jusqu'au 27/08/2026. |
| Ampleur | Top 1 050 par volume (ALL, V) : gains +411,6 M$, pertes −328,0 M$, net +83,6 M$ pour 50,4 Md$ de volume (+0,17 %/$). |
| Frais 2026 inclus ? | Makers : 0 frais et 15 % de rebate. P&L après 18/02/2026 non isolé : inconnu. |
| Perdants du même modèle | Top 1 050 par volume sports (ALL, V) : 434 perdants, soit 42 %. La part propre aux makers est inconnue. |
| Dépend de la vitesse ? | **Oui** : live, retrait des cotes avant but ou point, flux de données sportives. |
| Capital minimum | Millions de $ (inféré des volumes). Inconnu précisément. |
| Risque extrême caché | Snipe en direct par des joueurs à information plus rapide (courtsiders) ; erreurs de résolution ; événements annulés. |
| Venues et accès | Comme R1 (accessible pour le propriétaire, déclaratif). La réglementation locale des paris sportifs est à vérifier selon la localisation : inconnu. |
| Vérification possible en 1 jour | P&L 12 mois par user-pnl : oui. Part maker du P&L : non. |
| Plafond estimé à petite taille | ≈ 0 € (vitesse et capital hors de portée). |
| Confiance | **Probable** (reçu ALL vérifié, récence 12 mois non vérifiée). |

## R4 — Tenue de marché perps Hyperliquid

| Champ | Contenu |
|---|---|
| ID | R4 HL-MM |
| Titre | Market makers perps (flux retail à levier, liquidations) |
| Type | maker |
| Mécanisme : qui paie | Les takers à levier paient le spread et 0,045 % de frais au tier 0. Ils continuent parce qu'ils veulent du levier immédiat, et les liquidations sont forcées. |
| REÇU | `stats-data.hyperliquid.xyz/Mainnet/leaderboard` (V). Heuristique maker : volume all-time > 1 Md$ et abs(pnl)/volume < 2 pb. **198 comptes**. Exemples : `0x162cc7c861ebd0c06b3d72319201150482518185` (722 Md$, +42,8 M$, 0,59 pb/$) ; `0x87f9cd15f5050a9283b8896300f7c8cf69ece2cf` (599 Md$, +45,2 M$, 0,75 pb/$, mais −16,5 M$ sur le mois) ; `0x023a3d058020fb76cca98f01b3c48c8938a22355` (243 Md$, +46,9 M$, 1,93 pb/$, −13,4 M$ sur le mois). |
| Période couverte / dernière date gagnante | Historique complet et fenêtre « month » au 29/09/2026 (V). |
| Ampleur | Les 198 comptes totalisent +295,5 M$. Marge nette 0,18 à 1,93 pb par $ échangé pour les 8 plus gros (V). |
| Frais 2026 inclus ? | Oui (P&L net de frais). **Grille officielle** : maker 0,015 % (1,5 pb) au tier 0, 0 % au-delà de 500 M$/14 jours, rebate −0,1 à −0,3 pb seulement au-delà de 0,5 % de part maker. **Un petit maker paie 1,5 pb, soit autant ou plus que toute la marge nette des MM établis.** |
| Perdants du même modèle | All-time : 94/198 perdants (47,5 %). **Mois : 61/108 actifs perdants (56,5 %)** (V). |
| Dépend de la vitesse ? | **Oui** (latence en millisecondes, co-location). |
| Capital minimum | Dizaines de M$ (inféré). |
| Risque extrême caché | Cascades de liquidation, ADL, manipulation d'actifs peu liquides (cas connu JELLY, mars 2025) ; inventaire lors d'un gap. |
| Venues et accès | Hyperliquid : front-end bloqué pour les US. France : accès technique sans KYC ; statut réglementaire **inconnu / non vérifié**. |
| Vérification possible en 1 jour | Oui (endpoint public, calcul reproduit ici). |
| Plafond estimé à petite taille | **≤ 0 €/mois** (frais tier 0 > marge des MM établis). |
| Confiance | **Vérifié**. Caveats : l'identification maker est heuristique, et le P&L all-time peut inclure spot/airdrop. |

## R5 — Arbitrage de cohérence Polymarket (somme des issues ≠ 1 $)

| Champ | Contenu |
|---|---|
| ID | R5 PM-ARB |
| Titre | Rééquilibrage NegRisk, arbitrage intra-condition et arbitrage combinatoire |
| Type | arbitrage |
| Mécanisme : qui paie | Les traders qui déplacent une issue sans réajuster les autres. Ils peuvent arrêter : le flux dépend de l'inattention. |
| REÇU | Saguillo, Ghafouri, Kiffer, Suarez-Tangil, *Unravelling the Probabilistic Forest*, AFT 2025, [arXiv 2508.03474](https://arxiv.org/abs/2508.03474). Tables établies sur les données on-chain du carnet d'ordres. |
| Période couverte / dernière date gagnante | 01/04/2024 → 01/04/2025. **Aucun reçu après avril 2025.** |
| Ampleur | ≈ 40 M$ réalisés : NegRisk 28,9 M$, intra-condition 10,6 M$, combinatoire 95 k$. Meilleure adresse : 2,01 M$ sur 4 049 transactions. Les 10 premières adresses captent l'essentiel. |
| Frais 2026 inclus ? | **Non** : l'étude précise qu'il n'y avait aucun frais par trade à l'époque. Déduction depuis la formule officielle : un panier NegRisk de N issues coûte en taker ≈ rate × (1 − Σp²) par panier de 1 $, soit ≈ 4,5 ¢ pour 10 issues uniformes à rate 0,05. Cela efface la plupart des écarts. |
| Perdants du même modèle | Inconnu (l'étude mesure les profits réalisés, pas les tentatives perdantes). |
| Dépend de la vitesse ? | **Oui** (compétition de bots, fenêtres courtes). |
| Capital minimum | Faible par opportunité ; inconnu en pratique. |
| Risque extrême caché | Jambes non exécutées ; résolutions incohérentes entre marchés liés ; litige UMA. |
| Venues et accès | Comme R1 (accessible pour le propriétaire, déclaratif). |
| Vérification possible en 1 jour | Oui pour l'existence d'écarts actuels (carnets publics). Rentabilité nette de frais : non. |
| Plafond estimé à petite taille | ≈ 0 € en taker après frais 2026 (inféré). Inconnu en maker. |
| Confiance | **Vérifié historiquement, non récent.** Échoue au critère 2 du reçu. |

## R6 — Stratégies déléguées : vaults utilisateurs Hyperliquid (contrôle du survivant)

| Champ | Contenu |
|---|---|
| ID | R6 HL-VAULTS |
| Titre | Déposer chez un « leader » de vault (famille copy-trading, déjà rejetée) |
| Type | autre (délégation) |
| Mécanisme : qui paie | Aucun payeur structurel. Le P&L vient des trades directionnels du leader ; les déposants paient 10 % de commission de performance. |
| REÇU | `stats-data.hyperliquid.xyz/Mainnet/vaults` (V). |
| Période couverte / dernière date gagnante | Historique complet et fenêtre « month » au 29/09/2026 (V). |
| Ampleur | Vaults utilisateurs (hors famille HLP) avec P&L non nul : **8 029**. **Gains +62,2 M$ contre pertes −123,5 M$, net −61,3 M$ (V).** |
| Frais 2026 inclus ? | Oui (P&L des vaults net de frais de trading ; commission de 10 % en plus pour le déposant). |
| Perdants du même modèle | **73,2 % perdants** (2 153 gagnants sur 8 029). Vaults fermés : 1 530/5 186 gagnants. Vaults ouverts : 623/2 843. Survivants ouverts avec TVL ≥ 100 k$ et âge ≥ 1 an : 38/46 gagnants all-time, mais seulement 27/46 sur le mois. **Biais du survivant manifeste.** |
| Dépend de la vitesse ? | Non. |
| Capital minimum | Faible. |
| Risque extrême caché | Drawdown brutal du leader ; retraits bloqués selon les règles du vault ; P&L affiché sélectionné a posteriori. |
| Venues et accès | Comme R4. |
| Vérification possible en 1 jour | Oui (fait ici). |
| Plafond estimé à petite taille | Espérance négative sur l'univers. **Rejet copy-trading confirmé.** |
| Confiance | **Vérifié.** |

---

## Négatifs utiles

1. **Vaults utilisateurs Hyperliquid** : 26,8 % gagnants, net −61 M$ (V). Déléguer ou copier reste mort ; le rejet copy-trading est confirmé.
2. **Petit maker Hyperliquid** : frais maker tier 0 de 1,5 pb, au moins égaux à la marge nette totale des MM établis (0,2 à 1,9 pb/$), et 56 % d'entre eux perdent sur le mois (V). Mort à petite taille.
3. **Arbitrage de cohérence Polymarket en taker** : le seul reçu (≈ 40 M$) date de 2024–25, sans frais. Les frais 2026, rate × p(1−p) par jambe, l'effacent (inféré de la formule officielle).
4. **Classements et célébrités** : les P&L MONTH du classement Polymarket sont faux (V). Les stars météo publiées (gopfan2, aenews2, ColdMath) ne gagnent presque plus depuis avril 2026 (V) : la notoriété précède la décroissance.
5. **LP passif Uniswap v3** : LVR supérieur aux frais sur les plus grands pools ([arXiv 2404.05803](https://arxiv.org/html/2404.05803v2)) ; environ la moitié des positions sont perdantes (source secondaire, non vérifié directement).
